import os
import typing
from typing import Type

import pandas

from flytekit import FlyteContext
from flytekit.core.type_engine import AsyncTypeTransformer, T, TypeEngine
from flytekit.models.literals import Literal, Scalar, Schema
from flytekit.models.types import LiteralType, SchemaType
from flytekit.types.schema import LocalIOSchemaReader, LocalIOSchemaWriter, SchemaEngine, SchemaFormat, SchemaHandler


class ParquetIO(object):
    PARQUET_ENGINE = "pyarrow"

    def _read(self, chunk: os.PathLike, columns: typing.Optional[typing.List[str]], **kwargs) -> pandas.DataFrame:
        return pandas.read_parquet(chunk, columns=columns, engine=self.PARQUET_ENGINE, **kwargs)

    def read(
        self, *files: os.PathLike, columns: typing.Optional[typing.List[str]] = None, **kwargs
    ) -> pandas.DataFrame:
        frames = [self._read(chunk=f, columns=columns, **kwargs) for f in files if os.path.getsize(f) > 0]
        if len(frames) == 1:
            return frames[0]
        elif len(frames) > 1:
            return pandas.concat(frames, copy=True)
        return pandas.DataFrame()

    def write(
        self,
        df: pandas.DataFrame,
        to_file: os.PathLike,
        coerce_timestamps: str = "us",
        allow_truncated_timestamps: bool = False,
        **kwargs,
    ):
