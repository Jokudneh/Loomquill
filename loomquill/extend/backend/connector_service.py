import typing
from http import HTTPStatus

import grpc
from flyteidl.admin.agent_pb2 import (
    CreateTaskRequest,
    CreateTaskResponse,
    DeleteTaskRequest,
    DeleteTaskResponse,
    ExecuteTaskSyncRequest,
    ExecuteTaskSyncResponse,
    ExecuteTaskSyncResponseHeader,
    GetAgentRequest,
    GetAgentResponse,
    GetTaskLogsRequest,
    GetTaskLogsResponse,
    GetTaskMetricsRequest,
    GetTaskMetricsResponse,
    GetTaskRequest,
    GetTaskResponse,
    ListAgentsRequest,
    ListAgentsResponse,
)
from flyteidl.service.agent_pb2_grpc import (
    AgentMetadataServiceServicer,
    AsyncAgentServiceServicer,
    SyncAgentServiceServicer,
)
from prometheus_client import Counter, Summary

from flytekit import logger
from flytekit.bin.entrypoint import get_traceback_str
from flytekit.exceptions.system import FlyteConnectorNotFound
from flytekit.extend.backend.base_connector import ConnectorRegistry, SyncConnectorBase, mirror_async_methods
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskExecutionMetadata, TaskTemplate

metric_prefix = "flyte_connector_"
create_operation = "create"
get_operation = "get"
delete_operation = "delete"
do_operation = "do"

# Follow the naming convention. https://prometheus.io/docs/practices/naming/
request_success_count = Counter(
    f"{metric_prefix}requests_success_total",
    "Total number of successful requests",
    ["task_type", "operation"],
)
request_failure_count = Counter(
    f"{metric_prefix}requests_failure_total",
    "Total number of failed requests",
    ["task_type", "operation", "error_code"],
)
request_latency = Summary(
    f"{metric_prefix}request_latency_seconds",
    "Time spent processing connector request",
    ["task_type", "operation"],
)
input_literal_size = Summary(f"{metric_prefix}input_literal_bytes", "Size of input literal", ["task_type"])

