import importlib.util
import typing

from flytekit import FlyteContext, lazy_module
from flytekit.models import literals
from flytekit.models.literals import StructuredDatasetMetadata
from flytekit.models.types import StructuredDatasetType
from flytekit.types.structured.structured_dataset import (
    PARQUET,
    StructuredDataset,
    StructuredDatasetDecoder,
    StructuredDatasetEncoder,
    StructuredDatasetTransformerEngine,
)

pd = lazy_module("pandas")
pyspark = lazy_module("pyspark")

# Base Spark DataFrame (Spark 3.x or Spark 4 parent)
ps_dataframe = lazy_module("pyspark.sql.dataframe")
DataFrame = ps_dataframe.DataFrame


class SparkDataFrameRenderer:
    """
    Render a Spark dataframe schema as an HTML table.
    """

    def to_html(self, df: DataFrame) -> str:
        assert isinstance(df, DataFrame)
        return pd.DataFrame(df.schema, columns=["StructField"]).to_html()


class SparkToParquetEncodingHandler(StructuredDatasetEncoder):
    def __init__(self):
        super().__init__(DataFrame, None, PARQUET)

    def encode(
