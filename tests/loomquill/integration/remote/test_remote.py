import botocore.session
import shutil
from contextlib import ExitStack, contextmanager
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import tempfile
import time
import typing
import re
import joblib
from urllib.parse import urlparse
import uuid
import pytest
from unittest import mock
import random
import string
from dataclasses import asdict, dataclass

from flytekit import LaunchPlan, kwtypes, WorkflowExecutionPhase, task, workflow
from flytekit.configuration import Config, ImageConfig, SerializationSettings
from flytekit.core.launch_plan import reference_launch_plan
from flytekit.core.task import reference_task
from flytekit.core.workflow import reference_workflow
from flytekit.models import task as task_models
from flytekit.exceptions.user import FlyteAssertion, FlyteEntityNotExistException
from flytekit.extras.sqlite3.task import SQLite3Config, SQLite3Task
from flytekit.remote.remote import FlyteRemote
from flyteidl.service import dataproxy_pb2 as _data_proxy_pb2
from flytekit.types.schema import FlyteSchema
from flytekit.types.structured import StructuredDataset
from flytekit.clients.friendly import SynchronousFlyteClient as _SynchronousFlyteClient
from flytekit.configuration import PlatformConfig

from tests.flytekit.integration.remote.utils import SimpleFileTransfer


MODULE_PATH = pathlib.Path(__file__).parent / "workflows/basic"
CONFIG = os.environ.get("FLYTECTL_CONFIG", str(pathlib.Path.home() / ".flyte" / "config-sandbox.yaml"))
# Run `make build-dev` to build and push the image to the local registry.
IMAGE = os.environ.get("FLYTEKIT_IMAGE", "localhost:30000/flytekit:dev")
PROJECT = "flytesnacks"
DOMAIN = "development"
VERSION = f"v{os.getpid()}"
DEST_DIR = "/tmp"


@pytest.fixture(scope="session")
def register():
    out = subprocess.run(
        [
            "pyflyte",
            "--verbose",
            "-c",
            CONFIG,
            "register",
            "--image",
            IMAGE,
            "--project",
            PROJECT,
            "--domain",
            DOMAIN,
            "--version",
            VERSION,
            MODULE_PATH,
        ]
    )
    assert out.returncode == 0


def run(file_name, wf_name, *args) -> str:
    # Copy the environment and set the environment variable
    out = subprocess.run(
        [
            "pyflyte",
            "--verbose",
            "-c",
            CONFIG,
            "run",
            "--remote",
            "--destination-dir",
            DEST_DIR,
            "--image",
            IMAGE,
            "--project",
            PROJECT,
            "--domain",
            DOMAIN,
            MODULE_PATH / file_name,
            wf_name,
            *args,
        ],
        capture_output=True,  # Capture the output streams
        text=True,  # Return outputs as strings (not bytes)
    )
    assert out.returncode == 0, (f"Command failed with return code {out.returncode}.\n"
                                 f"Standard Output: {out.stdout}\n"
                                 f"Standard Error: {out.stderr}\n")

    match = re.search(r'executions/([a-zA-Z0-9]+)', out.stdout)
    if match:
        execution_id = match.group(1)
        return execution_id

    return "Unknown"


def test_remote_run():
    # child_workflow.parent_wf asynchronously register a parent wf1 with child lp from another wf2.
    run("child_workflow.py", "parent_wf", "--a", "3")

    # run twice to make sure it will register a new version of the workflow.
    run("default_lp.py", "my_wf")


def test_remote_eager_run():
    # child_workflow.parent_wf asynchronously register a parent wf1 with child lp from another wf2.
    run("eager_example.py", "simple_eager_workflow", "--x", "3")


def test_pydantic_default_input_with_map_task():
    execution_id = run("pydantic_wf.py", "wf")
    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)
    execution = remote.fetch_execution(name=execution_id)
    execution = remote.wait(execution=execution, timeout=datetime.timedelta(minutes=5))
    print("Execution Error:", execution.error)
    assert execution.closure.phase == WorkflowExecutionPhase.SUCCEEDED, f"Execution failed with phase: {execution.closure.phase}"


