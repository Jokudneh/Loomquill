import importlib.util
import typing
from typing import Type

from flytekit import FlyteContext, lazy_module
from flytekit.extend import T, TypeEngine, TypeTransformer
from flytekit.models.literals import Literal, Scalar, Schema
from flytekit.models.types import LiteralType, SchemaType
from flytekit.types.schema import SchemaEngine, SchemaFormat, SchemaHandler, SchemaReader, SchemaWriter

pyspark = lazy_module("pyspark")


class SparkDataFrameSchemaReader(SchemaReader[pyspark.sql.DataFrame]):
    """
    Implements how SparkDataFrame should be read using the ``open`` method of FlyteSchema
    """

    def __init__(self, from_path: str, cols: typing.Optional[typing.Dict[str, type]], fmt: SchemaFormat):
        super().__init__(from_path, cols, fmt)

    def iter(self, **kwargs) -> typing.Generator[T, None, None]:
        raise NotImplementedError("Spark DataFrame reader cannot iterate over individual chunks in spark dataframe")

    def all(self, **kwargs) -> pyspark.sql.DataFrame:
        if self._fmt == SchemaFormat.PARQUET:
            ctx = FlyteContext.current_context().user_space_params
            return ctx.spark_session.read.parquet(self.from_path)
        raise AssertionError("Only Parquet type files are supported for spark dataframe currently")


class SparkDataFrameSchemaWriter(SchemaWriter[pyspark.sql.DataFrame]):
    """
    Implements how SparkDataFrame should be written to using ``open`` method of FlyteSchema
    """

    def __init__(self, to_path: str, cols: typing.Optional[typing.Dict[str, type]], fmt: SchemaFormat):
        super().__init__(to_path, cols, fmt)

    def write(self, *dfs: pyspark.sql.DataFrame, **kwargs):
        if dfs is None or len(dfs) == 0:
            return
        if len(dfs) > 1:
