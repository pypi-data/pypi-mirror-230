"""Defines a mixin for doing FP16 scaling.

FP16 scaling is a technique for training with FP16 precision while maintaining
FP32 precision for the model weights. This is done by scaling the loss by a
large factor (e.g. 2^16) and then scaling the gradients by the inverse of that
factor. So if the scale factor starts to decrease, it means that the loss is
overflowing and training is diverging.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, TypeVar

import torch
from torch import Tensor, nn
from torch.distributed.fsdp.fully_sharded_data_parallel import FullyShardedDataParallel as FSDP
from torch.optim import Optimizer

from ml.core.config import conf_field
from ml.trainers.base import BaseTrainer, BaseTrainerConfig, ModelT, TaskT
from ml.trainers.mixins.grad_balancer import GradBalancer
from ml.utils.exceptions import MinGradScaleError, NaNError
from ml.utils.mixed_precision import clip_grad_norm_, get_weight_norm

logger = logging.getLogger(__name__)


@dataclass
class MixedPrecisionConfig:
    enabled: bool = conf_field(True, help="If set, should FP16 training be enabled")
    init_scale: float = conf_field(2.0**16, help="Initial scaling factor")
    growth_factor: float = conf_field(2.0, help="Factor by which the scale is multiplied if no gradient NaNs occur")
    backoff_factor: float = conf_field(0.5, help="Factor by which the scale is multiplied if gradient NaNs occur")
    growth_interval: int = conf_field(2000, help="How often to grow the scale")
    min_grad_scale: float = conf_field(1e-4, help="Minimum allowable gradient scale")
    foreach: bool | None = conf_field(None, help="If set, use foreach implementation")


@dataclass
class MixedPrecisionTrainerConfig(BaseTrainerConfig):
    mixed_precision: MixedPrecisionConfig = conf_field(MixedPrecisionConfig(), help="Mixed precision configuration")
    clip_grad_norm: float = conf_field(10.0, help="What to clip the gradient norm to")
    clip_grad_norm_type: Any = conf_field(2, help="Type of norm to use")
    balance_grad_norms: bool = conf_field(False, help="If set, balance gradient norms")


MixedPrecisionConfigT = TypeVar("MixedPrecisionConfigT", bound=MixedPrecisionTrainerConfig)


class MixedPrecisionTrainerMixin(BaseTrainer[MixedPrecisionConfigT, ModelT, TaskT]):
    """Defines a trainer mixin for doing FP16 scaling."""

    def __init__(self, config: MixedPrecisionConfigT) -> None:
        super().__init__(config)

        self.grad_scaler: torch.cuda.amp.GradScaler | None
        if self._device.supports_grad_scaler() and self.config.mixed_precision.enabled:
            self.grad_scaler = torch.cuda.amp.GradScaler(
                init_scale=self.config.mixed_precision.init_scale,
                growth_factor=self.config.mixed_precision.growth_factor,
                backoff_factor=self.config.mixed_precision.backoff_factor,
                growth_interval=self.config.mixed_precision.growth_interval,
                enabled=True,
            )
        else:
            self.grad_scaler = None

        self.autocast_context = self._device.autocast_context(enabled=self.config.mixed_precision.enabled)

        self.balancer = (
            GradBalancer(
                logger=self.logger,
                total_norm=self.config.clip_grad_norm,
                norm_type=self.config.clip_grad_norm_type,
                foreach=self.config.mixed_precision.foreach,
            )
            if self.config.balance_grad_norms
            else None
        )

    def scale_mixed_precision(self, tensor: Tensor) -> Tensor:
        if self.grad_scaler is not None:
            return self.grad_scaler.scale(tensor)
        return tensor

    def backward_grads(self, model: nn.Module, loss: Tensor, loss_names: list[str]) -> None:
        if self.grad_scaler is not None:
            loss = self.grad_scaler.scale(loss)
        if self.balancer is not None:
            loss = self.balancer.balance(model, loss, loss_names)
        if loss.numel() > 1:
            loss = loss.sum()
        isnan = not bool(torch.isfinite(loss))
        if isnan:
            loss.backward(torch.zeros_like(loss))
        else:
            loss.backward()

        if isnan:
            if any(not torch.isfinite(p).all() for p in model.parameters()):
                raise NaNError("One or more model parameters are NaN")
            if self.grad_scaler is not None:
                with torch.no_grad():
                    new_scale = self.grad_scaler.get_scale() * self.grad_scaler.get_backoff_factor()
                    if new_scale < self.config.mixed_precision.min_grad_scale:
                        raise MinGradScaleError("Minimum gradient scale reached; your loss is probably exploding")
                    logger.warning("Loss NaNs detected; reducing scale to %.2g", new_scale)
                    self.grad_scaler.update(new_scale)

    @torch.no_grad()
    def step_optimizer(self, model: nn.Module, optim: Optimizer, num_steps: int = 1) -> None:
        clip_norm = self.config.clip_grad_norm
        norm_type = self.config.clip_grad_norm_type

        # When accumulating multiple steps of gradients per backward pass, we
        # need to divide the gradients by the number of steps.
        if num_steps > 1:
            for p in model.parameters():
                if p.grad is not None:
                    p.grad /= num_steps

        # Unscale gradients.
        if self.grad_scaler is not None:
            self.grad_scaler.unscale_(optim)

        # Clips gradients.
        if isinstance(model, FSDP):
            total_norm = model.clip_grad_norm_(clip_norm, norm_type)
            was_clipped = bool(torch.isfinite(total_norm))
        else:
            total_norm, was_clipped = clip_grad_norm_(
                model.parameters(),
                max_norm=clip_norm,
                norm_type=norm_type,
                foreach=self.config.mixed_precision.foreach,
            )

        # Logs weight and gradient norms.
        self.logger.log_scalar("weight_norm", lambda: get_weight_norm(model.parameters()), namespace="📉 optim")
        self.logger.log_scalar("grad_norm", total_norm, namespace="📉 optim")

        # Steps the optimizer.
        if self.grad_scaler is None:
            if was_clipped:
                optim.step()
        elif was_clipped:
            self.grad_scaler.step(optim)
            self.grad_scaler.update()
        else:
            if any(not torch.isfinite(p).all() for p in model.parameters()):
                raise NaNError("One or more model parameters are NaN")
            new_scale = self.grad_scaler.get_scale() * self.grad_scaler.get_backoff_factor()
            bad = [k for k, v in model.named_parameters() if v.grad is not None and not torch.isfinite(v.grad).all()]
            bad_str = ", ".join(bad[:5])
            if len(bad) > 5:
                bad_str += f" (plus {len(bad) - 5} more)"
            bad_str += f" out of {sum(1 for _ in model.parameters())} parameters"
            if new_scale < self.config.mixed_precision.min_grad_scale:
                raise MinGradScaleError(f"Minimum gradient scale reached. Bad parameters: {bad_str}")
            logger.warning("Gradient NaNs detected for %s; reducing scale to %.2g", bad_str, new_scale)
            self.grad_scaler.update(new_scale)

    def log_mp_scale(self) -> None:
        if (scaler := self.grad_scaler) is not None and scaler._enabled:
            self.logger.log_scalar("scale", scaler.get_scale, namespace="⚖️ fp16")
            self.logger.log_scalar("growth", scaler._get_growth_tracker, namespace="⚖️ fp16")

    def load_state_dict(self, state_dict: dict) -> None:
        if self.grad_scaler is not None and "grad_scaler" in state_dict:
            self.grad_scaler.load_state_dict(json.loads(state_dict["grad_scaler"]))
        super().load_state_dict(state_dict)

    def update_state_dict(self, state_dict: dict) -> None:
        if self.grad_scaler is not None:
            assert "grad_scaler" not in state_dict, "Duplicate keys!"
            state_dict["grad_scaler"] = json.dumps(self.grad_scaler.state_dict())
        super().update_state_dict(state_dict)
