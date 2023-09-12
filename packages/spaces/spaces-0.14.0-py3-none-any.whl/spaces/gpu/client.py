"""
"""
from __future__ import annotations

import time
import warnings
from dataclasses import asdict
from dataclasses import dataclass
from datetime import timedelta
from http import HTTPStatus

import gradio as gr
import requests

from .. import utils
from ..config import Config


TOKEN_HEADER = 'X-IP-Token'
UNUSED_MESSAGE = "GPU device not used"


@dataclass
class ScheduleParams:
    cgroupPath: str
    taskId: int
    token: str | None
    durationSeconds: int | None

@dataclass
class ScheduleResponse:
    idle: bool
    nvidiaIndex: int
    nvidiaUUID: str

@dataclass
class ReleaseParams:
    cgroupPath: str
    taskId: int
    nvidiaIndex: int
    fail: bool


def base_url() -> str:
    assert Config.zero_device_api_url is not None
    return Config.zero_device_api_url

def post(path: str, params: dict | None = None) -> requests.Response:
    return requests.post(base_url() + path, params=params if params else None)


def startup_report():
    retries, max_retries = 0, 2
    while (status := post('/startup-report').status_code) == HTTPStatus.NOT_FOUND: # pragma: no cover
        time.sleep(1)
        if (retries := retries + 1) > max_retries:
            raise RuntimeError("Error while initializing ZeroGPU: NotFound")
    if status != HTTPStatus.OK: # pragma: no cover
        raise RuntimeError("Error while initializing ZeroGPU: Unknown")


def schedule(
    task_id: int,
    request: gr.Request | None,
    duration: timedelta | None,
) -> ScheduleResponse:

    res = post('/schedule', params=asdict(ScheduleParams(
        cgroupPath=utils.self_cgroup_device_path(),
        taskId=task_id,
        token=_get_token(request),
        durationSeconds=duration.seconds if duration is not None else None,
    )))

    if res.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        raise gr.Error("You have exceeded your GPU quota") # pragma: no cover

    if res.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
        raise gr.Error("No GPU is currently available")

    try:
        data = res.json()
    except requests.JSONDecodeError: # pragma: no cover
        data = {}

    if not res.ok: # pragma: no cover
        raise RuntimeError(f"ZeroGPU API /schedule error: {data.get('detail')}")

    return ScheduleResponse(**data)


def release(
    task_id: int,
    nvidia_index: int,
    fail: bool = False,
) -> None:

    res = post('/release', params=asdict(ReleaseParams(
        cgroupPath=utils.self_cgroup_device_path(),
        taskId=task_id,
        nvidiaIndex=nvidia_index,
        fail=fail,
    )))

    if res.status_code == HTTPStatus.NO_CONTENT: # pragma: no cover
        try:
            gr.Warning(UNUSED_MESSAGE)
        except AttributeError:
            pass
        warnings.warn(UNUSED_MESSAGE, RuntimeWarning)
        return None

    if not res.ok:
        try:
            data = res.json()
        except requests.JSONDecodeError: # pragma: no cover
            data = {}
        raise RuntimeError(f"ZeroGPU API /release error: {data.get('detail')}")

    return None


def _get_token(request: gr.Request | None) -> str | None:

    if request is None:
        return None

    headers = getattr(request, 'headers', None)
    if headers is None or not hasattr(headers, '__dict__'):
        raise gr.Error("Internal Gradio error")

    # Compatibility trick
    if not hasattr(headers, 'get'):
        headers = headers.__dict__ # pragma: no cover

    if not (token := headers.get(TOKEN_HEADER.lower())):
        raise gr.Error("Internal infra error")

    return token
