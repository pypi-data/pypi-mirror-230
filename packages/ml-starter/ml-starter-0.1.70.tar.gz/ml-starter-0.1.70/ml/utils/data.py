# mypy: disable-error-code="import"
"""Some common utilities for datasets and data loaders."""

import hashlib
import itertools
import logging
import math
import shutil
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import IO, BinaryIO, Collection, Sequence, TypeVar, cast

from smart_open import open
from torch.utils.data.dataloader import get_worker_info as _get_worker_info_base
from torch.utils.data.datapipes._decorator import functional_datapipe
from torch.utils.data.datapipes.datapipe import MapDataPipe
from torch.utils.data.datapipes.utils.common import StreamWrapper

from ml.core.env import get_s3_data_bucket
from ml.core.state import Phase
from ml.utils.distributed import get_rank, get_world_size
from ml.utils.timer import Timer, spinnerator

logger = logging.getLogger(__name__)

T = TypeVar("T")

MAGIC = b"SDS\n"
PRE_HEADER_SIZE = len(MAGIC) + 8


@dataclass
class WorkerInfo:
    worker_id: int
    num_workers: int
    in_worker: bool


def get_worker_info() -> WorkerInfo:
    """Gets a typed worker info object which always returns a value.

    Returns:
        The typed worker info object
    """
    if (worker_info := _get_worker_info_base()) is None:
        return WorkerInfo(
            worker_id=0,
            num_workers=1,
            in_worker=False,
        )

    return WorkerInfo(
        worker_id=worker_info.id,
        num_workers=worker_info.num_workers,
        in_worker=True,
    )


def split_n_items_across_workers(n: int, worker_id: int, num_workers: int) -> tuple[int, int]:
    """Splits N items across workers.

    This returns the start and end indices for the items to be processed by the
    given worker. The end index is exclusive.

    Args:
        n: The number of items to process.
        worker_id: The ID of the current worker.
        num_workers: The total number of workers.
    """
    assert n >= num_workers, f"n ({n}) must be >= num_workers ({num_workers})"
    assert 0 <= worker_id < num_workers, f"worker_id ({worker_id}) must be >= 0 and < num_workers ({num_workers})"

    # The number of items to process per worker.
    items_per_worker = math.ceil(n / num_workers)

    # The start and end indices for the items to process.
    start = worker_id * items_per_worker
    end = min(start + items_per_worker, n)

    return start, end


def get_dataset_splits(
    items: Sequence[T],
    valid: float | int,
    test: float | int,
) -> tuple[Sequence[T], Sequence[T], Sequence[T]]:
    """Splits a list of items into three sub-lists for train, valid, and test.

    Args:
        items: The list of items to split.
        valid: If a value between 0 and 1, the fraction of items to use for
            the validation set, otherwise the number of items to use for the
            validation set.
        test: If a value between 0 and 1, the fraction of items to use for
            the test set, otherwise the number of items to use for the test
            set.

    Returns:
        A tuple of three lists, one for each phase.

    Raises:
        ValueError: If the split sizes would be invalid.
    """
    num_items = len(items)

    # Converts a fraction to an integer number of items.
    if isinstance(valid, float):
        if 0 > valid or valid > 1:
            raise ValueError(f"Valid fraction must be between 0 and 1, got {valid}")
        valid = int(num_items * valid)
    if isinstance(test, float):
        if 0 > test or test > 1:
            raise ValueError(f"Test fraction must be between 0 and 1, got {test}")
        test = int(num_items * test)

    if valid + test > num_items:
        raise ValueError(f"Invalid number of items: {num_items}, valid: {valid}, test: {test}")

    train_items = items[: num_items - valid - test]
    valid_items = items[num_items - valid - test : num_items - test]
    test_items = items[num_items - test :]

    return train_items, valid_items, test_items


def get_dataset_split_for_phase(
    items: Sequence[T],
    phase: Phase,
    valid: float | int,
    test: float | int,
) -> Sequence[T]:
    """Gets the items for a given phase.

    Args:
        items: The list of items to split.
        phase: The phase to get the items for.
        valid: If a value between 0 and 1, the fraction of items to use for
            the validation set, otherwise the number of items to use for the
            validation set.
        test: If a value between 0 and 1, the fraction of items to use for
            the test set, otherwise the number of items to use for the test
            set.

    Returns:
        The items for the given phase.

    Raises:
        ValueError: If the phase is not valid.
    """
    train_items, valid_items, test_items = get_dataset_splits(items, valid, test)

    match phase:
        case "train":
            return train_items
        case "valid":
            return valid_items
        case "test":
            return test_items
        case _:
            raise ValueError(f"Invalid phase: {phase}")


