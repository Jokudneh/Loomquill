import typing

import mock
import pytest

from flytekit.core import context_manager
from flytekit.core.base_task import kwtypes
from flytekit.models.literals import StructuredDatasetMetadata
from flytekit.models.types import StructuredDatasetType
from flytekit.types.structured import basic_dfs
from flytekit.types.structured.structured_dataset import (
    StructuredDataset,
    StructuredDatasetDecoder,
    StructuredDatasetEncoder,
    StructuredDatasetTransformerEngine,
)

pd = pytest.importorskip("pandas")
pa = pytest.importorskip("pyarrow")
my_cols = kwtypes(w=typing.Dict[str, typing.Dict[str, int]], x=typing.List[typing.List[int]], y=int, z=str)
fields = [("some_int", pa.int32()), ("some_string", pa.string())]
arrow_schema = pa.schema(fields)


def test_pandas():
    df = pd.DataFrame({"Name": ["Tom", "Joseph"], "Age": [20, 22]})
    encoder = basic_dfs.PandasToParquetEncodingHandler()
    decoder = basic_dfs.ParquetToPandasDecodingHandler()

    ctx = context_manager.FlyteContextManager.current_context()
    sd = StructuredDataset(dataframe=df)
    sd_type = StructuredDatasetType(format="parquet")
