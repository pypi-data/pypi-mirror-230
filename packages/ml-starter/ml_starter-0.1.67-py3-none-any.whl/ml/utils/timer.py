"""Defines a timer context manager for timing code blocks.

This also provides a simple spinner for long-running tasks.
"""

import errno
import functools
import logging
import os
import signal
import sys
import threading
import time
import warnings
from threading import Thread
from types import TracebackType
from typing import Any, Callable, ContextManager, Generic, Iterable, Iterator, ParamSpec, Sequence, Sized, TypeVar

from ml.utils.colors import colorize
from ml.utils.distributed import is_master

timer_logger: logging.Logger = logging.getLogger(__name__)

T = TypeVar("T")
P = ParamSpec("P")


@functools.lru_cache
def allow_spinners() -> bool:
    return (
        "PYTEST_CURRENT_TEST" not in os.environ
        and "pytest" not in sys.modules
        and sys.stdout.isatty()
        and os.environ.get("TERM") != "dumb"
        and is_master()
    )


class Spinner:
    def __init__(self, text: str | None = None) -> None:
        self._text = "" if text is None else text
        self._max_line_len = 0
        self._spinner_stop = False
        self._spinner_close = False
        self._flag = threading.Event()
        self._thread = Thread(target=self._spinner, daemon=True)
        self._thread.start()

        # If we're in a breakpoint, we want to close the spinner when we exit
        # the breakpoint.
        self._original_breakpointhook = sys.breakpointhook

    def _breakpointhook(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        warnings.warn("Breakpoint hit inside spinner; run `up 1` to see where it was hit")
        self.stop()
        sys.breakpointhook(*args, **kwargs)

    def set_text(self, text: str) -> "Spinner":
        sys.stderr.write(" " * (self._max_line_len + 1) + "\r")
        sys.stderr.flush()
        self._max_line_len = 0
        self._text = colorize(text, "grey")
        return self

    def start(self) -> None:
        self._spinner_stop = False
        self._flag.set()
        sys.breakpointhook = self._breakpointhook

    def stop(self) -> None:
        self._spinner_stop = True
        sys.breakpointhook = self._original_breakpointhook

    def close(self) -> None:
        self.stop()
        self._spinner_close = True
        self._thread.join()

    def _spinner(self) -> None:
        chars = [colorize(c, "light-yellow") for c in ("|", "/", "-", "\\")]
        while not self._spinner_close:
            self._flag.wait()
            start_time = time.time()
            while not self._spinner_stop:
                time.sleep(0.1)
                char = chars[int((time.time() * 10) % len(chars))]
                elapsed_secs = time.time() - start_time
                line = f"[ {char} {elapsed_secs:.1f} ] {self._text}\r"
                self._max_line_len = max(self._max_line_len, len(line))
                sys.stderr.write(line)
                sys.stderr.flush()
            sys.stderr.write(" " * (self._max_line_len + 1) + "\r")
            sys.stderr.flush()
            self._flag.clear()


@functools.lru_cache
def spinner() -> Spinner:
    return Spinner()


class Timer(ContextManager):
    """Defines a simple timer for logging an event."""

    def __init__(
        self,
        description: str,
        min_seconds_to_print: float = 5.0,
        logger: logging.Logger | None = None,
        spinner: bool = False,
    ) -> None:
        self.description = description
        self.min_seconds_to_print = min_seconds_to_print
        self._start_time: float | None = None
        self._elapsed_time: float | None = None
        self._logger = timer_logger if logger is None else logger
        self._use_spinner = spinner and allow_spinners()

    @property
    def elapsed_time(self) -> float:
        assert (elapsed_time := self._elapsed_time) is not None
        return elapsed_time

    def __enter__(self) -> "Timer":
        self._start_time = time.time()
        if self._use_spinner:
            spinner().set_text(self.description).start()
        return self

    def __exit__(self, _t: type[BaseException] | None, _e: BaseException | None, _tr: TracebackType | None) -> None:
        assert self._start_time is not None
        self._elapsed_time = time.time() - self._start_time
        if self._elapsed_time > self.min_seconds_to_print:
            self._logger.warning("Finished %s in %.3g seconds", self.description, self._elapsed_time)
        spinner().stop()


class spinnerator(Generic[T]):  # noqa: N801
    """Defines a spinning iterator which uses the built-in spinner."""

    def __init__(
        self,
        items: Sequence[T] | Iterable[T],
        desc: str | None = None,
        total: int | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._items = items
        self._desc = "Processing..." if desc is None else desc
        self._num_items: int = 0
        self._total_items: int | None = total
        self._iter: Iterator[T] | None = None
        self._logger = timer_logger if logger is None else logger
        self._use_spinner = allow_spinners()

    @property
    def desc(self) -> str:
        n, t = self._num_items, self._total_items
        processed_string = f"{n}" if t is None else f"{n}/{t} ({n/t:.0%})"
        return " ".join((self._desc, processed_string))

    @classmethod
    def range(
        cls,
        start: int | None,
        stop: int | None = None,
        step: int = 1,
        desc: str | None = None,
        logger: logging.Logger | None = None,
    ) -> "spinnerator[int]":
        if start is None:
            return spinnerator([], desc=desc, logger=logger)
        if stop is None:
            return spinnerator(
                range(0, start, step),
                desc=desc,
                logger=logger,
            )
        return spinnerator(
            range(start, stop, step),
            desc=desc,
            logger=logger,
        )

    def update(self, n: int = 1) -> None:
        self._num_items += n
        if self._use_spinner:
            spinner().set_text(self.desc)

    def __enter__(self) -> "spinnerator[T]":
        if self._use_spinner:
            spinner().set_text(self.desc).start()
        return self

    def __exit__(self, _t: type[BaseException] | None, _e: BaseException | None, _tr: TracebackType | None) -> None:
        if self._use_spinner:
            spinner().stop()

    def __iter__(self) -> Iterator[T]:
        assert self._items is not None, "Must provide items to iterate over"
        self._num_items = 0
        if self._total_items is None and isinstance(self._items, Sized):
            self._total_items = len(self._items)
        if self._use_spinner:
            spinner().set_text(self.desc).start()
        self._iter = iter(self._items)
        return self

    def __next__(self) -> T:
        assert self._iter is not None, "Must call __iter__ before __next__"
        try:
            item = next(self._iter)
        except Exception:
            spinner().stop()
            raise
        self._num_items += 1
        if self._use_spinner:
            spinner().set_text(self.desc)
        return item


def timeout(seconds: int, error_message: str = os.strerror(errno.ETIME)) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator for timing out long-running functions.

    Note that this function won't work on Windows.

    Args:
        seconds: Timeout after this many seconds
        error_message: Error message to pass to TimeoutError

    Returns:
        Decorator function
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        def _handle_timeout(*_: Any) -> None:  # noqa: ANN401
            raise TimeoutError(error_message)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator
