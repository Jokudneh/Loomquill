import os
import typing
from dataclasses import dataclass

import numpy as np
import pytest
from typing_extensions import Annotated

from flytekit import FlyteContext, FlyteContextManager, kwtypes, task, workflow
from flytekit.models import literals
from flytekit.models.literals import StructuredDatasetMetadata
from flytekit.models.types import StructuredDatasetType
from flytekit.types.structured.basic_dfs import CSVToPandasDecodingHandler, PandasToCSVEncodingHandler
from flytekit.types.structured.structured_dataset import (
    CSV,
    DF,
    PARQUET,
    StructuredDataset,
    StructuredDatasetDecoder,
    StructuredDatasetEncoder,
    StructuredDatasetTransformerEngine,
)

pd = pytest.importorskip("pandas")
pa = pytest.importorskip("pyarrow")
pq = pytest.importorskip("pyarrow.parquet")

PANDAS_PATH = FlyteContextManager.current_context().file_access.get_random_local_directory()
NUMPY_PATH = FlyteContextManager.current_context().file_access.get_random_local_directory()
BQ_PATH = "bq://flyte-dataset:flyte.table"


@dataclass
class MyCols:
    Name: str
    Age: int


my_cols = kwtypes(Name=str, Age=int)
my_dataclass_cols = MyCols
my_dict_cols = {"Name": str, "Age": int}
fields = [("Name", pa.string()), ("Age", pa.int32())]
arrow_schema = pa.schema(fields)
pd_df = pd.DataFrame({"Name": ["Tom", "Joseph"], "Age": [20, 22]})


class MockBQEncodingHandlers(StructuredDatasetEncoder):
    def __init__(self):
        super().__init__(pd.DataFrame, "bq", "")

    def encode(
        self,
        ctx: FlyteContext,
        structured_dataset: StructuredDataset,
        structured_dataset_type: StructuredDatasetType,
    ) -> literals.StructuredDataset:
        return literals.StructuredDataset(
            uri="bq://bucket/key", metadata=StructuredDatasetMetadata(structured_dataset_type)
        )


class MockBQDecodingHandlers(StructuredDatasetDecoder):
    def __init__(self):
        super().__init__(pd.DataFrame, "bq", "")

    def decode(
        self,
        ctx: FlyteContext,
        flyte_value: literals.StructuredDataset,
        current_task_metadata: StructuredDatasetMetadata,
    ) -> pd.DataFrame:
        return pd_df


StructuredDatasetTransformerEngine.register(MockBQEncodingHandlers(), False, True)
StructuredDatasetTransformerEngine.register(MockBQDecodingHandlers(), False, True)


class NumpyRenderer:
    """
    The Polars DataFrame summary statistics are rendered as an HTML table.
    """

    def to_html(self, array: np.ndarray) -> str:
        return pd.DataFrame(array).describe().to_html()


@pytest.fixture(autouse=True)
def numpy_type():
    class NumpyEncodingHandlers(StructuredDatasetEncoder):
        def encode(
            self,
            ctx: FlyteContext,
            structured_dataset: StructuredDataset,
            structured_dataset_type: StructuredDatasetType,
        ) -> literals.StructuredDataset:
            path = typing.cast(str, structured_dataset.uri)
            if not path:
                path = ctx.file_access.join(
                    ctx.file_access.raw_output_prefix,
                    ctx.file_access.get_random_string(),
                )
            df = typing.cast(np.ndarray, structured_dataset.dataframe)
            name = ["col" + str(i) for i in range(len(df))]
            table = pa.Table.from_arrays(df, name)
            local_dir = ctx.file_access.get_random_local_directory()
            local_path = os.path.join(local_dir, f"{0:05}")
            pq.write_table(table, local_path)
            ctx.file_access.upload_directory(local_dir, path)
            structured_dataset_type.format = PARQUET
            return literals.StructuredDataset(uri=path, metadata=StructuredDatasetMetadata(structured_dataset_type))

    class NumpyDecodingHandlers(StructuredDatasetDecoder):
        def decode(
