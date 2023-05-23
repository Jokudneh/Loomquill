import os
import typing

from flytekit import FlyteContext, StructuredDatasetType, lazy_module
from flytekit.models import literals
from flytekit.models.literals import StructuredDatasetMetadata
from flytekit.types.structured.structured_dataset import (
    PARQUET,
    StructuredDataset,
    StructuredDatasetDecoder,
    StructuredDatasetEncoder,
    StructuredDatasetTransformerEngine,
)

pd = lazy_module("pandas")
vaex = lazy_module("vaex")


class VaexDataFrameToParquetEncodingHandler(StructuredDatasetEncoder):
    def __init__(self):
        super().__init__(vaex.dataframe.DataFrameLocal, None, PARQUET)

    def encode(
        self,
        ctx: FlyteContext,
        structured_dataset: StructuredDataset,
        structured_dataset_type: StructuredDatasetType,
    ) -> literals.StructuredDataset:
        df = typing.cast(vaex.dataframe.DataFrameLocal, structured_dataset.dataframe)
        local_dir = ctx.file_access.get_random_local_directory()
