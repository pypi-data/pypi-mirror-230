"""
"""
# pyright: reportPrivateImportUsage=false

from __future__ import annotations

import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from typing import TYPE_CHECKING
from typing import Tuple

if TYPE_CHECKING:
    import torch as Torch

try:
    # TODO: Do not import torch on non-ZeroGPU environments
    import torch
except ImportError:
    torch = None


if torch is not None:

    _tensor_to      = torch.Tensor.to
    _tensor_cuda    = torch.Tensor.cuda
    _cuda_init      = torch._C._cuda_init
    _cuda_available = torch.cuda.is_available

    TensorToArgs = Tuple[torch.device, torch.dtype, bool, torch.memory_format]

    to_ops: list[tuple[Torch.Tensor, TensorToArgs]] = []
    cuda_ops: list[Torch.Tensor] = []

    def _to_op_register(self: Torch.Tensor, *args, **kwargs):
        parsed = torch._C._nn._parse_to(*args, **kwargs)
        device, *_ = parsed
        if not isinstance(device, torch.device):
            return _tensor_to(self, *args, **kwargs)
        if device.type != 'cuda':
            return _tensor_to(self, *args, **kwargs)
        to_ops.append((self, parsed))
        return self

    def _cuda_op_arg_check(device: Torch.device | int | str | None) -> bool:
        if device is None:
            return True
        if isinstance(device, int):
            return True
        if isinstance(device, str):
            device = torch.device(device)
        return device.type == 'cuda'

    def _cuda_op_register(self: Torch.Tensor, device: Torch.device | int | str | None = None, **kwargs):
        if not _cuda_op_arg_check(device):
            # Let PyTorch handle the fail
            return _tensor_cuda(self, device, **kwargs)
        cuda_ops.append(self)
        return self

    def _cuda_init_raise():
        raise RuntimeError(
            "CUDA must not be initialized in the main process "
            "on Spaces with Stateless GPU environment.\n"
            "You can look at this Stacktrace to find out "
            "which part of your code triggered a CUDA init"
        )

    def _patch():
        torch.Tensor.to         = _to_op_register   # type: ignore
        torch.Tensor.cuda       = _cuda_op_register # type: ignore
        torch._C._cuda_init     = _cuda_init_raise
        torch.cuda.is_available = lambda: True

    def _unpatch():
        torch.Tensor.to         = _tensor_to
        torch.Tensor.cuda       = _tensor_cuda
        torch._C._cuda_init     = _cuda_init
        torch.cuda.is_available = _cuda_available

    def _move(nvidia_uuid: str):
        os.environ['CUDA_VISIBLE_DEVICES'] = nvidia_uuid
        for op in to_ops:
            tensor, parsed_args = op
            _, dtype, _, memory_format = parsed_args
            tensor.data = _tensor_to(tensor,
                device='cuda',
                dtype=dtype,
                memory_format=memory_format,
            ) # type: ignore
        for op in cuda_ops:
            tensor = op
            tensor.data = _tensor_cuda(tensor)
        torch.cuda.init()

    def _is_in_bad_fork():
        with ProcessPoolExecutor(mp_context=multiprocessing.get_context('fork')) as e:
            f = e.submit(torch.cuda._is_in_bad_fork)
            return f.result()

    def _disable_cuda_intercept():
        torch.Tensor.to   = _tensor_to
        torch.Tensor.cuda = _tensor_cuda

else:

    _patch = lambda: None
    _unpatch = lambda: None
    _move = lambda nvidia_uuid: None
    _is_in_bad_fork = lambda: False
    _disable_cuda_intercept = lambda: None


patch = _patch
unpatch = _unpatch
move = _move
is_in_bad_fork = _is_in_bad_fork
disable_cuda_intercept = _disable_cuda_intercept
