import datetime
import os
import sys
import tempfile
import typing
from dataclasses import dataclass

import pytest
from dataclasses_json import DataClassJsonMixin

import flytekit
from flytekit import kwtypes
from flytekit.exceptions.user import FlyteRecoverableException
from flytekit.extras.tasks.shell import (
    OutputLocation,
    RawShellTask,
    ShellTask,
    get_raw_shell_task,
    subproc_execute,
)
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import CSVFile, FlyteFile

test_file_path = os.path.dirname(os.path.realpath(__file__))
testdata = os.path.join(test_file_path, "testdata")
test_csv = os.path.join(testdata, "test.csv")
if os.name == "nt":
    script_sh = os.path.join(testdata, "script.exe")
    script_sh_2 = None
else:
    script_sh = os.path.join(testdata, "script.sh")
    script_sh_2 = os.path.join(testdata, "script_args_env.sh")


def test_shell_task_access_to_result():
    t = ShellTask(
        name="test",
        script="""
        echo "Hello World!"
        """,
        shell="/bin/bash",
    )
    t()

    assert t.result.returncode == 0
    assert "Hello World!" in t.result.output  # ShellTask strips carriage returns
    assert t.result.error == ""


def test_shell_task_no_io():
    t = ShellTask(
        name="test",
        script="""
        echo "Hello World!"
        """,
        shell="/bin/bash",
    )

    t()


def test_shell_task_fail():
    t = ShellTask(
        name="test",
        script="""
            non-existent blah
            """,
    )

    with pytest.raises(Exception):
        t()


def test_input_substitution_primitive():
    t = ShellTask(
        name="test",
        script="""
            set -ex
            cat {inputs.f}
            echo "Hello World {inputs.y} on  {inputs.j}"
            """,
        inputs=kwtypes(f=str, y=int, j=datetime.datetime),
    )

    if os.name == "nt":
        t._script = t._script.replace("set -ex", "").replace("cat", "type")

    t(
        f=os.path.join(test_file_path, "__init__.py"),
        y=5,
        j=datetime.datetime(2021, 11, 10, 12, 15, 0),
    )
    t(
        f=os.path.join(test_file_path, "test_shell.py"),
        y=5,
        j=datetime.datetime(2021, 11, 10, 12, 15, 0),
    )
    with pytest.raises(FlyteRecoverableException):
        t(f="non_exist.py", y=5, j=datetime.datetime(2021, 11, 10, 12, 15, 0))


def test_input_substitution_files():
    t = ShellTask(
        name="test",
        script="""
            cat {inputs.f}
