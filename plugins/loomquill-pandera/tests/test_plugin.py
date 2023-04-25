import typing

import pandas
import pandera
import pytest
from pandera.typing.pandas import DataFrame, Series

from flytekit import current_context, task, workflow
from flytekitplugins.pandera import ValidationConfig, PandasReportRenderer


def test_pandera_dataframe_type_hints():
    class InSchema(pandera.DataFrameModel):
        col1: int
        col2: float

    class IntermediateSchema(InSchema):
        col3: float

        @pandera.dataframe_check
        @classmethod
        def col3_check(cls, df: DataFrame) -> Series[bool]:
            return df["col3"] == df["col1"] * df["col2"]

    class OutSchema(IntermediateSchema):
        col4: str

    @task
    def transform1(df: DataFrame[InSchema]) -> DataFrame[IntermediateSchema]:
        return df.assign(col3=df["col1"] * df["col2"])

    @task
    def transform2(df: DataFrame[IntermediateSchema]) -> DataFrame[OutSchema]:
        return df.assign(col4="foo")

    valid_df = pandas.DataFrame({"col1": [1, 2, 3], "col2": [10.0, 11.0, 12.0]})

    @workflow
    def my_wf() -> DataFrame[OutSchema]:
        return transform2(df=transform1(df=valid_df))
