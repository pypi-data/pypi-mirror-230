"""Defines a Tensorboard logging interface.

This is a pretty vanilla Tensorboard setup. Each phase gets its own
SummaryWriter, and scalars are logged to the writer for the current phase.
Additionally, when developing locally, we also start a Tensorboard server
in a subprocess. This can be disabled by setting ``DISABLE_TENSORBOARD=1``.
Also, a specific Tensorboard port can be specified by setting
``TENSORBOARD_PORT=<port>``.
"""

import atexit
import datetime
import functools
import logging
import os
import re
import shutil
import subprocess
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, TypeVar, cast

import torch
import torch.distributed
from omegaconf import MISSING, DictConfig, OmegaConf
from torch import Tensor
from torch.utils.tensorboard import SummaryWriter

from ml.core.config import conf_field
from ml.core.env import is_tensorboard_disabled
from ml.core.registry import register_logger
from ml.core.state import Phase, State
from ml.loggers.base import BaseLogger, BaseLoggerConfig
from ml.loggers.multi import TARGET_FPS
from ml.utils.colors import make_bold
from ml.utils.distributed import is_distributed, is_master
from ml.utils.logging import IntervalTicker
from ml.utils.networking import get_unused_port

logger: logging.Logger = logging.getLogger(__name__)

T = TypeVar("T")

WRITE_PROC_TEXT_EVERY_N_SECONDS: int = 60 * 2
DEFAULT_TENSORBOARD_PORT = 9249


def format_as_string(value: Any) -> str:  # noqa: ANN401
    if isinstance(value, str):
        return value
    if isinstance(value, Tensor):
        value = value.detach().float().cpu().item()
    if isinstance(value, (int, float)):
        return f"{value:.4g}"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, datetime.timedelta):
        return f"{value.total_seconds():.4g}s"
    if value is None:
        return ""
    if value is MISSING:
        return ""
    return str(value)


def iter_flat(config: dict) -> Iterator[tuple[list[str | None], str]]:
    for key, value in config.items():
        if isinstance(value, dict):
            is_first = True
            for sub_key_list, sub_value in iter_flat(value):
                yield [format_as_string(key) if is_first else None] + sub_key_list, sub_value
                is_first = False
        elif isinstance(value, (list, tuple)):
            is_first = True
            for i, sub_value in enumerate(value):
                for sub_key_list, sub_sub_value in iter_flat({f"{i}": sub_value}):
                    yield [format_as_string(key) if is_first else None] + sub_key_list, sub_sub_value
                    is_first = False
        else:
            yield [format_as_string(key)], format_as_string(value)


def to_markdown_table(config: DictConfig) -> str:
    config = cast(
        dict,
        OmegaConf.to_container(
            config,
            resolve=True,
            throw_on_missing=False,
            enum_to_str=True,
        ),
    )
    config_flat = list(iter_flat(config))

    # Gets rows of strings.
    rows: list[list[str]] = []
    for key_list, value in config_flat:
        row = ["" if key is None else key for key in key_list] + [value]
        rows.append(row)

    # Pads all rows to the same length.
    max_len = max(len(row) for row in rows)
    rows = [row[:-1] + [""] * (max_len - len(row)) + row[-1:] for row in rows]

    # Converts to a markdown table.
    header_str = "| " + " | ".join([f"key_{i}" for i in range(max_len - 1)]) + " | value |"
    header_sep_str = "|-" + "-|-" * (max_len - 1) + "-|"
    rows_str = "\n".join(["| " + " | ".join(row) + " |" for row in rows])
    return "\n".join([header_str, header_sep_str, rows_str])


@dataclass
class TensorboardLoggerConfig(BaseLoggerConfig):
    flush_seconds: float = conf_field(10.0, help="How often to flush logs")
    wait_seconds: float = conf_field(0.0, help="Time to wait before starting Tensorboard process")
    start_in_subprocess: bool = conf_field(True, help="Start TensorBoard subprocess")


