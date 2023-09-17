# mypy: disable-error-code="import"
"""Defines utilites for saving and loading audio streams.

The main API for using this module is:

.. code-block:: python

    from ml.utils.audio import read_audio, write_audio

This just uses FFMPEG so it should be rasonably quick.
"""

import logging
import random
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Callable, Iterator

import numpy as np
import sarfile
import soundfile as sf
import torch
import torchaudio.functional as A
from smart_open import open
from torch import Tensor
from torch.utils.data.dataset import IterableDataset

from ml.utils.io import prefetch_samples
from ml.utils.numpy import as_numpy_array

logger = logging.getLogger(__name__)

DEFAULT_BLOCKSIZE = 16_000

AUDIO_FILE_EXTENSIONS = [".wav", ".flac", ".mp3"]


@dataclass
class AudioProps:
    sample_rate: int
    channels: int
    num_frames: int

    @classmethod
    def from_file(cls, fpath: str | Path) -> "AudioProps":
        info = sf.info(str(fpath))
        return cls(
            sample_rate=info.samplerate,
            channels=info.channels,
            num_frames=info.frames,
        )


@dataclass
class AudioFile:
    path: Path
    props: AudioProps

    @classmethod
    def parse(cls, line: str) -> "AudioFile":
        path, num_frames, sample_rate, channels = re.split(r"\s+", line.strip())
        return AudioFile(
            path=Path(path),
            props=AudioProps(
                sample_rate=int(sample_rate),
                channels=int(channels),
                num_frames=int(num_frames),
            ),
        )

    def __repr__(self) -> str:
        return "\t".join(
            [
                str(self.path),
                str(self.props.sample_rate),
                str(self.props.channels),
                str(self.props.num_frames),
            ]
        )


def rechunk_audio(
    audio_chunks: Iterator[np.ndarray],
    *,
    prefetch_n: int = 1,
    chunk_length: int | None = None,
    sample_rate: tuple[int, int] | None = None,
) -> Iterator[np.ndarray]:
    """Rechunks audio chunks to a new size.

    Args:
        audio_chunks: The input audio chunks.
        prefetch_n: The number of samples to prefetch.
        chunk_length: The length of the chunks to yield.
        sample_rate: If set, resample all chunks to this sample rate. The first
            argument is the input sample rate and the second argument is the
            output sample rate.

    Yields:
        Chunks of waveforms with shape ``(channels, num_frames)``.
    """
    if chunk_length is None:
        yield from prefetch_samples(audio_chunks, prefetch_n)
        return

    audio_chunk_list: list[np.ndarray] = []
    total_length: int = 0
    for chunk in prefetch_samples(audio_chunks, prefetch_n):
        if sample_rate is not None and sample_rate[0] != sample_rate[1]:
            chunk = A.resample(torch.from_numpy(chunk), sample_rate[0], sample_rate[1]).numpy()
        cur_chunk_length = chunk.shape[-1]
        while total_length + cur_chunk_length >= chunk_length:
            yield np.concatenate(audio_chunk_list + [chunk[..., : chunk_length - total_length]], axis=-1)
            chunk = chunk[..., chunk_length - total_length :]
            audio_chunk_list = []
            total_length = 0
            cur_chunk_length = chunk.shape[-1]
        if cur_chunk_length > 0:
            audio_chunk_list.append(chunk)
            total_length += cur_chunk_length

    if audio_chunk_list:
        yield np.concatenate(audio_chunk_list, axis=-1)


def read_audio(
    in_file: str | Path,
    *,
    blocksize: int = DEFAULT_BLOCKSIZE,
    prefetch_n: int = 1,
    chunk_length: int | None = None,
    sample_rate: int | None = None,
) -> Iterator[np.ndarray]:
    """Function that reads an audio file to a stream of numpy arrays using SoundFile.

    Args:
        in_file: Path to the input file.
        blocksize: Number of samples to read at a time.
        prefetch_n: The number of samples to prefetch.
        chunk_length: The length of the chunks to yield.
        sample_rate: If set, resample all chunks to this sample rate.

    Yields:
        Audio chunks as numpy arrays, with shape ``(channels, num_frames)``.
    """
    if chunk_length is None and sample_rate is None:
        with sf.SoundFile(str(in_file), mode="r") as f:
            for frame in f.blocks(blocksize=blocksize, always_2d=True):
                yield frame.T

    else:
        with sf.SoundFile(str(in_file), mode="r") as f:

            def chunk_iter() -> Iterator[np.ndarray]:
                for frame in f.blocks(blocksize=blocksize, always_2d=True):
                    yield frame.T

            sr: int = f.samplerate

            yield from rechunk_audio(
                chunk_iter(),
                prefetch_n=prefetch_n,
                chunk_length=chunk_length,
                sample_rate=None if sample_rate is None or sr == sample_rate else (sr, sample_rate),
            )


