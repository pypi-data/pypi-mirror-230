"""Utility function for testing datasets.

All this does is iterates through some samples in a dataset or dataloder. It's
useful when developing a dataset because you can just add a small code snippet
to the bottom of your file like so:

.. code-block:: python

    if __name__ == "__main__":
        from ml.utils.testing import test_dataset, test_task

        test_dataset(MyDataset())
        test_task(MyTask(MyTaskConfig()))
"""

import itertools
import logging
import time
from typing import Any

import torch
from torch.utils.data.dataloader import DataLoader
from torch.utils.data.dataset import Dataset, IterableDataset

from ml.core.state import State
from ml.models.base import BaseModel, BaseModelConfig
from ml.tasks.base import BaseTask
from ml.tasks.rl.base import ReinforcementLearningTask
from ml.tasks.sl.base import SupervisedLearningTask
from ml.utils.checkpoint import is_missing
from ml.utils.logging import configure_logging
from ml.utils.timer import Timer, spinnerator

logger: logging.Logger = logging.getLogger(__name__)


def test_dataset(
    ds: Dataset | IterableDataset | DataLoader,
    max_samples: int = 3,
    log_interval: int = 10,
) -> None:
    """Iterates through a dataset.

    Args:
        ds: The dataset to iterate through
        max_samples: Maximum number of samples to loop through
        log_interval: How often to log the time it takes to load a sample
    """
    configure_logging()
    start_time = time.time()

    if isinstance(ds, (IterableDataset, DataLoader)):
        logger.info("Iterating samples in %s", "dataloader" if isinstance(ds, DataLoader) else "dataset")
        for i, _ in enumerate(itertools.islice(ds, max_samples)):
            if i % log_interval == 0:
                logger.info("Sample %d in %.2g seconds", i, time.time() - start_time)
    else:
        samples = len(ds)  # type: ignore[arg-type]
        logger.info("Dataset has %d items", samples)
        for i in spinnerator.range(min(samples, max_samples)):
            _ = ds[i]
            if i % log_interval == 0:
                logger.info("Sample %d in %.2g seconds", i, time.time() - start_time)


class DummyModelConfig(BaseModelConfig):
    pass


class DummyModel(BaseModel[BaseModelConfig]):
    def forward(self, *args: Any, **_kwargs: Any) -> Any:  # noqa: ANN401
        return args


def test_task(
    task: BaseTask,
    model: BaseModel | None = None,
    max_samples: int = 3,
    log_interval: int = 10,
    default_batch_size: int = 4,
) -> None:
    """Runs some adhoc tests on a task.

    This is useful for testing a task while developing it, by running through
    the various parts.

    Args:
        task: The task to test.
        model: The model to use for testing the task. If not provided, a dummy
            model will be created.
        max_samples: Maximum number of samples to loop through, for testing
            the raw dataset
        log_interval: How often to log the time it takes to load a sample,
            for testing the raw dataset
        default_batch_size: The default batch size to use for testing the
            dataloaders
    """
    configure_logging()
    start_time = time.time()

    if is_missing(task.config.train_dl, "batch_size") or not isinstance(task.config.train_dl.batch_size, int):
        task.config.train_dl.batch_size = default_batch_size
    if is_missing(task.config.valid_dl, "batch_size") or not isinstance(task.config.valid_dl.batch_size, int):
        task.config.valid_dl.batch_size = 1
    if is_missing(task.config.train_dl, "batch_size") or not isinstance(task.config.test_dl.batch_size, int):
        task.config.test_dl.batch_size = 1
    if is_missing(task.config.train_dl, "num_workers") or not isinstance(task.config.train_dl.num_workers, int):
        task.config.train_dl.num_workers = 2

    with Timer("initializing model"):
        if model is None:
            model = DummyModel(DummyModelConfig())
            logger.warning("Testing task using dummy Identity model")
        else:
            num_trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
            logger.info("Model has %s trainable parameters", f"{num_trainable_params:,}")
        device, dtype = task._device._get_device(), torch.float32
        model.init(device, dtype)
        task.to(device, dtype)

    if isinstance(task, SupervisedLearningTask):
        with Timer("building dataset", min_seconds_to_print=0.0):
            ds = task.get_dataset("train")
        with Timer("testing dataset", min_seconds_to_print=0.0):
            test_dataset(ds, max_samples, log_interval)
        with Timer("building dataloader", min_seconds_to_print=0.0):
            dl = task.get_dataloader(ds, "train")
        with Timer("building prefetcher", min_seconds_to_print=0.0):
            pf = task._device.get_prefetcher(dl)
        with Timer("getting sample", min_seconds_to_print=0.0):
            sample = next(iter(pf))
        state = State.init_state()
        output = task.run_model(model, sample, state)
        loss = task.compute_loss(model, sample, state, output)
        logger.info("Computed loss (%s) in %.2g seconds", loss, time.time() - start_time)

    elif isinstance(task, ReinforcementLearningTask):
        with Timer("getting worker pool", min_seconds_to_print=0.0):
            worker_pool = task.get_worker_pool()
        with Timer("getting samples", min_seconds_to_print=0.0):
            samples = task.collect_samples(model, worker_pool, 10)
        with Timer("building dataset", min_seconds_to_print=0.0):
            ds = task.build_rl_dataset(samples)
        with Timer("building dataloader", min_seconds_to_print=0.0):
            dl = task.get_dataloader(ds, "train")
        with Timer("building prefetcher", min_seconds_to_print=0.0):
            pf = task._device.get_prefetcher(dl)
        with Timer("getting sample", min_seconds_to_print=0.0):
            sample = next(iter(pf))
        state = State.init_state()
        output = task.run_model(model, sample, state)
        loss = task.compute_loss(model, sample, state, output)
        logger.info("Computed loss (%s) in %.2g seconds", loss, time.time() - start_time)

    else:
        raise NotImplementedError(f"Testing not implemented for task type {task}")
