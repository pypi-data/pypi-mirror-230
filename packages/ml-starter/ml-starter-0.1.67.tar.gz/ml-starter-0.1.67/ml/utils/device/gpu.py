"""GPU device type.

The default floating point type can be configured with the environment
variables:

- ``USE_FP64``: Use FP64
- ``USE_FP32``: Use FP32
- ``USE_BF16``: Use BF16
"""

import functools
import logging
import os
from typing import Callable

import torch

from ml.core.env import is_gpu_disabled
from ml.utils.device.base import base_device

logger: logging.Logger = logging.getLogger(__name__)


def get_env_bool(key: str) -> bool:
    val = int(os.environ.get(key, 0))
    assert val in (0, 1), f"Invalid value for {key}: {val}"
    return val == 1


class gpu_device(base_device):  # noqa: N801
    """Mixin to support single-GPU training."""

    @classmethod
    def has_device(cls) -> bool:
        return torch.cuda.is_available() and torch.cuda.device_count() > 0 and not is_gpu_disabled()

    @functools.lru_cache(maxsize=None)
    def _get_device(self) -> torch.device:
        return torch.device("cuda")

    @functools.lru_cache(maxsize=None)
    def _get_floating_point_type(self) -> torch.dtype:
        # Allows users to override the default floating point type.
        if get_env_bool("USE_FP64"):
            return torch.float64
        elif get_env_bool("USE_FP32"):
            return torch.float32
        elif get_env_bool("USE_BF16"):
            return torch.bfloat16
        elif get_env_bool("USE_FP16"):
            return torch.float16

        # By default, use BF16 if the GPU supports it, otherwise FP16.
        if torch.cuda.get_device_capability()[0] >= 8:
            return torch.bfloat16
        return torch.float16

    def get_torch_compile_backend(self) -> str | Callable:
        capability = torch.cuda.get_device_capability()
        if capability >= (7, 0):
            return "inductor"
        return "aot_ts_nvfuser"

    def supports_grad_scaler(self) -> bool:
        return self._get_floating_point_type() not in (torch.float32, torch.float64)