def test_pydantic_default_input_with_map_task():
    execution_id = run("pydantic_wf.py", "wf")
    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)
    execution = remote.fetch_execution(name=execution_id)
    execution = remote.wait(execution=execution, timeout=datetime.timedelta(minutes=5))
    print("Execution Error:", execution.error)
    assert execution.closure.phase == WorkflowExecutionPhase.SUCCEEDED, f"Execution failed with phase: {execution.closure.phase}"


def test_generic_idl_flytetypes():
    os.environ["FLYTE_USE_OLD_DC_FORMAT"] = "true"
    # default inputs for flyte types in dataclass
    execution_id = run("generic_idl_flytetypes.py", "wf")
    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)
    execution = remote.fetch_execution(name=execution_id)
    execution = remote.wait(execution=execution, timeout=datetime.timedelta(minutes=5))
    print("Execution Error:", execution.error)
    assert execution.closure.phase == WorkflowExecutionPhase.SUCCEEDED, f"Execution failed with phase: {execution.closure.phase}"
    os.environ["FLYTE_USE_OLD_DC_FORMAT"] = "false"


def test_msgpack_idl_flytetypes():
    # default inputs for flyte types in dataclass
    execution_id = run("msgpack_idl_flytetypes.py", "wf")
    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)
    execution = remote.fetch_execution(name=execution_id)
    execution = remote.wait(execution=execution, timeout=datetime.timedelta(minutes=5))
    print("Execution Error:", execution.error)
    assert execution.closure.phase == WorkflowExecutionPhase.SUCCEEDED, f"Execution failed with phase: {execution.closure.phase}"


def test_fetch_execute_launch_plan(register):
    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)
    flyte_launch_plan = remote.fetch_launch_plan(name="basic.hello_world.my_wf", version=VERSION)
    execution = remote.execute(flyte_launch_plan, inputs={}, wait=True)
    print("Execution Error:", execution.error)
    assert execution.outputs["o0"] == "hello world"


def test_get_download_artifact_signed_url(register):
    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)
    flyte_launch_plan = remote.fetch_launch_plan(name="basic.basic_workflow.my_wf", version=VERSION)
    execution = remote.execute(flyte_launch_plan, inputs={"a": 10, "b": "foobar"}, wait=True)
    project, domain, name = execution.id.project, execution.id.domain, execution.id.name

    # Fetch the download deck signed URL for the execution
    client = _SynchronousFlyteClient(PlatformConfig.for_endpoint("localhost:30080", True))
    download_link_response = client.get_download_artifact_signed_url(
        node_id="n0",  # Assuming node_id is "n0"
        project=project,
        domain=domain,
        name=name,
        artifact_type=_data_proxy_pb2.ARTIFACT_TYPE_DECK,
    )

    # Check if the signed URL is valid and starts with the expected prefix
    signed_url = download_link_response.signed_url[0]
    assert signed_url.startswith(
        f"http://localhost:30002/my-s3-bucket/metadata/propeller/{project}-{domain}-{name}/n0/data/0/deck.html")


def test_fetch_execute_launch_plan_with_args(register):
    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)
    flyte_launch_plan = remote.fetch_launch_plan(name="basic.basic_workflow.my_wf", version=VERSION)
    execution = remote.execute(flyte_launch_plan, inputs={"a": 10, "b": "foobar"}, wait=True)
    assert execution.node_executions["n0"].inputs == {"a": 10}
    assert execution.node_executions["n0"].outputs == {
        "t1_int_output": 12,
        "c": "world",
    }
    assert execution.node_executions["n1"].inputs == {"a": "world", "b": "foobar"}
    assert execution.node_executions["n1"].outputs == {"o0": "foobarworld"}
    assert execution.node_executions["n0"].task_executions[0].inputs == {"a": 10}
    assert execution.node_executions["n0"].task_executions[0].outputs == {"t1_int_output": 12, "c": "world"}
    assert execution.node_executions["n1"].task_executions[0].inputs == {"a": "world", "b": "foobar"}
    assert execution.node_executions["n1"].task_executions[0].outputs == {"o0": "foobarworld"}
    assert execution.inputs["a"] == 10
    assert execution.inputs["b"] == "foobar"
    assert execution.outputs["o0"] == 12
    assert execution.outputs["o1"] == "foobarworld"


