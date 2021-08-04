from __future__ import annotations

import datetime
import json
import os
import typing
from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Type

import msgpack
from dataclasses_json import config
from google.protobuf import json_format as _json_format
from google.protobuf.struct_pb2 import Struct
from marshmallow import fields
from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.types import SerializableType

from flytekit.core.constants import MESSAGEPACK
from flytekit.core.context_manager import FlyteContext, FlyteContextManager
from flytekit.core.type_engine import AsyncTypeTransformer, TypeEngine, TypeTransformerFailedError
from flytekit.extras.pydantic_transformer.decorator import model_serializer, model_validator
from flytekit.loggers import logger
from flytekit.models.literals import Binary, Literal, Scalar, Schema
from flytekit.models.types import LiteralType, SchemaType

T = typing.TypeVar("T")


class SchemaFormat(Enum):
    """
    Represents the schema storage format (at rest).
    Currently only parquet is supported
    """

    PARQUET = "parquet"
    # ARROW = "arrow"
    # HDF5 = "hdf5"
    # CSV = "csv"
    # RECORDIO = "recordio"


class SchemaOpenMode(Enum):
    READ = "r"
    WRITE = "w"


def generate_ordered_files(directory: os.PathLike, n: int) -> typing.Generator[str, None, None]:
    for i in range(n):
        yield os.path.join(directory, f"{i:05}")


class SchemaReader(typing.Generic[T]):
    """
    Base SchemaReader to handle any readers (that can manage their own IO or otherwise)
    Use the simplified base LocalIOSchemaReader for non distributed dataframes
    """

    def __init__(self, from_path: str, cols: typing.Optional[typing.Dict[str, type]], fmt: SchemaFormat):
        self._from_path = from_path
        self._fmt = fmt
        self._columns = cols

    @property
    def from_path(self) -> str:
        return self._from_path

    @property
    def column_names(self) -> typing.Optional[typing.List[str]]:
        if self._columns:
            return list(self._columns.keys())
        return None

    @abstractmethod
    def iter(self, **kwargs) -> typing.Generator[T, None, None]: ...

    @abstractmethod
    def all(self, **kwargs) -> T: ...


class SchemaWriter(typing.Generic[T]):
    def __init__(self, to_path: str, cols: typing.Optional[typing.Dict[str, type]], fmt: SchemaFormat):
        self._to_path = to_path
        self._fmt = fmt
        self._columns = cols
        # TODO This should be change to send a stop instead of hardcoded to 1024
        self._file_name_gen = generate_ordered_files(Path(self._to_path), 1024)

    @property
    def to_path(self) -> str:
        return self._to_path

    @property
    def column_names(self) -> typing.Optional[typing.List[str]]:
        if self._columns:
            return list(self._columns.keys())
        return None

    @abstractmethod
    def write(self, *dfs, **kwargs): ...


class LocalIOSchemaReader(SchemaReader[T]):
    def __init__(self, from_path: str, cols: typing.Optional[typing.Dict[str, type]], fmt: SchemaFormat):
        super().__init__(from_path, cols, fmt)

    @abstractmethod
    def _read(self, *path: os.PathLike, **kwargs) -> T:
        pass

    def iter(self, **kwargs) -> typing.Generator[T, None, None]:
        with os.scandir(self._from_path) as it:  # type: ignore
            for entry in it:
                if (
                    not typing.cast(os.DirEntry, entry).name.startswith(".")
                    and typing.cast(os.DirEntry, entry).is_file()
                ):
                    yield self._read(Path(typing.cast(os.DirEntry, entry).path), **kwargs)

    def all(self, **kwargs) -> T:
        files: typing.List[os.PathLike] = []
        with os.scandir(self._from_path) as it:  # type: ignore
            for entry in it:
                if (
                    not typing.cast(os.DirEntry, entry).name.startswith(".")
                    and typing.cast(os.DirEntry, entry).is_file()
                ):
                    files.append(Path(typing.cast(os.DirEntry, entry).path))

        return self._read(*files, **kwargs)