def check_md5(file_path: str | Path, hash_str: str | None, chunk_size: int = 2**16) -> bool:
    """Checks the MD5 of the downloaded file.

    Args:
        file_path: Path to the downloaded file.
        hash_str: Expected MD5 of the file; if None, return True.
        chunk_size: Size of the chunks to read from the file.

    Returns:
        True if the MD5 matches, False otherwise.
    """
    if hash_str is None:
        return True

    md5 = hashlib.md5()

    with open(file_path, "rb") as f:
        for chunk in spinnerator(iter(lambda: f.read(chunk_size), b"")):
            md5.update(chunk)

    return md5.hexdigest() == hash_str


def check_sha256(file_path: str | Path, hash_str: str | None, chunk_size: int = 2**16) -> bool:
    """Checks the SHA256 of the downloaded file.

    Args:
        file_path: Path to the downloaded file.
        hash_str: Expected SHA256 of the file; if None, return True.
        chunk_size: Size of the chunks to read from the file.

    Returns:
        True if the SHA256 matches, False otherwise.
    """
    if hash_str is None:
        return True

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in spinnerator(iter(lambda: f.read(chunk_size), b"")):
            sha256.update(chunk)

    return sha256.hexdigest() == hash_str


def _get_files_to_compress(
    input_dir: Path,
    only_extension_set: set[str] | None,
    exclude_extension_set: set[str] | None,
) -> list[tuple[str, int]]:
    file_chunks: list[tuple[str, int]] = []
    for file_path in input_dir.rglob("*"):
        if not file_path.is_file():
            continue
        if only_extension_set is not None and file_path.suffix not in only_extension_set:
            continue
        if exclude_extension_set is not None and file_path.suffix in exclude_extension_set:
            continue
        num_bytes = file_path.stat().st_size
        file_chunks.append((str(file_path.relative_to(input_dir)), num_bytes))
    return sorted(file_chunks)


@dataclass
class Header:
    files: list[tuple[str, int]]
    init_offset: int = 0

    def encode(self) -> bytes:
        file_lengths = [num_bytes for _, num_bytes in self.files]
        names_bytes = [file_path.encode("utf-8") for file_path, _ in self.files]
        names_bytes_lengths = [len(n) for n in names_bytes]

        def get_byte_enc_and_dtype(n: int) -> tuple[int, str]:
            if n < 2**8:
                return 1, "B"
            elif n < 2**16:
                return 2, "H"
            elif n < 2**32:
                return 4, "I"
            else:
                return 8, "Q"

        file_lengths_dtype_int, file_lengths_dtype = get_byte_enc_and_dtype(max(file_lengths))
        name_lengths_dtype_int, name_lengths_dtype = get_byte_enc_and_dtype(max(names_bytes_lengths))

        return b"".join(
            [
                struct.pack("B", file_lengths_dtype_int),
                struct.pack("B", name_lengths_dtype_int),
                struct.pack("Q", len(self.files)),
                struct.pack(f"<{len(file_lengths)}{file_lengths_dtype}", *file_lengths),
                struct.pack(f"<{len(names_bytes)}{name_lengths_dtype}", *names_bytes_lengths),
                *names_bytes,
            ],
        )

    def write(self, fp: IO[bytes]) -> None:
        encoded = self.encode()
        fp.write(struct.pack("Q", len(encoded)))
        fp.write(encoded)

    @classmethod
    def decode(cls, b: bytes) -> "Header":
        def get_dtype_from_int(n: int) -> str:
            if n == 1:
                return "B"
            elif n == 2:
                return "H"
            elif n == 4:
                return "I"
            elif n == 8:
                return "Q"
            else:
                raise ValueError(f"Invalid dtype int: {n}")

        (file_lengths_dtype_int, name_lengths_dtype_int), b = struct.unpack("BB", b[:2]), b[2:]
        file_lengths_dtype = get_dtype_from_int(file_lengths_dtype_int)
        name_lengths_dtype = get_dtype_from_int(name_lengths_dtype_int)

        (num_files,), b = struct.unpack("Q", b[:8]), b[8:]

        fl_bytes = num_files * struct.calcsize(file_lengths_dtype)
        nl_bytes = num_files * struct.calcsize(name_lengths_dtype)
        file_lengths, b = struct.unpack(f"<{num_files}{file_lengths_dtype}", b[:nl_bytes]), b[nl_bytes:]
        names_bytes_lengths, b = struct.unpack(f"<{num_files}{name_lengths_dtype}", b[:fl_bytes]), b[fl_bytes:]

        names = []
        for name_bytes_length in names_bytes_lengths:
            name_bytes, b = b[:name_bytes_length], b[name_bytes_length:]
            names.append(name_bytes.decode("utf-8"))

        assert len(b) == 0, f"Bytes left over: {len(b)}"

        return cls(list(zip(names, file_lengths)))

    @classmethod
    def read(cls, fp: IO[bytes]) -> tuple["Header", int]:
        (num_bytes,) = struct.unpack("Q", fp.read(8))
        return cls.decode(fp.read(num_bytes)), num_bytes

    def shard(self, shard_id: int, total_shards: int) -> "Header":
        num_files = len(self.files)
        num_files_per_shard = math.ceil(num_files / total_shards)
        start = shard_id * num_files_per_shard
        end = min((shard_id + 1) * num_files_per_shard, num_files)
        shard_offset = sum(num_bytes for _, num_bytes in self.files[:start])
        return Header(self.files[start:end], self.init_offset + shard_offset)

    def offsets(self, header_size: int) -> list[int]:
        return [
            offset + header_size + self.init_offset
            for offset in itertools.accumulate((num_bytes for _, num_bytes in self.files), initial=0)
        ]


