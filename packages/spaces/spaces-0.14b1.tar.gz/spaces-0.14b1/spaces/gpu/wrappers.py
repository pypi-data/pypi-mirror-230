"""
"""
from __future__ import annotations

import multiprocessing
import inspect
import os
import signal
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from functools import partial
from inspect import Parameter
from pickle import PicklingError
from threading import Thread
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import Callable
from typing import Generator
from typing import Generic
from typing import Tuple
from typing import TypeVar
from typing_extensions import Concatenate
from typing_extensions import ParamSpec

import gradio as gr
import psutil

from ..utils import drop_params
from ..utils import SimpleQueue as Queue
from . import client
from . import torch


Process = multiprocessing.get_context('fork').Process

Arg = Tuple[Tuple[Any], Dict[str, Any]]
Res = TypeVar('Res')
Param = ParamSpec('Param')
NvidiaIndex = int
NvidiaUUID = str


class Worker(Generic[Res]):
    process: Process
    arg_queue: Queue[Arg]
    res_queue: Queue[Res]
    _sentinel: Thread

    def __init__(
        self,
        target: Callable[[Queue[Arg], Queue[Res], NvidiaUUID, list[int]], None],
        nvidia_uuid: str,
    ):
        self._sentinel = Thread(target=self._close_on_exit)
        self.arg_queue = Queue()
        self.res_queue = Queue()
        fds = [c.fd for c in psutil.Process().connections()]
        args = self.arg_queue, self.res_queue, nvidia_uuid, fds
        if TYPE_CHECKING:
            target(*args)
        self.process = Process(
            target=target,
            args=args,
            daemon=True,
        )
        self.process.start()
        self._sentinel.start()

    def _close_on_exit(self):
        self.process.join()
        self.res_queue.close()


def regular_function_wrapper(
    task: Callable[Param, Res],
    duration: timedelta | None,
) -> Callable[Concatenate[gr.Request, Param], Res]:

    workers: dict[NvidiaIndex, Worker[list[Res] | Exception]] = {}
    task_id = id(task)

    def gradio_handler(request: gr.Request, /, *args: Param.args, **kwargs: Param.kwargs) -> Res:

        schedule_response = client.schedule(task_id, request, duration)
        nvidia_index = schedule_response.nvidiaIndex
        nvidia_uuid = schedule_response.nvidiaUUID
        release = partial(client.release, task_id=task_id, nvidia_index=nvidia_index)

        worker = workers.get(nvidia_index)
        if worker is None or not worker.process.is_alive():
            worker = Worker(thread_wrapper, nvidia_uuid)
            workers[nvidia_index] = worker

        try:
            worker.arg_queue.put((args, kwargs))
        except PicklingError:
            release(fail=True)
            raise

        try:
            res = worker.res_queue.get()
        except EOFError:
            release(fail=True)
            raise gr.Error("GPU task aborted")
        if isinstance(res, Exception):
            release(fail=True)
            raise res
        release()
        return res[0]


    def thread_wrapper(
        arg_queue: Queue[Arg],
        res_queue: Queue[list[Res] | Exception],
        nvidia_uuid: str,
        fds: list[int],
    ):
        torch.unpatch()
        torch.move(nvidia_uuid)
        for fd in fds:
            os.close(fd)
        signal.signal(signal.SIGTERM, drop_params(arg_queue.close))
        while True:
            try:
                args, kwargs = arg_queue.get()
            except OSError:
                break
            with ThreadPoolExecutor() as executor:
                future = executor.submit(task, *args, **kwargs) # type: ignore
            try:
                res = [future.result()]
            except Exception as e:
                traceback.print_exc()
                res = e
            try:
                res_queue.put(res)
            except PicklingError as e:
                res_queue.put(e)
    
    update_handler_meta(gradio_handler, inspect.signature(task))

    return gradio_handler


def generator_function_wrapper(
    task: Callable[Param, Generator[Res, None, None]],
    duration: timedelta | None,
) -> Callable[Concatenate[gr.Request, Param], Generator[Res, None, None]]:

    workers: dict[NvidiaIndex, Worker[list[Res] | Exception | None]] = {}
    task_id = id(task)

    def gradio_handler(request: gr.Request, /, *args: Param.args, **kwargs: Param.kwargs) -> Generator[Res, None, None]:

        schedule_response = client.schedule(task_id, request, duration)
        nvidia_index = schedule_response.nvidiaIndex
        nvidia_uuid = schedule_response.nvidiaUUID
        release = partial(client.release, task_id=task_id, nvidia_index=nvidia_index)

        worker = workers.get(nvidia_index)
        if worker is None or not worker.process.is_alive():
            worker = Worker(thread_wrapper, nvidia_uuid)
            workers[nvidia_index] = worker

        try:
            worker.arg_queue.put((args, kwargs))
        except PicklingError:
            release(fail=True)
            raise

        yield_queue: Queue[list[Res] | Exception | None] = Queue()
        def fill_yield_queue(worker: Worker[list[Res] | Exception | None]):
            while True:
                try:
                    res = worker.res_queue.get()
                except Exception:
                    release(fail=True)
                    yield_queue.close()
                    return
                if isinstance(res, Exception):
                    release(fail=True)
                    yield_queue.put(res)
                    return
                if res is None:
                    release()
                    yield_queue.put(None)
                    return
                yield_queue.put(res)

        with ThreadPoolExecutor() as e:
            e.submit(fill_yield_queue, worker)
            while True:
                try:
                    res = yield_queue.get()
                except Exception:
                    raise gr.Error("GPU task aborted")
                if isinstance(res, Exception):
                    raise res
                if res is None:
                    break
                yield res[0]


    def thread_wrapper(
        arg_queue: Queue[Arg],
        res_queue: Queue[list[Res] | Exception | None],
        nvidia_uuid: str,
        fds: list[int],
    ):
        torch.unpatch()
        torch.move(nvidia_uuid)
        for fd in fds:
            os.close(fd)
        signal.signal(signal.SIGTERM, drop_params(arg_queue.close))
        while True:
            try:
                args, kwargs = arg_queue.get()
            except OSError:
                break
            def iterate():
                gen = task(*args, **kwargs) # type: ignore
                while True:
                    try:
                        res = next(gen)
                    except StopIteration:
                        break
                    except Exception as e:
                        res_queue.put(e)
                        break
                    try:
                        res_queue.put([res])
                    except PicklingError as e:
                        res_queue.put(e)
                        break
                    else:
                        continue
            with ThreadPoolExecutor() as executor:
                executor.submit(iterate)
            res_queue.put(None)

    update_handler_meta(gradio_handler, inspect.signature(task))

    return gradio_handler


def update_handler_meta(handler: Callable, task_signature: inspect.Signature):
    param_name = f'request_{uuid.uuid4().hex}'
    new_param = Parameter(param_name, Parameter.POSITIONAL_ONLY, annotation=gr.Request)
    new_params = [new_param] + list(task_signature.parameters.values())
    handler.__signature__ = task_signature.replace(parameters=new_params)
    handler.__annotations__.update({param_name: gr.Request})
