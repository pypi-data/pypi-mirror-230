"""A trainer mixin to support ``torch.compile``.

By default this is disabled, but can be enabled by setting the environment
variable ``TORCH_COMPILE=1`` or setting ``trainer.torch_compile.enabled=true``
in your configuration file.
"""

import logging
from dataclasses import dataclass
from typing import Callable, ParamSpec, TypeVar, cast

import torch
from omegaconf import II

from ml.core.config import conf_field
from ml.trainers.base import BaseTrainer, BaseTrainerConfig, ModelT, TaskT

logger = logging.getLogger(__name__)

T = TypeVar("T")
P = ParamSpec("P")


@dataclass
class TorchCompileConfig:
    model: bool = conf_field(II("oc.decode:${oc.env:COMPILE_MODEL,0}"), help="Enable Torch compilation for the model")
    func: bool = conf_field(II("oc.decode:${oc.env:COMPILE_FUNC,0}"), help="Enable Torch compilation for functions")
    fullgraph: bool = conf_field(False, help="Whether it is OK to break the model into subgraphs")
    dynamic: bool = conf_field(False, help="Whether to use dynamic shape tracing")
    backend: str = conf_field("auto", help="The backend to use")
    model_mode: str | None = conf_field("max-autotune", help="Either 'default', 'reduce-overhead' or 'max-autotune'")
    func_mode: str | None = conf_field("reduce-overhead", help="Either 'default', 'reduce-overhead' or 'max-autotune'")


@dataclass
class CompileConfig(BaseTrainerConfig):
    compiler: TorchCompileConfig = conf_field(TorchCompileConfig(), help="Torch compile config")


CompileConfigT = TypeVar("CompileConfigT", bound=CompileConfig)


class CompileMixin(BaseTrainer[CompileConfigT, ModelT, TaskT]):
    """Defines a mixin for calling `torch.compile` on models."""

    def _get_compiler_backend(self) -> str | Callable:
        backend: str | Callable = self.config.compiler.backend
        if backend == "auto":
            backend = self._device.get_torch_compile_backend()
            logger.info("Using torch-compile backend [%s]", backend)
        return backend

    def _compile_model(self, model: ModelT) -> ModelT:
        if self.config.compiler.model:
            model = cast(
                ModelT,
                torch.compile(
                    model,
                    fullgraph=self.config.compiler.fullgraph,
                    dynamic=self.config.compiler.dynamic,
                    backend=self._get_compiler_backend(),
                    mode=self.config.compiler.model_mode,
                    disable=not self.config.compiler.model,
                ),
            )

        return model

    def _compile_func(self, func: Callable[P, T]) -> Callable[P, T]:
        if self.config.compiler.func:
            func = torch.compile(
                func,
                fullgraph=self.config.compiler.fullgraph,
                dynamic=self.config.compiler.dynamic,
                backend=self._get_compiler_backend(),
                mode=self.config.compiler.func_mode,
                disable=not self.config.compiler.func,
            )

        return func
