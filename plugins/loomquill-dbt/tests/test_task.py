import os
import pathlib

import pytest
from flytekitplugins.dbt.error import DBTUnhandledError
from flytekitplugins.dbt.schema import (
    DBTFreshnessInput,
    DBTFreshnessOutput,
    DBTRunInput,
    DBTRunOutput,
    DBTTestInput,
    DBTTestOutput,
)
from flytekitplugins.dbt.task import DBTFreshness, DBTRun, DBTTest

from flytekit import workflow
from flytekit.tools.subprocess import check_call

DBT_PROJECT_DIR = str(pathlib.Path(os.path.dirname(os.path.realpath(__file__)), "testdata", "jaffle_shop"))
DBT_PROFILES_DIR = str(pathlib.Path(os.path.dirname(os.path.realpath(__file__)), "testdata", "profiles"))
DBT_PROFILE = "jaffle_shop"


@pytest.fixture(scope="module", autouse=True)
def prepare_db():
    # Ensure path to sqlite database file exists
    dbs_path = pathlib.Path(DBT_PROJECT_DIR, "dbs")
    dbs_path.mkdir(exist_ok=True, parents=True)
    database_file = pathlib.Path(dbs_path, "database_name.db")
    database_file.touch()

    # Seed the database
    check_call(
        [
            "dbt",
            "--log-format",
            "json",
            "seed",
            "--project-dir",
            DBT_PROJECT_DIR,
            "--profiles-dir",
            DBT_PROFILES_DIR,
