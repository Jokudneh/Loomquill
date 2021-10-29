import pandas as pd
import vaex
from flytekitplugins.vaex.sd_transformers import VaexDataFrameRenderer
from typing_extensions import Annotated

from flytekit import kwtypes, task, workflow
from flytekit.types.structured.structured_dataset import PARQUET, StructuredDataset

full_schema = Annotated[StructuredDataset, kwtypes(x=int, y=str), PARQUET]
subset_schema = Annotated[StructuredDataset, kwtypes(y=str), PARQUET]
vaex_df = vaex.from_dict(dict(x=[1, 3, 2], y=["a", "b", "c"]))


def test_vaex_workflow_subset():
    @task
    def generate() -> subset_schema:
        return StructuredDataset(dataframe=vaex_df)

    @task
    def consume(df: subset_schema) -> subset_schema:
        subset_df = df.open(vaex.dataframe.DataFrameLocal).all()
        assert subset_df.column_names == ["y"]
        coly = subset_df.y.values.tolist()
        assert coly[0] == "a"
        assert coly[1] == "b"
        assert coly[2] == "c"
        return StructuredDataset(dataframe=subset_df)

    @workflow
    def wf() -> subset_schema:
        return consume(df=generate())

    result = wf()
    assert result is not None


def test_vaex_workflow_full():
