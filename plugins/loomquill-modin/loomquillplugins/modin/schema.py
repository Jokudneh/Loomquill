import os
import typing
from typing import Type

from flytekit import FlyteContext, lazy_module
from flytekit.extend import T, TypeEngine, TypeTransformer
from flytekit.models.literals import Literal, Scalar, Schema
from flytekit.models.types import LiteralType, SchemaType
from flytekit.types.schema import LocalIOSchemaReader, LocalIOSchemaWriter, SchemaEngine, SchemaFormat, SchemaHandler
from flytekit.types.schema.types import FlyteSchemaTransformer

modin = lazy_module("modin")
pandas = lazy_module("modin.pandas")


class ModinPandasSchemaReader(LocalIOSchemaReader[pandas.DataFrame]):
    """
    Implements how ModinPandasDataFrame should be read using the ``open`` method of FlyteSchema
    """

    def __init__(
        self,
        from_path: str,
        cols: typing.Optional[typing.Dict[str, type]],
        fmt: SchemaFormat,
    ):
        super().__init__(from_path, cols, fmt)

    def all(self, **kwargs) -> pandas.DataFrame:
        if self._fmt == SchemaFormat.PARQUET:
            return pandas.read_parquet(self.from_path + "/00000")
        raise AssertionError("Only Parquet type files are supported for modin pandas dataframe currently")


class ModinPandasSchemaWriter(LocalIOSchemaWriter[pandas.DataFrame]):
    """
    Implements how ModinPandasDataFrame should be written to using ``open`` method of FlyteSchema
    """
