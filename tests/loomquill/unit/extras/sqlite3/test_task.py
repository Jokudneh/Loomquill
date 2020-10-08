import os
import sys

import pytest

from flytekit import kwtypes, task, workflow
from flytekit.configuration import DefaultImages
from flytekit.core import context_manager
from flytekit.extras.sqlite3.task import SQLite3Config, SQLite3Task

# https://www.sqlitetutorial.net/sqlite-sample-database/
from flytekit.types.schema import FlyteSchema

ctx = context_manager.FlyteContextManager.current_context()
EXAMPLE_DB = os.path.join(os.path.dirname(os.path.realpath(__file__)), "chinook.zip")

# This task belongs to test_task_static but is intentionally here to help test tracking
tk = SQLite3Task(
    "test",
    query_template="select * from tracks",
    task_config=SQLite3Config(
        uri=EXAMPLE_DB,
        compressed=True,
    ),
)


@pytest.mark.skipif("pandas" not in sys.modules, reason="Pandas is not installed.")
def test_task_static():
    assert tk.output_columns is None

    df = tk()
    assert df is not None

