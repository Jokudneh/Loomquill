import enum
import json
import os
import pathlib
import shutil
import sys
import io

import mock
import pytest
import yaml
from click.testing import CliRunner
from flytekit.loggers import logging, logger

from flytekit.clis.sdk_in_container import pyflyte
from flytekit.clis.sdk_in_container.run import (
    RunLevelParams,
    get_entities_in_file,
    run_command, WorkflowCommand,
)
from flytekit.configuration import Config, Image, ImageConfig
from flytekit.core.task import task
from flytekit.image_spec.image_spec import (
    ImageBuildEngine,
    ImageSpec,
)
from flytekit.interaction.click_types import DirParamType, FileParamType
from flytekit.remote import FlyteRemote
from typing import Iterator, List, Optional
from flytekit.types.iterator import JSON
from flytekit import workflow, LaunchPlan

from flytekit.core.context_manager import FlyteContextManager
from flytekit.clients.friendly import SynchronousFlyteClient

pytest.importorskip("pandas")

REMOTE_WORKFLOW_FILE = "https://raw.githubusercontent.com/flyteorg/flytesnacks/8337b64b33df046b2f6e4cba03c74b7bdc0c4fb1/cookbook/core/flyte_basics/basic_workflow.py"
IMPERATIVE_WORKFLOW_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "imperative_wf.py"
)
DIR_NAME = os.path.dirname(os.path.realpath(__file__))

monkeypatch = pytest.MonkeyPatch()


class WorkflowFileLocation(enum.Enum):
    NORMAL = enum.auto()
    TEMP_DIR = enum.auto()


@pytest.fixture(scope="module")
def workflow_file(request, tmp_path_factory):
    normal_workflow_path = pathlib.Path(__file__).parent / "workflow.py"
    if request.param == WorkflowFileLocation.NORMAL:
        return str(normal_workflow_path)
    if request.param == WorkflowFileLocation.TEMP_DIR:
        temp_workflow_path = tmp_path_factory.mktemp("workflows") / "workflow.py"
        if not temp_workflow_path.exists():
            shutil.copy(normal_workflow_path, temp_workflow_path)
        return str(temp_workflow_path)
    raise ValueError("Invalid workflow file location")


@pytest.fixture
def remote():
    with mock.patch("flytekit.clients.friendly.SynchronousFlyteClient") as mock_client:
        flyte_remote = FlyteRemote(
            config=Config.auto(), default_project="p1", default_domain="d1"
        )
        flyte_remote._client = mock_client
        return flyte_remote


