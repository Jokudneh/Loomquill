import os
import pathlib
import sqlite3
import typing

import pandas as pd
import pytest
from flytekitplugins.great_expectations import BatchRequestConfig, GreatExpectationsTask
from flytekitplugins.spark import Spark
from great_expectations.exceptions import InvalidBatchRequestError, ValidationError

import flytekit
from flytekit import kwtypes, task, workflow
from flytekit.types.file import CSVFile, FlyteFile
from flytekit.types.schema import FlyteSchema

this_dir = pathlib.Path(__file__).resolve().parent
os.chdir(this_dir)


def test_ge_simple_task():
    task_object = GreatExpectationsTask(
        name="test1",
        datasource_name="data",
        inputs=kwtypes(dataset=str),
        expectation_suite_name="test.demo",
        data_connector_name="data_example_data_connector",
    )

    # valid data
    result = task_object(dataset="yellow_tripdata_sample_2019-01.csv")

    assert result["success"] is True
    assert result["statistics"]["evaluated_expectations"] == result["statistics"]["successful_expectations"]

    # invalid data
    with pytest.raises(ValidationError):
        invalid_result = task_object(dataset="yellow_tripdata_sample_2019-02.csv")
        assert invalid_result["success"] is False
        assert (
            invalid_result["statistics"]["evaluated_expectations"]
            != invalid_result["statistics"]["successful_expectations"]
        )

    assert task_object.python_interface.inputs == {"dataset": str}


def test_ge_batchrequest_pandas_config():
    task_object = GreatExpectationsTask(
        name="test2",
        datasource_name="data",
        inputs=kwtypes(data=str),
        expectation_suite_name="test.demo",
        data_connector_name="my_data_connector",
        task_config=BatchRequestConfig(
            data_connector_query={
                "batch_filter_parameters": {
                    "year": "2019",
                    "month": "01",
                },
                "limit": 10,
            },
        ),
    )

    # name of the asset -- can be found in great_expectations.yml file
    task_object(data="my_assets")


def test_invalid_ge_batchrequest_pandas_config():
    task_object = GreatExpectationsTask(
        name="test3",
        datasource_name="data",
        inputs=kwtypes(data=str),
        expectation_suite_name="test.demo",
        data_connector_name="my_data_connector",
        task_config=BatchRequestConfig(
            data_connector_query={
                "batch_filter_parameters": {
                    "year": "2020",
                },
            }
        ),
    )

    # Capture IndexError
    with pytest.raises(InvalidBatchRequestError):
        task_object(data="my_assets")


def test_ge_runtimebatchrequest_sqlite_config():
    task_object = GreatExpectationsTask(
        name="test4",
        datasource_name="sqlite_data",
        inputs=kwtypes(dataset=str),
        expectation_suite_name="sqlite.movies",
        data_connector_name="sqlite_data_connector",
        data_asset_name="sqlite_data",
        task_config=BatchRequestConfig(
            batch_identifiers={
                "pipeline_stage": "validation",
            },
        ),
    )

    @workflow
    def runtime_sqlite_wf():
        task_object(dataset="SELECT * FROM movies")

    runtime_sqlite_wf()


def test_ge_runtimebatchrequest_pandas_config():
    task_object = GreatExpectationsTask(
        name="test5",
        datasource_name="my_pandas_datasource",
        inputs=kwtypes(dataset=FlyteSchema),
        expectation_suite_name="test.demo",
        data_connector_name="my_runtime_data_connector",
        data_asset_name="pandas_data",
        task_config=BatchRequestConfig(
            batch_identifiers={
                "pipeline_stage": "validation",
            },
        ),