@register_logger("tensorboard", TensorboardLoggerConfig)
class TensorboardLogger(BaseLogger[TensorboardLoggerConfig]):
    def __init__(self, config: TensorboardLoggerConfig) -> None:
        super().__init__(config)

        self.scalars: dict[Phase, dict[str, Callable[[], int | float | Tensor]]] = defaultdict(dict)
        self.strings: dict[Phase, dict[str, Callable[[], str]]] = defaultdict(dict)
        self.images: dict[Phase, dict[str, Callable[[], Tensor]]] = defaultdict(dict)
        self.audio: dict[Phase, dict[str, Callable[[], tuple[Tensor, int]]]] = defaultdict(dict)
        self.videos: dict[Phase, dict[str, Callable[[], Tensor]]] = defaultdict(dict)
        self.histograms: dict[Phase, dict[str, Callable[[], Tensor]]] = defaultdict(dict)
        self.point_clouds: dict[Phase, dict[str, Callable[[], Tensor]]] = defaultdict(dict)

        self.run_config: DictConfig | None = None
        self.logged_run_config = False

        self.line_str: str | None = None
        self.last_tensorboard_write_time = 0.0

        self.warning_ticker = IntervalTicker(60.0)
        self.proc: subprocess.Popen | None = None

        self._started = not is_master()

    def _start(self) -> None:
        if self._started:
            return

        threading.Thread(target=self.worker_thread, daemon=True).start()
        self._started = True

    def worker_thread(self) -> None:
        time.sleep(self.config.wait_seconds)

        if "TENSORBOARD_PORT" in os.environ:
            port, use_localhost = int(os.environ["TENSORBOARD_PORT"]), True
        else:
            port, use_localhost = get_unused_port(default=DEFAULT_TENSORBOARD_PORT), False

        def make_localhost(s: str) -> str:
            if use_localhost:
                s = re.sub(rf"://(.+?):{port}", f"://localhost:{port}", s)
            return s

        def parse_url(s: str) -> str:
            m = re.search(r" (http\S+?) ", s)
            if m is None:
                return s
            return f"Tensorboard: {m.group(1)}"

        command: list[str] = [
            "tensorboard",
            "serve",
            "--logdir",
            str(self.tensorboard_log_directory),
            "--bind_all",
            "--port",
            str(port),
            "--reload_interval",
            "15",
        ]
        logger.info("Tensorboard command: %s", " ".join(command))

        if not self.config.start_in_subprocess:
            logger.info("Tensorboard subprocess disabled because start_in_subprocess=False")

        elif is_tensorboard_disabled():
            logger.info("Tensorboard subprocess disabled because DISABLE_TENSORBOARD=1")

        else:
            self.proc = subprocess.Popen(  # pylint: disable=consider-using-with
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )

            # Gets the output line that shows the running address.
            assert self.proc is not None and self.proc.stdout is not None
            for line in self.proc.stdout:
                line_str = line.decode("utf-8")
                if line_str.startswith("TensorBoard"):
                    self.line_str = parse_url(make_localhost(line_str))
                    break

            if self.line_str is None:
                logger.warning("Failed to parse TensorBoard address")
            else:
                logger.info("Running TensorBoard process:\n%s", make_bold([self.line_str], "light-green", "cyan"))

            atexit.register(self.cleanup)

    def cleanup(self) -> None:
        if self.proc is not None:
            logger.info("Terminating TensorBoard process")
            self.proc.terminate()
            self.proc.wait()
            self.proc = None

    def __del__(self) -> None:
        self.cleanup()

    @property
    def tensorboard_log_directory(self) -> Path:
        return self.log_directory / "tensorboard"

    @functools.cached_property
    def train_writer(self) -> SummaryWriter:
        return SummaryWriter(
            self.tensorboard_log_directory / "train",
            flush_secs=self.config.flush_seconds,
        )

    @functools.cached_property
    def valid_writer(self) -> SummaryWriter:
        return SummaryWriter(
            self.tensorboard_log_directory / "valid",
            flush_secs=self.config.flush_seconds,
        )

    @functools.cached_property
    def test_writer(self) -> SummaryWriter:
        return SummaryWriter(
            self.tensorboard_log_directory / "test",
            flush_secs=self.config.flush_seconds,
        )

    @functools.lru_cache(None)  # Avoid clearing logs multiple times.
    def clear_logs(self) -> None:
        try:
            if not is_master():
                return
            if not self.tensorboard_log_directory.exists():
                return
            if not any(child.is_dir() for child in self.tensorboard_log_directory.iterdir()):
                return
            logger.info("Clearing TensorBoard logs in %s", self.tensorboard_log_directory)
            shutil.rmtree(self.tensorboard_log_directory)

        finally:
            if torch.distributed.is_initialized():
                torch.distributed.barrier()

    def get_writer(self, phase: Phase) -> SummaryWriter:
        self._start()
        if phase == "train":
            return self.train_writer
        if phase == "valid":
            return self.valid_writer
        if phase == "test":
            return self.test_writer
        raise NotImplementedError(f"Unexpected phase: {phase}")

    def log_scalar(self, key: str, value: Callable[[], int | float | Tensor], state: State, namespace: str) -> None:
        self.scalars[state.phase][f"{namespace}/{key}"] = value

    def log_string(self, key: str, value: Callable[[], str], state: State, namespace: str) -> None:
        self.strings[state.phase][f"{namespace}/{key}"] = value

    def log_image(self, key: str, value: Callable[[], Tensor], state: State, namespace: str) -> None:
        self.images[state.phase][f"{namespace}/{key}"] = value

    def log_audio(self, key: str, value: Callable[[], tuple[Tensor, int]], state: State, namespace: str) -> None:
        self.audio[state.phase][f"{namespace}/{key}"] = value

    def log_video(self, key: str, value: Callable[[], Tensor], state: State, namespace: str) -> None:
        self.videos[state.phase][f"{namespace}/{key}"] = value

    def log_histogram(self, key: str, value: Callable[[], Tensor], state: State, namespace: str) -> None:
        self.histograms[state.phase][f"{namespace}/{key}"] = value

    def log_point_cloud(self, key: str, value: Callable[[], Tensor], state: State, namespace: str) -> None:
        self.point_clouds[state.phase][f"{namespace}/{key}"] = value

    def log_config(self, config: DictConfig) -> None:
        self.run_config = config

    def write(self, state: State) -> None:
        if state.num_steps == 0:
            self.clear_logs()

        if self.line_str is not None:
            cur_time = state.elapsed_time_s
            if cur_time - self.last_tensorboard_write_time > WRITE_PROC_TEXT_EVERY_N_SECONDS:
                logger.info("Running TensorBoard process:\n%s", make_bold([self.line_str], "light-green", "cyan"))
                self.last_tensorboard_write_time = cur_time

        writer = self.get_writer(state.phase)
        all_keys: set[str] = set()
        walltime = state.start_time_s + state.elapsed_time_s

        def filter_items(items: Iterable[tuple[str, T]]) -> Iterable[tuple[str, T]]:
            duplicate_keys: set[str] = set()
            for k, v in items:
                if k in all_keys:
                    duplicate_keys
                else:
                    all_keys.add(k)
                    yield k, v
            if duplicate_keys and self.warning_ticker.tick():
                logger.warning("Found duplicate logging key(s): %s", duplicate_keys)

        for scalar_key, scalar_value in filter_items(self.scalars[state.phase].items()):
            writer.add_scalar(
                scalar_key,
                scalar_value(),
                global_step=state.num_steps,
                walltime=walltime,
            )

        for string_key, string_value in filter_items(self.strings[state.phase].items()):
            writer.add_text(
                string_key,
                string_value(),
                global_step=state.num_steps,
                walltime=walltime,
            )

        for image_key, image_value in filter_items(self.images[state.phase].items()):
            writer.add_image(
                image_key,
                image_value(),
                global_step=state.num_steps,
                walltime=walltime,
            )

        for audio_key, audio_value in filter_items(self.audio[state.phase].items()):
            audio_wav, audio_sample_rate = audio_value()
            writer.add_audio(
                audio_key,
                audio_wav,
                global_step=state.num_steps,
                walltime=walltime,
                sample_rate=audio_sample_rate,
            )

        for video_key, video_value in filter_items(self.videos[state.phase].items()):
            writer.add_video(
                video_key,
                video_value().unsqueeze(0),
                global_step=state.num_steps,
                walltime=walltime,
                fps=TARGET_FPS,
            )

        for hist_key, hist_value in filter_items(self.histograms[state.phase].items()):
            writer.add_histogram(
                hist_key,
                hist_value(),
                global_step=state.num_steps,
                walltime=walltime,
            )

        for pc_key, pc_value_func in filter_items(self.point_clouds[state.phase].items()):
            pc_value = pc_value_func()
            bsz, _, _ = pc_value.shape
            colors = torch.randint(0, 255, (bsz, 1, 3), device=pc_value.device).expand_as(pc_value)
            pc_value, colors = pc_value.flatten(0, 1).unsqueeze(0), colors.flatten(0, 1).unsqueeze(0)
            writer.add_mesh(
                pc_key,
                pc_value,
                colors=colors,
                global_step=state.num_steps,
                walltime=walltime,
            )

        if not self.logged_run_config and self.run_config is not None:
            writer.add_text(
                "config",
                to_markdown_table(self.run_config),
                global_step=state.num_steps,
                walltime=walltime,
            )
            self.logged_run_config = True

        self.clear(state)

    def clear(self, state: State) -> None:
        self.scalars[state.phase].clear()
        self.strings[state.phase].clear()
        self.images[state.phase].clear()
        self.audio[state.phase].clear()
        self.videos[state.phase].clear()
        self.histograms[state.phase].clear()
        self.point_clouds[state.phase].clear()

    def default_write_every_n_seconds(self, state: State) -> float:
        return 10.0 if is_distributed() or state.num_steps > 5000 else 1.0
