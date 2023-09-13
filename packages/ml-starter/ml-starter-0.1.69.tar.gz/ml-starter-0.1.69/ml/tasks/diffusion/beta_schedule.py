"""Implements various beta schedules for diffusion models."""

import math
from typing import Literal, cast, get_args

import torch
from torch import Tensor

DiffusionBetaSchedule = Literal["linear", "quad", "warmup", "const", "cosine", "jsd"]


def _warmup_beta_schedule(
    beta_start: float,
    beta_end: float,
    num_timesteps: int,
    warmup: float,
    dtype: torch.dtype = torch.float32,
) -> Tensor:
    betas = beta_end * torch.ones(num_timesteps, dtype=dtype)
    warmup_time = int(num_timesteps * warmup)
    betas[:warmup_time] = torch.linspace(beta_start, beta_end, warmup_time, dtype=dtype)
    return betas


def _cosine_beta_schedule(
    num_timesteps: int,
    offset: float = 0.008,
    dtype: torch.dtype = torch.float32,
) -> Tensor:
    rng = torch.arange(num_timesteps, dtype=dtype)
    f_t = torch.cos((rng / (num_timesteps - 1) + offset) / (1 + offset) * math.pi / 2) ** 2
    bar_alpha = f_t / f_t[0]
    beta = torch.zeros_like(bar_alpha)
    beta[1:] = (1 - (bar_alpha[1:] / bar_alpha[:-1])).clip(0, 0.999)
    return beta


def cast_beta_schedule(schedule: str) -> DiffusionBetaSchedule:
    assert schedule in get_args(DiffusionBetaSchedule), f"Unknown schedule type: {schedule}"
    return cast(DiffusionBetaSchedule, schedule)


def get_diffusion_beta_schedule(
    schedule: DiffusionBetaSchedule,
    num_timesteps: int,
    *,
    beta_start: float = 0.0001,
    beta_end: float = 0.02,
    warmup: float = 0.1,
    dtype: torch.dtype = torch.float32,
) -> Tensor:
    """Returns a beta schedule for the given schedule type.

    Args:
        schedule: The schedule type.
        num_timesteps: The total number of timesteps.
        beta_start: The initial beta value.
        beta_end: The final beta value.
        warmup: The fraction of timesteps to use for warmup.
        dtype: The dtype of the returned tensor.

    Returns:
        The beta schedule, a tensor with shape ``(num_timesteps)``.
    """
    match schedule:
        case "linear":
            return torch.linspace(beta_start, beta_end, num_timesteps, dtype=dtype)
        case "quad":
            return torch.linspace(beta_start**0.5, beta_end**0.5, num_timesteps, dtype=dtype) ** 2
        case "warmup":
            return _warmup_beta_schedule(beta_start, beta_end, num_timesteps, warmup, dtype=dtype)
        case "const":
            return torch.full((num_timesteps,), beta_end, dtype=dtype)
        case "cosine":
            return _cosine_beta_schedule(num_timesteps, dtype=dtype)
        case "jsd":
            return torch.linspace(num_timesteps, 1, num_timesteps, dtype=dtype) ** -1.0
        case _:
            raise NotImplementedError(f"Unknown schedule type: {schedule}")
