import tempfile

import pandas as pd
import polars as pl
import pytest
from flytekitplugins.polars.sd_transformers import PolarsDataFrameRenderer
from typing_extensions import Annotated
import numpy as np
from polars.testing import assert_frame_equal

from flytekit import kwtypes, task, workflow
from flytekit.types.structured.structured_dataset import PARQUET, StructuredDataset

subset_schema = Annotated[StructuredDataset, kwtypes(col2=str), PARQUET]
full_schema = Annotated[StructuredDataset, PARQUET]

polars_version = pl.__version__


@pytest.mark.parametrize("df_cls", [pl.DataFrame, pl.LazyFrame])
def test_polars_workflow_subset(df_cls):
    @task
    def generate() -> subset_schema:
        df = df_cls({"col1": [1, 3, 2], "col2": list("abc")})
        return StructuredDataset(dataframe=df)

    @task