def test_monitor_workflow_execution(register):
    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)
    flyte_launch_plan = remote.fetch_launch_plan(name="basic.hello_world.my_wf", version=VERSION)
    execution = remote.execute(
        flyte_launch_plan,
        inputs={},
    )

    poll_interval = datetime.timedelta(seconds=1)
    time_to_give_up = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=60)

    execution = remote.sync_execution(execution, sync_nodes=True)
    while datetime.datetime.now(datetime.timezone.utc) < time_to_give_up:
        if execution.is_done:
            break

        with pytest.raises(
                FlyteAssertion, match="Please wait until the execution has completed before requesting the outputs.",
        ):
            execution.outputs

        time.sleep(poll_interval.total_seconds())
        execution = remote.sync_execution(execution, sync_nodes=True)

        if execution.node_executions:
            assert execution.node_executions["start-node"].closure.phase == 3  # SUCCEEDED

    for key in execution.node_executions:
        assert execution.node_executions[key].closure.phase == 3

    assert execution.node_executions["n0"].inputs == {}
    assert execution.node_executions["n0"].outputs["o0"] == "hello world"
    assert execution.node_executions["n0"].task_executions[0].inputs == {}
    assert execution.node_executions["n0"].task_executions[0].outputs["o0"] == "hello world"
    assert execution.inputs == {}
    assert execution.outputs["o0"] == "hello world"


def test_sync_execution_sync_nodes_get_all_executions(register):
    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)
    flyte_launch_plan = remote.fetch_launch_plan(name="basic.deep_child_workflow.parent_wf", version=VERSION)
    execution = remote.execute(
        flyte_launch_plan,
        inputs={"a": 3},
    )

    poll_interval = datetime.timedelta(seconds=1)
    time_to_give_up = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=600)

    execution = remote.sync_execution(execution, sync_nodes=True)
    while datetime.datetime.now(datetime.timezone.utc) < time_to_give_up:
        if execution.is_done:
            break

        with pytest.raises(
                FlyteAssertion, match="Please wait until the execution has completed before requesting the outputs.",
        ):
            execution.outputs

        time.sleep(poll_interval.total_seconds())
        execution = remote.sync_execution(execution, sync_nodes=True)

        if execution.node_executions:
            assert execution.node_executions["start-node"].closure.phase == 3  # SUCCEEDED

    for key in execution.node_executions:
        assert execution.node_executions[key].closure.phase == 3

    # check node execution getting correct number of nested workflows and executions
    assert len(execution.node_executions) == 5
    execution_n0 = execution.node_executions["n0"]
    execution_n1 = execution.node_executions["n1"]
    assert len(execution_n1.workflow_executions[0].node_executions) == 4
    execution_n1_n0 = execution_n1.workflow_executions[0].node_executions["n0"]
    assert len(execution_n1_n0.workflow_executions[0].node_executions) == 3
    execution_n1_n0_n0 = execution_n1_n0.workflow_executions[0].node_executions["n0"]

    # check inputs and outputs each node execution
    assert execution_n0.inputs == {"a": 3}
    assert execution_n0.outputs["o0"] == 6
    assert execution_n1.inputs == {"a": 6}
    assert execution_n1_n0.inputs == {"a": 6}
    assert execution_n1_n0_n0.inputs == {"a": 6}
    assert execution_n1_n0_n0.outputs["o0"] == 12



def test_fetch_execute_launch_plan_with_subworkflows(register):
    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)

    flyte_launch_plan = remote.fetch_launch_plan(name="basic.subworkflows.parent_wf", version=VERSION)
    execution = remote.execute(flyte_launch_plan, inputs={"a": 101}, wait=True)
    # check node execution inputs and outputs
    assert execution.node_executions["n0"].inputs == {"a": 101}
    assert execution.node_executions["n0"].outputs == {"t1_int_output": 103, "c": "world"}
    assert execution.node_executions["n1"].inputs == {"a": 103}
    assert execution.node_executions["n1"].outputs == {"o0": "world", "o1": "world"}

    # check subworkflow task execution inputs and outputs
    subworkflow_node_executions = execution.node_executions["n1"].subworkflow_node_executions
    subworkflow_node_executions["n1-0-n0"].inputs == {"a": 103}
    subworkflow_node_executions["n1-0-n1"].outputs == {"t1_int_output": 107, "c": "world"}


