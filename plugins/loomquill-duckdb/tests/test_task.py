import json
from typing import List
import pytest
import pandas as pd
import pyarrow as pa
from flytekitplugins.duckdb import DuckDBQuery, DuckDBProvider
from flytekitplugins.duckdb.task import MissingSecretError
from typing_extensions import Annotated

from flytekit import kwtypes, task, workflow, Secret
from flytekit.types.structured.structured_dataset import StructuredDataset


def test_simple():
    simple_duckdb_query = DuckDBQuery(
        name="duckdb_task", query="SELECT SUM(a) FROM mydf", inputs=kwtypes(mydf=pd.DataFrame)
    )

    @workflow
    def pandas_wf(mydf: pd.DataFrame) -> pd.DataFrame:
        return simple_duckdb_query(mydf=mydf)

    @workflow
    def arrow_wf(mydf: pd.DataFrame) -> pa.Table:
        return simple_duckdb_query(mydf=mydf)

    df = pd.DataFrame({"a": [1, 2, 3]})
    assert isinstance(pandas_wf(mydf=df), pd.DataFrame)
    assert isinstance(arrow_wf(mydf=df), pa.Table)


def test_parquet():
    parquet_duckdb_query = DuckDBQuery(
        name="read_parquet",
        query=[
            "INSTALL httpfs",
            "LOAD httpfs",
            """SELECT hour(lpep_pickup_datetime) AS hour, count(*) AS count FROM READ_PARQUET(?) GROUP BY hour""",
        ],
        inputs=kwtypes(params=List[str]),
    )