def write_audio(itr: Iterator[np.ndarray | Tensor], out_file: str | Path, sample_rate: int) -> None:
    """Function that writes a stream of audio to a file using SoundFile.

    Args:
        itr: Iterator of audio chunks, with shape ``(channels, num_frames)``.
        out_file: Path to the output file.
        sample_rate: Sampling rate of the audio.
    """
    first_chunk = as_numpy_array(next(itr))

    # Parses the number of channels from the first audio chunk and gets a
    # function for cleaning up the input waveform.
    assert (ndim := len(first_chunk.shape)) in (1, 2), f"Expected 1 or 2 dimensions, got {ndim}"
    if ndim == 2:
        assert any(s in (1, 2) for s in first_chunk.shape), f"Expected 1 or 2 channels, got shape {first_chunk.shape}"
        channels = [s for s in first_chunk.shape if s in (1, 2)][0]

        def cleanup(x: np.ndarray) -> np.ndarray:
            return x.T if x.shape[0] == channels else x

    else:
        channels = 1

        def cleanup(x: np.ndarray) -> np.ndarray:
            return x[:, None]

    with sf.SoundFile(str(out_file), mode="w", samplerate=sample_rate, channels=channels) as f:
        f.write(cleanup(first_chunk))
        for chunk in itr:
            f.write(cleanup(as_numpy_array(chunk.T)))


get_audio_props = AudioProps.from_file


def read_audio_random_order(
    in_file: str | Path | BinaryIO,
    chunk_length: int,
    *,
    sample_rate: int | None = None,
    include_last: bool = False,
) -> Iterator[np.ndarray]:
    """Function that reads a stream of audio from a file in random order.

    This is similar to ``read_audio``, but it yields chunks in random order,
    which can be useful for training purposes.

    Args:
        in_file: Path to the input file.
        chunk_length: Size of the chunks to read.
        sample_rate: Sampling rate to resample the audio to. If ``None``,
            will use the sampling rate of the input audio.
        include_last: Whether to include the last chunk, even if it's smaller
            than ``chunk_length``.

    Yields:
        Audio chunks as arrays, with shape ``(n_channels, chunk_length)``.
    """
    with sf.SoundFile(str(in_file) if isinstance(in_file, (str, Path)) else in_file, mode="r") as f:
        num_frames = len(f)
        if sample_rate is not None:
            chunk_length = round(chunk_length * f.samplerate / sample_rate)
        chunk_starts = list(range(0, num_frames, chunk_length))
        if not include_last and num_frames - chunk_starts[-1] < chunk_length:
            chunk_starts = chunk_starts[:-1]
        random.shuffle(chunk_starts)
        for chunk_start in chunk_starts:
            f.seek(chunk_start)
            chunk = f.read(chunk_length, dtype="float32", always_2d=True).T
            if sample_rate is not None and sample_rate != f.samplerate:
                chunk = A.resample(torch.from_numpy(chunk), f.samplerate, sample_rate).numpy()
            yield chunk


