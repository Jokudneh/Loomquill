"""
Unit tests for EMR Serverless Task and configuration.
"""

from unittest.mock import MagicMock

import pytest
from flytekit import task

from flytekitplugins.awsemrserverless import (
    EMRServerless,
    EMRServerlessHiveJobDriver,
    EMRServerlessSparkJobDriver,
    EMRServerlessTask,
)


class TestEMRServerlessSparkJobDriver:
    def test_basic_creation(self):
        driver = EMRServerlessSparkJobDriver(entry_point="s3://bucket/main.py")
        assert driver.entry_point == "s3://bucket/main.py"
        assert driver.entry_point_arguments is None
        assert driver.spark_submit_parameters is None

    def test_full_creation(self):
        driver = EMRServerlessSparkJobDriver(
            entry_point="s3://bucket/main.py",
            entry_point_arguments=["--arg1", "value1"],
            spark_submit_parameters="--conf spark.executor.memory=4g",
        )
        assert driver.entry_point_arguments == ["--arg1", "value1"]

    def test_to_dict_basic(self):
        driver = EMRServerlessSparkJobDriver(entry_point="s3://bucket/main.py")
        assert driver.to_dict() == {"entryPoint": "s3://bucket/main.py"}

    def test_to_dict_full(self):
        driver = EMRServerlessSparkJobDriver(
            entry_point="s3://bucket/main.py",
            entry_point_arguments=["--arg1", "value1"],
            spark_submit_parameters="--conf spark.executor.memory=4g",
        )
        result = driver.to_dict()
        assert result["entryPoint"] == "s3://bucket/main.py"
        assert result["entryPointArguments"] == ["--arg1", "value1"]
        assert result["sparkSubmitParameters"] == "--conf spark.executor.memory=4g"


class TestEMRServerlessHiveJobDriver:
    def test_basic_creation(self):
        driver = EMRServerlessHiveJobDriver(query="SELECT * FROM table")
        assert driver.query == "SELECT * FROM table"
        assert driver.init_query_file is None

    def test_to_dict(self):
        driver = EMRServerlessHiveJobDriver(
            query="s3://bucket/query.sql",
            init_query_file="s3://bucket/init.sql",
        )
        result = driver.to_dict()
        assert result == {
            "query": "s3://bucket/query.sql",
            "initQueryFile": "s3://bucket/init.sql",
        }


class TestEMRServerless:
    def test_basic_spark_config(self):
        config = EMRServerless(
            execution_role_arn="arn:aws:iam::123456789012:role/EMRRole",
