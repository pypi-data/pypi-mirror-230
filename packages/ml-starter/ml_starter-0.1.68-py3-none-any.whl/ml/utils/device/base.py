"""Utilities for working with devices.

This module contains utilities for working with devices, such as moving tensors
and modules to devices, and getting prefetchers for non-blocking host-to-device
transfers.

The typical flow for using this module is:

.. code-block:: python

    from ml.utils.device.auto import detect_device

    device = detect_device()
    device.module_to(some_module)
    device.tensor_to(some_tensor)
    device.get_prefetcher(some_dataloader)
    device.recursive_apply(some_container, some_func)
"""

import contextlib
import functools
from abc import ABC, abstractmethod
from dataclasses import is_dataclass
from typing import Any, Callable, ContextManager, Generic, Iterable, Iterator, Mapping, Sequence, TypeVar

import numpy as np
import torch
from torch import Tensor, nn
from torch.utils.data.dataloader import DataLoader, _BaseDataLoaderIter

from ml.utils.containers import recursive_apply
from ml.utils.timer import Timer

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


def allow_nonblocking(device_a: torch.device, device_b: torch.device) -> bool:
    return device_a.type in ("cpu", "cuda") and device_b.type in ("cpu", "cuda")


class Prefetcher(Iterable[T_co], Generic[T_co]):
    """Helper class for pre-loading samples into device memory."""

    def __init__(
        self,
        to_device_func: Callable[[Any], Any],
        dataloader: DataLoader[T_co],
        raise_stop_iter: bool = False,
    ) -> None:
        super().__init__()

        self.to_device_func = to_device_func
        self.dataloader = dataloader
        self.raise_stop_iter = raise_stop_iter
        self.next_sample = None
        self.get_batch_time = 0.0
        self.to_device_time = 0.0
        self._dataloader_iter: _BaseDataLoaderIter | None = None

    @property
    def dataloader_iter(self) -> _BaseDataLoaderIter:
        if self._dataloader_iter is None:
            with Timer("starting dataloader", spinner=True):
                self._dataloader_iter = iter(self.dataloader)
        return self._dataloader_iter

    def prefetch(self) -> None:
        try:
            with Timer("getting sample from dataloader") as timer:
                next_sample = next(self.dataloader_iter)
            self.get_batch_time = timer.elapsed_time
            with Timer("moving sample to device") as timer:
                self.next_sample = self.to_device_func(next_sample)
            self.to_device_time = timer.elapsed_time
        except StopIteration:
            self.next_sample = None

    def recursive_chunk(self, item: Any, chunks: int) -> list[Any]:  # noqa: ANN401
        """Applies a function recursively to tensors in an item.

        Args:
            item: The item to apply the function to
            chunks: The number of output chunks

        Returns:
            The item, split into the requested number of chunks
        """
        if isinstance(item, (str, int, float)):
            return [item] * chunks
        if isinstance(item, np.ndarray):
            item = torch.from_numpy(item)
        if isinstance(item, Tensor):
            item_chunk_list = list(item.chunk(chunks, dim=0))
            assert len(item_chunk_list) == chunks, f"{len(item_chunk_list)=} != {chunks=}"
            return item_chunk_list
        if is_dataclass(item):
            item_chunk_dict = {k: self.recursive_chunk(v, chunks) for k, v in item.__dict__.items()}
            return [item.__class__(**{k: v[i] for k, v in item_chunk_dict.items()}) for i in range(chunks)]
        if isinstance(item, Mapping):
            item_chunk_dict = {k: self.recursive_chunk(v, chunks) for k, v in item.items()}
            return [{k: v[i] for k, v in item_chunk_dict.items()} for i in range(chunks)]
        if isinstance(item, Sequence):
            item_chunk_lists = [self.recursive_chunk(i, chunks) for i in item]
            return [[k[i] for k in item_chunk_lists] for i in range(chunks)]
        return item

    @classmethod
    def recursive_apply(cls, item: Any, func: Callable[[Tensor], Tensor]) -> Any:  # noqa: ANN401
        return recursive_apply(item, func)

    def __iter__(self) -> Iterator[T_co]:
        # Yields one sample quickly.
        next_sample = next(self.dataloader_iter)
        yield self.to_device_func(next_sample)

        try:
            self.prefetch()
            while True:
                if self.next_sample is None:
                    raise StopIteration
                sample = self.next_sample
                self.prefetch()
                yield sample

        except StopIteration:
            # Resets the dataloader if the iteration has completed.
            self._dataloader_iter = iter(self.dataloader)
            if self.raise_stop_iter:
                raise


class InfinitePrefetcher(Iterable[T_co]):
    def __init__(self, prefetcher: Prefetcher[T_co]) -> None:
        self.prefetcher = prefetcher

    def __iter__(self) -> Iterator[T_co]:
        while True:
            for batch in self.prefetcher:
                yield batch


class base_device(ABC):  # noqa: N801
    """Base mixin for different trainer device types."""

    def __init__(self) -> None:
        super().__init__()

        self._device = self._get_device()
        self._dtype_fp = self._get_floating_point_type()

    def __str__(self) -> str:
        return f"device({self._device.type}, {self._device.index}, {self._dtype_fp})"

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    @abstractmethod
    def has_device(cls) -> bool:
        """Detects whether or not the device is available.

        Returns:
            If the device is available
        """

    @abstractmethod
    def _get_device(self) -> torch.device:
        """Returns the device, for instantiating new tensors.

        Returns:
            The device
        """

    @abstractmethod
    def _get_floating_point_type(self) -> torch.dtype:
        """Returns the default floating point type to use.

        Returns:
            The dtype
        """

    @abstractmethod
    def get_torch_compile_backend(self) -> str | Callable:
        """Returns the backend to use for Torch compile.

        Returns:
            The backend
        """

    def sample_to_device(self, sample: T) -> T:
        return Prefetcher.recursive_apply(
            sample,
            lambda t: t.to(
                self._device,
                self._dtype_fp if t.is_floating_point() else t.dtype,
                non_blocking=allow_nonblocking(t.device, self._device),
            ),
        )

    def get_prefetcher(self, dataloader: DataLoader) -> Prefetcher:
        return Prefetcher(functools.partial(self.sample_to_device), dataloader)

    def module_to(self, module: nn.Module, with_dtype: bool = False) -> None:
        if with_dtype:
            module.to(self._device, self._dtype_fp)
        else:
            module.to(self._device)

    def tensor_to(self, tensor: np.ndarray | Tensor) -> Tensor:
        if isinstance(tensor, np.ndarray):
            tensor = torch.from_numpy(tensor)
        if tensor.is_floating_point():
            return tensor.to(self._device, self._dtype_fp)
        return tensor.to(self._device)

    def recursive_apply(self, item: T) -> T:
        def func(i: Tensor) -> Tensor:
            if isinstance(i, Tensor):
                return self.tensor_to(i)
            return i

        return recursive_apply(item, func)

    def autocast_context(self, enabled: bool = True) -> ContextManager:
        device_type = self._device.type
        if device_type not in ("cpu", "cuda"):
            return contextlib.nullcontext()
        if device_type == "cpu" and self._dtype_fp != torch.bfloat16:
            return contextlib.nullcontext()
        return torch.autocast(
            device_type=device_type,
            dtype=self._dtype_fp,
            enabled=enabled,
        )

    def supports_grad_scaler(self) -> bool:
        return False