class AudioSarFileDataset(IterableDataset[tuple[Tensor, int, tuple[str, int]]]):
    """Defines a dataset for iterating through audio samples in a SAR file.

    This dataset yields samples with shape ``(num_channels, num_samples)``,
    along with the name of the file they were read from.

    Parameters:
        sar_file: The SAR file to read from.
        sample_rate: The sampling rate to resample the audio to.
        length_ms: The length of the audio clips in milliseconds.
        channel_idx: The index of the channel to use.
    """

    def __init__(
        self,
        sar_file: str | Path,
        sample_rate: int,
        length_ms: float,
        max_iters: int | None = None,
        channel_idx: int = 0,
        include_file_fn: Callable[[str, int], bool] | None = None,
    ) -> None:
        super().__init__()

        self.sar_file = sar_file
        self.sample_rate = sample_rate
        self.max_iters = max_iters
        self.channel_idx = channel_idx
        self._include_file_fn = include_file_fn

        self.chunk_frames = round(sample_rate * length_ms / 1000)
        self._sar = sarfile.open(sar_file)

        self._fp: BinaryIO | None = None
        self._names: list[str] | None = None

    def include_file(self, name: str, num_bytes: int) -> bool:
        return True if self._include_file_fn is None else self._include_file_fn(name, num_bytes)

    @property
    def sar(self) -> sarfile.sarfile:
        return self._sar

    @property
    def names(self) -> list[str]:
        assert self._names is not None, "Must call __iter__ first!"
        return self._names

    def __iter__(self) -> "AudioSarFileDataset":
        if self._fp is not None:
            self._fp.close()
        self._fp = open(self.sar_file, "rb")
        if self._names is None:
            self._names = [
                name
                for (name, num_bytes) in self._sar._header.files
                if any(name.endswith(suffix) for suffix in AUDIO_FILE_EXTENSIONS) and self.include_file(name, num_bytes)
            ]
            self._names = list(sorted(self._names))
        return self

    def __next__(self) -> tuple[Tensor, int, tuple[str, int]]:
        name = random.choice(self.names)
        fidx = self._sar.name_index[name]

        with self.sar[fidx] as fp, sf.SoundFile(fp) as sfp:
            num_frames = len(sfp)
            chunk_length = round(self.chunk_frames * sfp.samplerate / self.sample_rate)
            start_frame = random.randint(0, num_frames - chunk_length)
            sfp.seek(start_frame)
            audio_np = sfp.read(chunk_length, dtype="float32", always_2d=True).T
            audio = torch.from_numpy(audio_np)
            if sfp.samplerate != self.sample_rate:
                audio = A.resample(audio, sfp.samplerate, self.sample_rate)

        return audio, fidx, self.sar._header.files[fidx]


class AudioSarFileSpeakerDataset(IterableDataset[tuple[Tensor, int]], ABC):
    """Defines a dataset with speaker information for a TAR file."""

    def __init__(self, ds: AudioSarFileDataset) -> None:
        super().__init__()

        self.ds = ds
        self._ds_iter: AudioSarFileDataset | None = None

        # Builds the mapping from the file index to the speaker ID.
        self._speaker_ids = [self.get_speaker_id(*finfo) for finfo in self.ds.sar._header.files]
        self._speaker_map = {k: i for i, k in enumerate(set(self._speaker_ids))}
        self._inv_speaker_map = {v: k for k, v in self._speaker_map.items()}

    @abstractmethod
    def get_speaker_id(self, name: str, num_bytes: int) -> str | int:
        """Returns the speaker ID for a given file.

        Args:
            name: The file entry name.
            num_bytes: The number of bytes in the file entry.

        Returns:
            The speaker ID corresponding to the file.
        """

    @property
    def num_speakers(self) -> int:
        assert self._speaker_map is not None, "Must call __iter__ first!"
        return len(self._speaker_map)

    @property
    def ds_iter(self) -> AudioSarFileDataset:
        assert self._ds_iter is not None, "Must call __iter__ first!"
        return self._ds_iter

    @property
    def speaker_ids(self) -> list[str | int]:
        assert self._speaker_ids is not None, "Must call __iter__ first!"
        return self._speaker_ids

    @property
    def speaker_map(self) -> dict[str | int, int]:
        assert self._speaker_map is not None, "Must call __iter__ first!"
        return self._speaker_map

    @property
    def inv_speaker_map(self) -> dict[int, str | int]:
        assert self._speaker_map is not None, "Must call __iter__ first!"
        return {v: k for k, v in self._speaker_map.items()}

    def __iter__(self) -> "AudioSarFileSpeakerDataset":
        self._ds_iter = self.ds.__iter__()
        return self

    def __next__(self) -> tuple[Tensor, int]:
        audio, fidx, _ = self.ds_iter.__next__()
        return audio, self.speaker_map[self.speaker_ids[fidx]]
