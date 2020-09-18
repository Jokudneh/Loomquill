import typing
from collections import OrderedDict
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import grpc
import pytest
from flyteidl.admin.agent_pb2 import (
    Agent,
    CreateRequestHeader,
    CreateTaskRequest,
    DeleteTaskRequest,
    ExecuteTaskSyncRequest,
    GetAgentRequest,
    GetTaskRequest,
    ListAgentsRequest,
    ListAgentsResponse,
    TaskCategory, DeleteTaskResponse, GetTaskLogsResponse, GetTaskLogsResponseBody, GetTaskMetricsResponse,
    GetTaskMetricsRequest, GetTaskLogsRequest,
)
from flyteidl.core.execution_pb2 import TaskExecution, TaskLog
from flyteidl.core.identifier_pb2 import ResourceType
from flyteidl.core.metrics_pb2 import ExecutionMetricResult

from flytekit import PythonFunctionTask, task
from flytekit.configuration import (
    FastSerializationSettings,
    Image,
    ImageConfig,
    SerializationSettings,
)
from flytekit.core.base_task import PythonTask, kwtypes
from flytekit.core.interface import Interface
from flytekit.exceptions.system import FlyteConnectorNotFound
from flytekit.extend.backend.connector_service import (
    ConnectorMetadataService,
    AsyncConnectorService,
    SyncConnectorService,
)
from flytekit.extend.backend.base_connector import (
    ConnectorRegistry,
    AsyncConnectorBase,
    AsyncConnectorExecutorMixin,
    Resource,
    ResourceMeta,
    SyncConnectorBase,
    SyncConnectorExecutorMixin,
    is_terminal_phase,
    render_task_template,
)
from flytekit.extend.backend.utils import convert_to_flyte_phase, get_agent_secret, get_connector_secret
from flytekit.models import literals
from flytekit.models.core.identifier import (
    Identifier,
    NodeExecutionIdentifier,
    TaskExecutionIdentifier,
    WorkflowExecutionIdentifier,
)
from flytekit.models.literals import LiteralMap
from flytekit.models.security import Identity
from flytekit.models.task import TaskExecutionMetadata, TaskTemplate
from flytekit.tools.translator import get_serializable
from flytekit.utils.asyn import loop_manager

dummy_id = "dummy_id"


@dataclass
class DummyMetadata(ResourceMeta):
    job_id: str
    output_path: typing.Optional[str] = None
    task_name: typing.Optional[str] = None


class DummyConnector(AsyncConnectorBase):
    name = "Dummy Connector"

    def __init__(self):
        super().__init__(task_type_name="dummy", metadata_type=DummyMetadata)

    def create(self, task_template: TaskTemplate, inputs: typing.Optional[LiteralMap], **kwargs) -> DummyMetadata:
        return DummyMetadata(job_id=dummy_id)

    def get(self, resource_meta: DummyMetadata, **kwargs) -> Resource:
        return Resource(
            phase=TaskExecution.SUCCEEDED,
            log_links=[TaskLog(name="console", uri="localhost:3000")],
            custom_info={"custom": "info", "num": 1},
        )

    def delete(self, resource_meta: DummyMetadata, **kwargs):
        ...


class AsyncDummyConnector(AsyncConnectorBase):
    name = "Async Dummy Connector"

    def __init__(self):
        super().__init__(task_type_name="async_dummy", metadata_type=DummyMetadata)

    async def create(
        self,
        task_template: TaskTemplate,
        inputs: typing.Optional[LiteralMap] = None,
        output_prefix: typing.Optional[str] = None,
        task_execution_metadata: typing.Optional[TaskExecutionMetadata] = None,
        **kwargs,
    ) -> DummyMetadata:
        output_path = f"{output_prefix}/{dummy_id}" if output_prefix else None
        task_name = task_execution_metadata.task_execution_id.task_id.name if task_execution_metadata else "default"
        return DummyMetadata(job_id=dummy_id, output_path=output_path, task_name=task_name)

    async def get(self, resource_meta: DummyMetadata, **kwargs) -> Resource:
        return Resource(
            phase=TaskExecution.SUCCEEDED,
            log_links=[TaskLog(name="console", uri="localhost:3000")],
            custom_info={"custom": "info", "num": 1},
        )

    async def delete(self, resource_meta: DummyMetadata, **kwargs):
        ...

    async def get_metrics(self, resource_meta: DummyMetadata, **kwargs) -> GetTaskMetricsResponse:
        return GetTaskMetricsResponse(results=[ExecutionMetricResult(metric="EXECUTION_METRIC_LIMIT_MEMORY_BYTES", data=None)])

    async def get_logs(self, resource_meta: DummyMetadata, **kwargs) -> GetTaskLogsResponse:
        return GetTaskLogsResponse(body=GetTaskLogsResponseBody(results=["foo", "bar"]))


class MockOpenAIConnector(SyncConnectorBase):
    name = "mock openAI Connector"

    def __init__(self):
        super().__init__(task_type_name="openai")

    def do(
        self,
        task_template: TaskTemplate,
        inputs: typing.Optional[LiteralMap] = None,
        **kwargs,
    ) -> Resource:
        assert inputs.literals["a"].scalar.primitive.integer == 1
        return Resource(phase=TaskExecution.SUCCEEDED, outputs={"o0": 1})


class MockAsyncOpenAIConnector(SyncConnectorBase):
    name = "mock async openAI Connector"

    def __init__(self):
        super().__init__(task_type_name="async_openai")

    async def do(self, task_template: TaskTemplate, inputs: LiteralMap = None, **kwargs) -> Resource:
        assert inputs.literals["a"].scalar.primitive.integer == 1
        return Resource(phase=TaskExecution.SUCCEEDED, outputs={"o0": 1})


def get_task_template(task_type: str) -> TaskTemplate:
    @task
    def simple_task(i: int):
        print(i)

    default_img = Image(name="default", fqn="test", tag="tag")
    serialization_settings = SerializationSettings(
