import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import typing
import uuid
from collections import OrderedDict
from datetime import datetime, timedelta
from functools import partial

import mock
import pytest
from flyteidl.core import compiler_pb2 as _compiler_pb2
from flyteidl.service import dataproxy_pb2
from mock import ANY, MagicMock, patch

import flytekit.configuration
from flytekit import CronSchedule, ImageSpec, LaunchPlan, WorkflowFailurePolicy, task, workflow, reference_task, map_task, dynamic, eager
from flytekit.clients.grpc_utils.deadline_interceptor import scoped_grpc_deadline
from flytekit.configuration import Config, DefaultImages, Image, ImageConfig, SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.type_engine import TypeEngine
from flytekit.exceptions import user as user_exceptions
from flytekit.exceptions.user import FlyteEntityNotExistException, FlyteAssertion
from flytekit.models import common as common_models
from flytekit.models import security
from flytekit.models.admin.workflow import Workflow, WorkflowClosure
from flytekit.models.core import condition as _condition
from flytekit.models.core import workflow as _workflow
from flytekit.models.core.compiler import CompiledWorkflowClosure
from flytekit.models.core.identifier import Identifier, ResourceType, WorkflowExecutionIdentifier
from flytekit.models.execution import Execution
from flytekit.models.task import Task
from flytekit.remote import FlyteTask, FlyteWorkflow, FlyteWorkflowExecution
from flytekit.remote.lazy_entity import LazyEntity
from flytekit.remote.remote import FlyteRemote, _get_git_repo_url, _get_pickled_target_dict
from flytekit.tools.translator import Options, get_serializable, get_serializable_launch_plan
from tests.flytekit.common.parameterizers import LIST_OF_TASK_CLOSURES

CLIENT_METHODS = {
    ResourceType.WORKFLOW: "list_workflows_paginated",
    ResourceType.TASK: "list_tasks_paginated",
    ResourceType.LAUNCH_PLAN: "list_launch_plans_paginated",
}

REMOTE_METHODS = {
    ResourceType.WORKFLOW: "fetch_workflow",
    ResourceType.TASK: "fetch_task",
    ResourceType.LAUNCH_PLAN: "fetch_launch_plan",
}

ENTITY_TYPE_TEXT = {
    ResourceType.WORKFLOW: "Workflow",
    ResourceType.TASK: "Task",
    ResourceType.LAUNCH_PLAN: "Launch Plan",
}

obj = _workflow.Node(
    id="some:node:id",
    metadata="1",
    inputs=[],
    upstream_node_ids=[],
    output_aliases=[],
    workflow_node=_workflow.WorkflowNode(launchplan_ref="LAUNCH_PLAN"),
)
node1 = _workflow.Node(
    id="some:node:id",
    metadata="1",
    inputs=[],
    upstream_node_ids=[],
    output_aliases=[],
    branch_node=_workflow.BranchNode(
        _workflow.IfElseBlock(
            case=_workflow.IfBlock(
                condition=_condition.BooleanExpression(),
                then_node=obj,
            )
        )
    ),
)
nodes = [node1]

obj2 = _workflow.Node(id="some:node:id", metadata="1", inputs=[], upstream_node_ids=[], output_aliases=[])

node2 = node1 = _workflow.Node(
    id="some:node:id",
    metadata="1",
    inputs=[],
    upstream_node_ids=[],
    output_aliases=[],
    branch_node=_workflow.BranchNode(
        _workflow.IfElseBlock(
            case=_workflow.IfBlock(
                condition=_condition.BooleanExpression(),
                then_node=obj2,
            ),
            else_node=node1,
        )
    ),
)
nodes2 = [node2]


@pytest.fixture
def remote():
    with patch("flytekit.clients.friendly.SynchronousFlyteClient") as mock_client:
        flyte_remote = FlyteRemote(config=Config.auto(), default_project="p1", default_domain="d1")
        flyte_remote._client_initialized = True
        flyte_remote._client = mock_client
        return flyte_remote


def test_remote_fetch_execution(remote):
    admin_workflow_execution = Execution(
        id=WorkflowExecutionIdentifier("p1", "d1", "n1"),
        spec=MagicMock(),
        closure=MagicMock(),
    )
    mock_client = MagicMock()
    mock_client.get_execution.return_value = admin_workflow_execution
    mock_client.get_workflow.return_value.closure.compiled_workflow.primary.template.failure_node = None
    remote._client = mock_client
    flyte_workflow_execution = remote.fetch_execution(name="n1")
    assert flyte_workflow_execution.id == admin_workflow_execution.id


def test_sync_execution_sets_default_rpc_deadline(remote):
    execution = MagicMock()
    with patch.object(remote, "_sync_execution", return_value=execution) as mock_sync:
        with patch("flytekit.remote.remote.scoped_grpc_deadline") as mock_deadline:
            assert remote.sync_execution(execution) is execution

    mock_deadline.assert_called_once_with(60.0)
    mock_sync.assert_called_once_with(execution, sync_nodes=False)


