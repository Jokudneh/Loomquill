"""
# flytekit.core.base_task

This module provides the core task-related functionality in Flytekit.

## Core Components

### kwtypes
Utility for creating keyword type annotations for tasks.

### PythonTask
Base class for Python-based task implementations.

### Task
The base class for all Flyte tasks.

### TaskResolverMixin
Mixin class that helps resolve a task implementation.

### IgnoreOutputs
Exception that can be raised to ignore task outputs.

"""

import asyncio
import collections
import datetime
import warnings
from abc import abstractmethod
from base64 import b64encode
from dataclasses import dataclass
from typing import (
    Any,
    Coroutine,
    Dict,
    Generic,
    List,
    Optional,
    OrderedDict,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from flyteidl.core import artifact_id_pb2 as art_id
from flyteidl.core import tasks_pb2

from flytekit.configuration import LocalConfig, SerializationSettings
from flytekit.core.artifact_utils import (
    idl_partitions_from_dict,
    idl_time_partition_from_datetime,
)
from flytekit.core.context_manager import (
    ExecutionParameters,
    ExecutionState,
    FlyteContext,
    FlyteContextManager,
    FlyteEntities,
)
from flytekit.core.interface import Interface, transform_interface_to_typed_interface
from flytekit.core.local_cache import LocalTaskCache
from flytekit.core.promise import (
    Promise,
    VoidPromise,
    create_and_link_node,
    create_task_output,
    extract_obj_name,
    flyte_entity_call_handler,
    translate_inputs_to_literals,
)
from flytekit.core.tracker import TrackedInstance
from flytekit.core.type_engine import TypeEngine, TypeTransformerFailedError
from flytekit.core.utils import timeit
from flytekit.deck import DeckField
from flytekit.exceptions.system import (
    FlyteDownloadDataException,
    FlyteNonRecoverableSystemException,
    FlyteUploadDataException,
)
from flytekit.exceptions.user import FlyteUserRuntimeException
from flytekit.loggers import logger
from flytekit.models import dynamic_job as _dynamic_job
from flytekit.models import interface as _interface_models
from flytekit.models import literals as _literal_models
from flytekit.models import task as _task_model
from flytekit.models.core import workflow as _workflow_model
from flytekit.models.documentation import Description, Documentation
from flytekit.models.interface import Variable
from flytekit.models.security import SecurityContext
from flytekit.utils.asyn import run_sync

DYNAMIC_PARTITIONS = "_uap"
MODEL_CARD = "_ucm"
DATA_CARD = "_ucd"
UNSET_CARD = "_uc"


def kwtypes(**kwargs) -> OrderedDict[str, Type]:
    """
    This is a small helper function to convert the keyword arguments to an OrderedDict of types.

    ```python
    kwtypes(a=int, b=str)
    ```
    """
    d = collections.OrderedDict()
    for k, v in kwargs.items():
        d[k] = v
    return d


@dataclass
class TaskMetadata(object):
    """
    Metadata for a Task. Things like retries and whether or not caching is turned on, and cache version are specified
    here.

    See the :std:ref:`IDL <idl:protos/docs/core/core:taskmetadata>` for the protobuf definition.

    Attributes:
        cache (bool): Indicates if caching should be enabled. See :std:ref:`Caching <cookbook:caching>`.
        cache_serialize (bool): Indicates if identical (i.e. same inputs) instances of this task should be executed in serial when caching is enabled. See :std:ref:`Caching <cookbook:caching>`.
        cache_version (str): Version to be used for the cached value.
        cache_ignore_input_vars (Tuple[str, ...]): Input variables that should not be included when calculating hash for cache.
        interruptible (Optional[bool]): Indicates that this task can be interrupted and/or scheduled on nodes with lower QoS guarantees that can include pre-emption.
        deprecated (str): Can be used to provide a warning message for a deprecated task. An absence or empty string indicates that the task is active and not deprecated.
        retries (int): for retries=n; n > 0, on failures of this task, the task will be retried at-least n number of times.
        timeout (Optional[Union[datetime.timedelta, int]]): The maximum duration for which one execution of this task should run. The execution will be terminated if the runtime exceeds this timeout.
        pod_template_name (Optional[str]): The name of an existing PodTemplate resource in the cluster which will be used for this task.
        generates_deck (bool): Indicates whether the task will generate a Deck URI.
        is_eager (bool): Indicates whether the task should be treated as eager.
        labels (Optional[dict[str, str]]): Labels to be applied to the task resource.
        annotations (Optional[dict[str, str]]): Annotations to be applied to the task resource.
    """

    cache: bool = False
    cache_serialize: bool = False
    cache_version: str = ""
    cache_ignore_input_vars: Tuple[str, ...] = ()
    interruptible: Optional[bool] = None
    deprecated: str = ""
    retries: int = 0
    timeout: Optional[Union[datetime.timedelta, int]] = None
    pod_template_name: Optional[str] = None
    generates_deck: bool = False
    is_eager: bool = False
    labels: Optional[dict[str, str]] = None
    annotations: Optional[dict[str, str]] = None

    def __post_init__(self):
        if self.timeout:
            if isinstance(self.timeout, int):
                self.timeout = datetime.timedelta(seconds=self.timeout)
            elif not isinstance(self.timeout, datetime.timedelta):
                raise ValueError("timeout should be duration represented as either a datetime.timedelta or int seconds")
        if self.cache and not self.cache_version:
            raise ValueError("Caching is enabled ``cache=True`` but ``cache_version`` is not set.")
        if self.cache_serialize and not self.cache:
            raise ValueError("Cache serialize is enabled ``cache_serialize=True`` but ``cache`` is not enabled.")
        if self.cache_ignore_input_vars and not self.cache:
            raise ValueError(
                f"Cache ignore input vars are specified ``cache_ignore_input_vars={self.cache_ignore_input_vars}`` but ``cache`` is not enabled."
            )

    @property
    def retry_strategy(self) -> _literal_models.RetryStrategy:
        return _literal_models.RetryStrategy(self.retries)

    def to_taskmetadata_model(self) -> _task_model.TaskMetadata:
        """
        Converts to _task_model.TaskMetadata
        """
        from flytekit import __version__

        return _task_model.TaskMetadata(
            discoverable=self.cache,
            runtime=_task_model.RuntimeMetadata(
                _task_model.RuntimeMetadata.RuntimeType.FLYTE_SDK, __version__, "python"
