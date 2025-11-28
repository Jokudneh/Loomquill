import asyncio
import inspect
import json
import sys
import time
import typing
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import asdict, dataclass
from functools import partial
from types import FrameType
from typing import Any, Dict, List, Optional, Union

from flyteidl.admin.agent_pb2 import Agent, GetTaskLogsResponse, GetTaskMetricsResponse
from flyteidl.admin.agent_pb2 import Resource as _Resource
from flyteidl.admin.agent_pb2 import TaskCategory as _TaskCategory
from flyteidl.core import literals_pb2
from flyteidl.core.execution_pb2 import TaskExecution, TaskLog
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct
from rich.logging import RichHandler
from rich.progress import Progress

from flytekit import FlyteContext, PythonFunctionTask, logger
from flytekit.configuration import ImageConfig, SerializationSettings
from flytekit.core import utils
from flytekit.core.base_task import PythonTask
from flytekit.core.context_manager import ExecutionState, FlyteContextManager
from flytekit.core.type_engine import TypeEngine, dataclass_from_dict
from flytekit.exceptions.system import FlyteConnectorNotFound
from flytekit.exceptions.user import FlyteUserException
from flytekit.extend.backend.utils import is_terminal_phase, mirror_async_methods, render_task_template
from flytekit.loggers import set_flytekit_log_properties
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskExecutionMetadata, TaskTemplate

# It's used to force connector to run in the same event loop in the local execution.
local_connector_loop = asyncio.new_event_loop()


class TaskCategory:
    def __init__(self, name: str, version: int = 0):
        self._name = name
        self._version = version

    def __hash__(self):
        return hash((self._name, self._version))

    def __eq__(self, other: "TaskCategory"):
        return self._name == other._name and self._version == other._version

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> int:
        return self._version

    def __str__(self):
        return f"{self._name}_v{self._version}"


@dataclass
class ResourceMeta:
    """
    This is the metadata for the job. For example, the id of the job.
    """

    def encode(self) -> bytes:
        """
        Encode the resource meta to bytes.
        """
        return json.dumps(asdict(self)).encode("utf-8")

    @classmethod
    def decode(cls, data: bytes) -> "ResourceMeta":
        """
        Decode the resource meta from bytes.
        """
        return dataclass_from_dict(cls, json.loads(data.decode("utf-8")))


@dataclass
class Resource:
    """
    This is the output resource of the job.

    Attributes
    ----------
        phase : TaskExecution.Phase
            The phase of the job.
        message : Optional[str]
            The return message from the job.
        log_links : Optional[List[TaskLog]]
            The log links of the job. For example, the link to the BigQuery Console.
        outputs : Optional[Union[LiteralMap, typing.Dict[str, Any]]]
            The outputs of the job. If return python native types, the agent will convert them to flyte literals.
        custom_info : Optional[typing.Dict[str, Any]]
            The custom info of the job. For example, the job config.
    """