def test_sync_execution_accepts_rpc_deadline_override(remote):
    execution = MagicMock()
    with patch.object(remote, "_sync_execution", return_value=execution):
        with patch("flytekit.remote.remote.scoped_grpc_deadline") as mock_deadline:
            assert remote.sync_execution(execution, rpc_timeout=5) is execution

    mock_deadline.assert_called_once_with(5.0)


def test_sync_execution_does_not_override_active_rpc_deadline(remote):
    execution = MagicMock()
    with patch.object(remote, "_sync_execution", return_value=execution):
        with patch("flytekit.remote.remote.scoped_grpc_deadline") as mock_deadline:
            with scoped_grpc_deadline(5):
                assert remote.sync_execution(execution, rpc_timeout=30) is execution

    mock_deadline.assert_not_called()


@pytest.fixture
def mock_wf_exec():
    return patch("flytekit.remote.executions.FlyteWorkflowExecution.promote_from_model")


def test_underscore_execute_uses_launch_plan_attributes(remote, mock_wf_exec):
    mock_wf_exec.return_value = True
    mock_client = MagicMock()
    remote._client = mock_client

    def local_assertions(*args, **kwargs):
        execution_spec = args[3]
        assert execution_spec.security_context.run_as.k8s_service_account == "svc"
        assert execution_spec.labels == common_models.Labels({"a": "my_label_value"})
        assert execution_spec.annotations == common_models.Annotations({"b": "my_annotation_value"})

    mock_client.create_execution.side_effect = local_assertions

    mock_entity = MagicMock()
    options = Options(
        labels=common_models.Labels({"a": "my_label_value"}),
        annotations=common_models.Annotations({"b": "my_annotation_value"}),
        security_context=security.SecurityContext(run_as=security.Identity(k8s_service_account="svc")),
    )

    remote._execute(
        mock_entity,
        inputs={},
        project="proj",
        domain="dev",
        options=options,
    )


def test_execution_cluster_label_attributes(remote, mock_wf_exec):
    mock_wf_exec.return_value = True
    mock_client = MagicMock()
    remote._client = mock_client

    def local_assertions(*args, **kwargs):
        execution_spec = args[3]
        assert execution_spec.execution_cluster_label.value == "label"

    mock_client.create_execution.side_effect = local_assertions

    mock_entity = MagicMock()

    remote._execute(
        mock_entity,
        inputs={},
        project="proj",
        domain="dev",
        execution_cluster_label="label",
    )


def test_underscore_execute_fall_back_remote_attributes(remote, mock_wf_exec):
    mock_wf_exec.return_value = True
    mock_client = MagicMock()
    remote._client = mock_client

    options = Options(
        raw_output_data_config=common_models.RawOutputDataConfig(output_location_prefix="raw_output"),
        security_context=security.SecurityContext(run_as=security.Identity(iam_role="iam:some:role")),
    )

    def local_assertions(*args, **kwargs):
        execution_spec = args[3]
        assert execution_spec.security_context.run_as.iam_role == "iam:some:role"
        assert execution_spec.raw_output_data_config.output_location_prefix == "raw_output"

    mock_client.create_execution.side_effect = local_assertions

    mock_entity = MagicMock()

    remote._execute(
        mock_entity,
        inputs={},
        project="proj",
        domain="dev",
        options=options,
    )


def test_execute_with_wrong_input_key(remote: FlyteRemote, mock_wf_exec):
    # mock_url.get.return_value = "localhost"
    # mock_insecure.get.return_value = True
    mock_wf_exec.return_value = True
    mock_client = MagicMock()
    remote._client = mock_client

    mock_entity = MagicMock()
    mock_entity.interface.inputs = {"foo": int}

    with pytest.raises(user_exceptions.FlyteValueException):
        remote._execute(
            mock_entity,
            inputs={"bar": 3},
            project="proj",
            domain="dev",
        )


def test_execute_with_no_inputs(remote: FlyteRemote, mock_wf_exec):
    mock_wf_exec.return_value = True
    mock_client = MagicMock()
    remote._client = mock_client

    mock_entity = MagicMock()
    out = remote._execute(mock_entity, project="proj", domain="dev")
    assert isinstance(out, FlyteWorkflowExecution)


def test_form_config():
    remote = FlyteRemote(config=Config.auto(), default_project="p1", default_domain="d1")
    assert remote.default_project == "p1"
    assert remote.default_domain == "d1"


@patch("flytekit.remote.remote.SynchronousFlyteClient")
def test_passing_of_kwargs(mock_client):
    additional_args = {
        "credentials": 1,
        "options": 2,
        "private_key": 3,
        "compression": 4,
        "root_certificates": 5,
        "certificate_chain": 6,
    }
    FlyteRemote(config=Config.auto(), default_project="project", default_domain="domain", **additional_args).client
    assert mock_client.called
    assert mock_client.call_args[1] == additional_args


