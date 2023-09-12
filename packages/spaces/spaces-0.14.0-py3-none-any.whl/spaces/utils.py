"""
"""
from __future__ import annotations

import sys
from functools import lru_cache as cache

import multiprocessing
from multiprocessing.queues import SimpleQueue as _SimpleQueue
from pathlib import Path
from pickle import PicklingError
from typing import Callable
from typing import TypeVar


T = TypeVar('T')


@cache
def self_cgroup_device_path() -> str:
    cgroup_content = Path('/proc/self/cgroup').read_text()
    for line in cgroup_content.strip().split('\n'):
        contents = line.split(':devices:')
        if len(contents) != 2:
            continue # pragma: no cover
        return contents[1]
    raise Exception # pragma: no cover


if sys.version_info.minor < 9: # pragma: no cover
    _SimpleQueue.__class_getitem__ = classmethod(lambda cls, _: cls) # type: ignore

class SimpleQueue(_SimpleQueue[T]):
    def __init__(self, *args):
        super().__init__(*args, ctx=multiprocessing.get_context('fork'))
    def put(self, element: T):
        try:
            super().put(element)
        except PicklingError:
            raise # pragma: no cover
        # https://bugs.python.org/issue29187
        except Exception as e:
            message = str(e)
            if not "pickle" in message:
                raise # pragma: no cover
            raise PicklingError(message)
    def close(self): # Python 3.8 static typing trick
        super().close() # type: ignore


def drop_params(fn: Callable[[], T]) -> Callable[..., T]:
    def drop(*args):
        return fn()
    return drop


def boolean(value: str | None) -> bool:
    return value is not None and value.lower() in ("1", "t", "true")