def test_fetch_execute_launch_plan_with_child_workflows(register):
    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)

    flyte_launch_plan = remote.fetch_launch_plan(name="basic.child_workflow.parent_wf", version=VERSION)
    execution = remote.execute(flyte_launch_plan, inputs={"a": 3}, wait=True)

    # check node execution inputs and outputs
    assert execution.node_executions["n0"].inputs == {"a": 3}
    assert execution.node_executions["n0"].outputs["o0"] == 6
    assert execution.node_executions["n1"].inputs == {"a": 6}
    assert execution.node_executions["n1"].outputs["o0"] == 12
    assert execution.node_executions["n2"].inputs == {"a": 6, "b": 12}
    assert execution.node_executions["n2"].outputs["o0"] == 18


def test_fetch_execute_workflow(register):
    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)
    flyte_workflow = remote.fetch_workflow(name="basic.hello_world.my_wf", version=VERSION)
    execution = remote.execute(flyte_workflow, inputs={}, wait=True)
    assert execution.outputs["o0"] == "hello world"
    assert isinstance(execution.closure.duration, datetime.timedelta)
    assert execution.closure.duration > datetime.timedelta(seconds=1)

    execution_to_terminate = remote.execute(flyte_workflow, {})
    remote.terminate(execution_to_terminate, cause="just because")


def test_fetch_execute_task(register):
    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)
    flyte_task = remote.fetch_task(name="basic.basic_workflow.t1", version=VERSION)
    execution = remote.execute(flyte_task, inputs={"a": 10}, wait=True)
    assert execution.outputs["t1_int_output"] == 12
    assert execution.outputs["c"] == "world"
    assert execution.inputs["a"] == 10
    assert execution.outputs["c"] == "world"


def test_execute_python_task(register):
    """Test execution of a @task-decorated python function that is already registered."""
    from workflows.basic.basic_workflow import t1

    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)
    execution = remote.execute(
        t1,
        name="basic.basic_workflow.t1",
        inputs={"a": 10},
        version=VERSION,
        wait=True,
        overwrite_cache=True,
        envs={"foo": "bar"},
        tags=["flyte"],
        cluster_pool="gpu",
    )
    assert execution.outputs["t1_int_output"] == 12
    assert execution.outputs["c"] == "world"
    assert execution.spec.envs.envs == {"foo": "bar"}
    assert execution.spec.tags == ["flyte"]
    assert execution.spec.cluster_assignment.cluster_pool == "gpu"


def test_execute_python_workflow_and_launch_plan(register):
    """Test execution of a @workflow-decorated python function and launchplan that are already registered."""
    from workflows.basic.basic_workflow import my_wf

    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)
    execution = remote.execute(
        my_wf, name="basic.basic_workflow.my_wf", inputs={"a": 10, "b": "xyz"}, version=VERSION, wait=True
    )
    assert execution.outputs["o0"] == 12
    assert execution.outputs["o1"] == "xyzworld"

    launch_plan = LaunchPlan.get_or_create(workflow=my_wf, name=my_wf.name)
    execution = remote.execute(
        launch_plan,
        name="basic.basic_workflow.my_wf",
        inputs={"a": 14, "b": "foobar"},
        version=VERSION,
        wait=True,
    )
    assert execution.outputs["o0"] == 16
    assert execution.outputs["o1"] == "foobarworld"

    flyte_workflow_execution = remote.fetch_execution(name=execution.id.name)
    assert execution.inputs == flyte_workflow_execution.inputs
    assert execution.outputs == flyte_workflow_execution.outputs


def test_fetch_execute_launch_plan_list_of_floats(register):
    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)
    flyte_launch_plan = remote.fetch_launch_plan(name="basic.list_float_wf.my_wf", version=VERSION)
    xs: typing.List[float] = [42.24, 999.1, 0.0001]
    execution = remote.execute(flyte_launch_plan, inputs={"xs": xs}, wait=True)
    assert execution.outputs["o0"] == "[42.24, 999.1, 0.0001]"


def test_fetch_execute_task_list_of_floats(register):
    remote = FlyteRemote(Config.auto(config_file=CONFIG), PROJECT, DOMAIN)
    flyte_task = remote.fetch_task(name="basic.list_float_wf.concat_list", version=VERSION)
    xs: typing.List[float] = [0.1, 0.2, 0.3, 0.4, -99999.7]
