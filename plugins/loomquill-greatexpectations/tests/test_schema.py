import os
import pathlib
import sqlite3
import typing

import pandas as pd
import pytest

from flytekit.core.type_engine import TypeTransformerFailedError
from flytekitplugins.great_expectations import BatchRequestConfig, GreatExpectationsFlyteConfig, GreatExpectationsType
from great_expectations.exceptions import InvalidBatchRequestError, ValidationError

from flytekit import task, workflow
from flytekit.types.file import CSVFile
from flytekit.types.schema import FlyteSchema

this_dir = pathlib.Path(__file__).resolve().parent
os.chdir(this_dir)


def test_ge_type():
    ge_config = GreatExpectationsFlyteConfig(
        datasource_name="data",
        expectation_suite_name="test.demo",
        data_connector_name="data_example_data_connector",
    )

    s = GreatExpectationsType[str, ge_config]
    assert s.config()[1] == ge_config
    assert s.config()[1].datasource_name == "data"


def test_ge_schema_task():
    ge_config = GreatExpectationsFlyteConfig(
        datasource_name="data",
        expectation_suite_name="test.demo",
        data_connector_name="data_example_data_connector",
    )

    @task
    def get_length(dataframe: pd.DataFrame) -> int:
        return dataframe.shape[0]

    @task
    def my_task(csv_file: GreatExpectationsType[str, ge_config]) -> pd.DataFrame:
        df = pd.read_csv(os.path.join("data", csv_file))
        df.drop(5, axis=0, inplace=True)
        return df

    @workflow
    def valid_wf(dataset: str = "yellow_tripdata_sample_2019-01.csv") -> int:
        dataframe = my_task(csv_file=dataset)
        return get_length(dataframe=dataframe)

    @workflow
    def invalid_wf(dataset: str = "yellow_tripdata_sample_2019-02.csv") -> int:
        dataframe = my_task(csv_file=dataset)
        return get_length(dataframe=dataframe)

    valid_result = valid_wf()
    assert valid_result == 9999

    with pytest.raises(TypeTransformerFailedError):
        invalid_wf()


def test_ge_schema_multiple_args():
    ge_config_one = GreatExpectationsFlyteConfig(
        datasource_name="data",
        expectation_suite_name="test.demo",
        data_connector_name="data_example_data_connector",
    )
    ge_config_two = GreatExpectationsFlyteConfig(
        datasource_name="data",
        expectation_suite_name="test1.demo",
        data_connector_name="data_example_data_connector",
    )

    @task
    def get_file_name(
        dataset_one: GreatExpectationsType[str, ge_config_one], dataset_two: GreatExpectationsType[str, ge_config_two]
    ) -> typing.Tuple[int, int]:
        df_one = pd.read_csv(os.path.join("data", dataset_one))
        df_two = pd.read_csv(os.path.join("data", dataset_two))
        return len(df_one), len(df_two)

    @workflow
    def wf(
        dataset_one: str = "yellow_tripdata_sample_2019-01.csv", dataset_two: str = "yellow_tripdata_sample_2019-02.csv"
    ) -> typing.Tuple[int, int]:
