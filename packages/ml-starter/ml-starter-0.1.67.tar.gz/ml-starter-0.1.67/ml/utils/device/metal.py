"""MPS device support for Metal GPUs (i.e., Apple Silicon)."""

import os
from typing import Callable

import torch

from ml.core.env import is_metal_disabled
from ml.utils.device.base import base_device


def get_env_bool(key: str) -> bool:
    val = int(os.environ.get(key, 0))
    assert val in (0, 1), f"Invalid value for {key}: {val}"
    return val == 1


class metal_device(base_device):  # noqa: N801
    """Mixin to support Metal training."""

    @classmethod
    def has_device(cls) -> bool:
        # Use the DISABLE_METAL environment variable if MPS has issues, since
        # it is still in the very early days of support.
        return torch.backends.mps.is_available() and not is_metal_disabled()

    def _get_device(self) -> torch.device:
        return torch.device("mps", 0)

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

        return torch.float32

    def get_torch_compile_backend(self) -> str | Callable:
        return "aot_ts"