def compress_folder_to_sds(
    input_dir: str | Path,
    output_path: str | Path,
    only_extensions: Collection[str] | None = None,
    exclude_extensions: Collection[str] | None = None,
) -> None:
    """Compresses a given folder to a streamable dataset (SDS).

    Args:
        input_dir: The directory to compress.
        output_path: The root directory to write the shards to.
        only_extensions: If not None, only files with these extensions will be
            included.
        exclude_extensions: If not None, files with these extensions will be
            excluded.
    """
    only_extension_set = set(only_extensions) if only_extensions is not None else None
    exclude_extension_set = set(exclude_extensions) if exclude_extensions is not None else None
    input_dir, output_path = Path(input_dir).resolve(), Path(output_path).resolve()

    # Compresses each of the files.
    with Timer("getting files to compress", spinner=True):
        file_paths = _get_files_to_compress(input_dir, only_extension_set, exclude_extension_set)
    header = Header(file_paths)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    with open(output_path, "wb") as f:
        # Writes the header.
        f.write(MAGIC)
        header.write(f)

        # Writes each of the files.
        for file_path, _ in spinnerator(file_paths):
            with open(input_dir / file_path, "rb") as f_in:
                shutil.copyfileobj(f_in, f)


@functional_datapipe("sds")
class SdsDataPipe(MapDataPipe[tuple[str, int, BinaryIO]]):
    """Defines a base reader for streamable datasets.

    This used to incorporate more functionality, but I've since migrated to
    using ``smart_open`` which handles the various backends, so now the data
    format is basically just a TAR file with a more efficient header for
    random access.

    Parameters:
        shard_id: The index of the current reader shard. If not specified, will
            default to the current rank.
        total_shards: The total number of reader shards. If not specified, will
            default to the world size.
    """

    def __init__(self, path: str | Path) -> None:
        super().__init__()

        self.path = path

        self.shard_id = get_rank()
        self.total_shards = get_world_size()

        # Shards the header using the given shard parameters.
        header, header_num_bytes = self.get_header_and_offsets()

        self.header = header.shard(self.shard_id, self.total_shards)
        self.offsets = self.header.offsets(PRE_HEADER_SIZE + header_num_bytes)

    def get_header_and_offsets(self) -> tuple[Header, int]:
        init_bytes = self.read(0, PRE_HEADER_SIZE)
        assert init_bytes[: len(MAGIC)] == MAGIC, "Invalid magic number."
        header_num_bytes = struct.unpack("Q", init_bytes[len(MAGIC) :])[0]

        header_bytes = self.read(PRE_HEADER_SIZE, header_num_bytes)
        header = Header.decode(header_bytes)

        return header, header_num_bytes

    def read(self, start: int, length: int) -> bytes:
        with open(self.path, "rb") as f:
            f.seek(start)
            return f.read(length)

    def __len__(self) -> int:
        worker_info = get_worker_info()
        worker_id, num_workers = worker_info.worker_id, worker_info.num_workers
        start, end = split_n_items_across_workers(len(self.header.files), worker_id, num_workers)
        return end - start

    def __getitem__(self, index: int) -> tuple[str, int, BinaryIO]:
        worker_info = get_worker_info()
        worker_id, num_workers = worker_info.worker_id, worker_info.num_workers
        start, _ = split_n_items_across_workers(len(self.header.files), worker_id, num_workers)
        (name, length), offset = self.header.files[index + start], self.offsets[index + start]
        fp = open(self.path, "rb")
        fp.seek(offset)
        return name, length, cast(BinaryIO, StreamWrapper(fp))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path!r})"


def upload_data_to_s3(
    file_path: str | Path,
    prefix: str | None = None,
    name: str | None = None,
    bucket: str | None = None,
) -> None:
    """Uploads a data file to S3.

    Args:
        file_path: The path to the file to upload.
        prefix: The prefix to use for the uploaded file, if requested.
        name: The name to use for the uploaded file. If not specified, will
            default to the name of the file.
        bucket: The bucket to upload to. If not specified, will default to the
            bucket specified by ``get_s3_data_bucket``.
    """
    try:
        import boto3
    except ImportError:
        raise ImportError("boto3 is required to upload to S3.")

    if name is None:
        name = Path(file_path).name
    key = name if prefix is None else f"{prefix}/{name}"

    if bucket is None:
        bucket = get_s3_data_bucket()

    s3 = boto3.client("s3")
    s3.upload_file(str(file_path), bucket, key)
