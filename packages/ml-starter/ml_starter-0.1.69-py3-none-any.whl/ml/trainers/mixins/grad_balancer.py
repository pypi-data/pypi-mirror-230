"""Implemenents a modified loss balancer.

The loss balancer balances the gradients of multiple losses. For each loss,
the gradients are scaled by the norm of the loss, so that the total norm after
all the losses are backpropagated is equal to the `total_norm` parameter.
"""

import torch
from torch import Tensor, nn

from ml.loggers.multi import MultiLogger
from ml.utils.mixed_precision import get_grad_norm


class GradBalancer:
    def __init__(
        self,
        logger: MultiLogger | None = None,
        total_norm: float = 1.0,
        epsilon: float = 1e-4,
        set_to_none: bool = True,
        norm_type: float = 2.0,
        foreach: bool | None = None,
    ) -> None:
        super().__init__()

        self.logger = logger
        self.total_norm = total_norm
        self.epsilon = epsilon
        self.set_to_none = set_to_none
        self.norm_type = norm_type
        self.foreach = foreach

    def balance(self, model: nn.Module, loss: Tensor, loss_names: list[str]) -> Tensor:
        num_losses = len(loss_names)
        assert loss.shape == (num_losses,), f"Loss should be a flat tensor, not {loss.shape}"
        norms_list = []
        for i in range(num_losses):
            model.zero_grad(set_to_none=self.set_to_none)
            loss[i].backward(retain_graph=True)
            with torch.no_grad():
                total_norm, _ = get_grad_norm(model.parameters(), self.norm_type, self.foreach)
                if self.logger is not None:
                    self.logger.log_scalar(f"{loss_names[i]}_grad_norm", total_norm, namespace="⚖️ balancer")
                norms_list.append(total_norm)
        model.zero_grad(set_to_none=self.set_to_none)
        norms = torch.stack(norms_list)
        scale = (self.total_norm / num_losses) / (norms + self.epsilon)
        return loss * scale.detach()