@pytest.mark.parametrize(
    "remote_flag",
    [
        "-r",
        "--remote",
    ],
)
@pytest.mark.parametrize(
    "workflow_file",
    [
        WorkflowFileLocation.NORMAL,
        WorkflowFileLocation.TEMP_DIR,
    ],
    indirect=["workflow_file"],
)
def test_pyflyte_run_wf(remote, remote_flag, workflow_file):
    with mock.patch("flytekit.configuration.plugin.FlyteRemote"):
        runner = CliRunner()
        result = runner.invoke(
            pyflyte.main,
            ["run", remote_flag, workflow_file, "my_wf", "--help"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0


@pytest.mark.parametrize("workflow_file", [WorkflowFileLocation.NORMAL], indirect=["workflow_file"])
@pytest.mark.parametrize(
    "interruptible_cli_val,expected_interruptible_override",
    [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
        (None, None),
    ],
)
def test_pyflyte_run_wf_interruptible(workflow_file, interruptible_cli_val, expected_interruptible_override):
    """Tests that the '--interruptible' option passed to 'pyflyte run' is correctly passed to the remote execution."""
    # Build the pyflyte args
    pyflyte_args = [
        "run",
        "--remote",
        str(workflow_file),
        "wf_with_list",
        "--a", "[1,2,3]",
    ]
    # Insert "--interruptible" if interruptible_cli_val is not None
    if interruptible_cli_val is not None:
        pyflyte_args = pyflyte_args[:2] + ["--interruptible", interruptible_cli_val] + pyflyte_args[2:]
    # Run the command - but mock 'FlyteRemote' to check what value 'remote.execute' was called with
    with mock.patch("flytekit.configuration.plugin.FlyteRemote") as mocked_remote:
        runner = CliRunner()
        result = runner.invoke(
            pyflyte.main,
            pyflyte_args,
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.stdout
        # Check that 'remote.execute' was called once with the correct interruptible override
        assert mocked_remote.return_value.execute.call_count == 1
        assert mocked_remote.return_value.execute.call_args[1]["interruptible"] == expected_interruptible_override



def test_pyflyte_run_with_labels():
    workflow_file = pathlib.Path(__file__).parent / "workflow.py"
    with mock.patch("flytekit.configuration.plugin.FlyteRemote"):
        runner = CliRunner()
        result = runner.invoke(
            pyflyte.main,
            ["run", "--remote", str(workflow_file), "my_wf", "--help"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0


def test_imperative_wf():
    runner = CliRunner()
    result = runner.invoke(
        pyflyte.main,
        ["run", IMPERATIVE_WORKFLOW_FILE, "wf", "--in1", "hello", "--in2", "world"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0


def test_copy_all_files():
    runner = CliRunner()
    result = runner.invoke(
        pyflyte.main,
        [
            "run",
            "--copy-all",
            IMPERATIVE_WORKFLOW_FILE,
            "wf",
            "--in1",
            "hello",
            "--in2",
            "world",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0


def test_remote_files():
    runner = CliRunner()
    result = runner.invoke(
        pyflyte.main,
        ["run", REMOTE_WORKFLOW_FILE, "my_wf", "--a", "1", "--b", "Hello"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "workflow_file",
    [
        WorkflowFileLocation.NORMAL,
        WorkflowFileLocation.TEMP_DIR,
    ],
    indirect=["workflow_file"],
)
def test_pyflyte_run_cli(workflow_file):
    runner = CliRunner()
    parquet_file = os.path.join(DIR_NAME, "testdata/df.parquet")
    result = runner.invoke(
        pyflyte.main,
        [
            "run",
            workflow_file,
            "my_wf",
            "--a",
            "1",
            "--b",
            "Hello",
            "--c",
            "1.1",
            "--d",
            '{"i":1,"a":["h","e"]}',
            "--e",
            "[1,2,3]",
            "--f",
            '{"x":1.0, "y":2.0}',
            "--g",
            parquet_file,
            "--i",
            "2020-05-01",
            "--j",
            "20H",
            "--k",
            "RED",
            "--l",
            '{"hello": "world"}',
            "--remote",
            os.path.join(DIR_NAME, "testdata"),
            "--image",
            os.path.join(DIR_NAME, "testdata"),
            "--h",
            "--n",
            json.dumps([{"x": parquet_file}]),
            "--o",
            json.dumps({"x": [parquet_file]}),
            "--p",
            "Any",
            "--q",
            DIR_NAME,
            "--r",
            json.dumps([{"i": 1, "a": ["h", "e"]}]),
            "--s",
            json.dumps({"x": {"i": 1, "a": ["h", "e"]}}),
            "--t",
            json.dumps({"i": [{"i": 1, "a": ["h", "e"]}]}),
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.stdout


@pytest.mark.parametrize(
    "input",
    [
        "1",
        os.path.join(DIR_NAME, "testdata/df.parquet"),
        '{"x":1.0, "y":2.0}',
        "2020-05-01",
        "RED",
    ],
)
def test_union_type1(input):
    runner = CliRunner()
    result = runner.invoke(
        pyflyte.main,
        [
            "run",
            os.path.join(DIR_NAME, "workflow.py"),
            "test_union1",
            "--a",
            input,
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "extra_cli_args, task_name, expected_output",
    [
        (("--a_b",), "test_boolean", True),
        (("--no_a_b",), "test_boolean", False),
        (("--no-a-b",), "test_boolean", False),

        (tuple(), "test_boolean_default_true", True),
        (("--a_b",), "test_boolean_default_true", True),
        (("--no_a_b",), "test_boolean_default_true", False),
        (("--no-a-b",), "test_boolean_default_true", False),

        (tuple(), "test_boolean_default_false", False),
        (("--a_b",), "test_boolean_default_false", True),
        (("--no_a_b",), "test_boolean_default_false", False),
        (("--no-a-b",), "test_boolean_default_false", False),
    ],
)
def test_boolean_type(extra_cli_args, task_name, expected_output):
    runner = CliRunner()
    result = runner.invoke(
        pyflyte.main,
        [
            "run",
            os.path.join(DIR_NAME, "workflow.py"),
            task_name,
            *extra_cli_args,
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert str(expected_output) in result.stdout


def test_all_types_with_json_input():
    runner = CliRunner()
    result = runner.invoke(
        pyflyte.main,
        [
