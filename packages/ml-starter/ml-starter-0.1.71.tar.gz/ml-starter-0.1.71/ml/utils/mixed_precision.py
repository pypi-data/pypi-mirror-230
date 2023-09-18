"""Defines functions used for mixed precision training."""

from typing import Iterable, cast

import torch
from torch import Tensor, inf, nn
from torch.utils._foreach_utils import _group_tensors_by_device_and_dtype, _has_foreach_support

GradDict = dict[tuple[torch.device, torch.dtype], list[list[Tensor]]]


@torch.no_grad()
def get_weight_norm(
    parameters: Iterable[nn.Parameter],
    norm_type: float = 2.0,
    foreach: bool | None = None,
) -> Tensor:
    """Computes the norm of an iterable of parameters.

    The norm is computed over all parameters together, as if they were
    concatenated into a single vector.

    Args:
        parameters: An iterable of the model parameters.
        norm_type: The type of the used p-norm.
        foreach: Use the faster foreach-based implementation.

    Returns:
        The total norm of the parameters (viewed as a single vector).
    """
    parameters = list(parameters)
    if len(parameters) == 0:
        return torch.tensor([0.0])

    first_device = parameters[0].device
    grouped_params = cast(GradDict, _group_tensors_by_device_and_dtype([[p.detach() for p in parameters]]))

    if norm_type == inf:
        norms = [p.detach().abs().max().to(first_device) for p in parameters]
        total_norm = norms[0] if len(norms) == 1 else torch.max(torch.stack(norms))
    else:
        norms = []
        for (device, _), [param] in grouped_params.items():
            if (foreach is None or foreach) and _has_foreach_support(param, device=device):
                norms.extend(torch._foreach_norm(param, norm_type))
            else:
                norms.extend([torch.norm(g, norm_type) for g in param])
        total_norm = torch.norm(torch.stack([norm.to(first_device) for norm in norms]), norm_type)

    return total_norm


@torch.no_grad()
def get_grad_norm(
    parameters: Iterable[nn.Parameter],
    norm_type: float = 2.0,
    foreach: bool | None = None,
) -> tuple[Tensor, GradDict]:
    grads = [p.grad for p in parameters if p.grad is not None]
    if len(grads) == 0:
        return torch.tensor([0.0]), {}

    first_device = grads[0].device
    grouped_grads = cast(GradDict, _group_tensors_by_device_and_dtype([[g.detach() for g in grads]]))

    if norm_type == inf:
        norms = [g.detach().abs().max().to(first_device) for g in grads]
        total_norm = norms[0] if len(norms) == 1 else torch.max(torch.stack(norms))
    else:
        norms = []
        for (device, _), [grads] in grouped_grads.items():
            if (foreach is None or foreach) and _has_foreach_support(grads, device=device):
                norms.extend(torch._foreach_norm(grads, norm_type))
            else:
                norms.extend([torch.norm(g, norm_type) for g in grads])
        total_norm = torch.norm(torch.stack([norm.to(first_device) for norm in norms]), norm_type)

    return total_norm, grouped_grads


@torch.no_grad()
def clip_grad_norm_(
    parameters: Iterable[nn.Parameter],
    max_norm: float,
    norm_type: float = 2.0,
    foreach: bool | None = None,
) -> tuple[Tensor, bool]:
    """Clips gradient norm of an iterable of parameters.

    The norm is computed over all gradients together, as if they were
    concatenated into a single vector. Gradients are modified in-place.

    Args:
        parameters: An iterable of the model parameters.
        max_norm: The maximum norm of the gradients.
        norm_type: The type of the used p-norm.
        foreach: Use the faster foreach-based implementation. If ``None``, use
            the foreach implementation for CUDA and CPU native tensors and
            silently fall back to the slow implementation for other device
            types. If ``True`` or ``False``, use the foreach or non-foreach
            implementation, respectively, and raise an error if the chosen
            implementation is not available.

    Returns:
        The total norm of the parameters (viewed as a single vector) and
        whether the parameters were successfully clipped.
    """
    total_norm, grouped_grads = get_grad_norm(parameters, norm_type, foreach)

    if not torch.isfinite(total_norm):
        return total_norm, False

    clip_coef = max_norm / (total_norm + 1e-6)
    clip_coef_clamped = torch.clamp(clip_coef, max=1.0)
    for (device, _), [grads] in grouped_grads.items():
        if (foreach is None or foreach) and _has_foreach_support(grads, device=device):
            torch._foreach_mul_(grads, clip_coef_clamped.to(device))  # type: ignore[call-overload]
        else:
            clip_coef_clamped_device = clip_coef_clamped.to(device)
            for g in grads:
                g.detach().mul_(clip_coef_clamped_device)

    return total_norm, True
