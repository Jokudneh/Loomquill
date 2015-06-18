import collections
import datetime
import inspect
import typing
from abc import abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, TypeVar, Union

from typing_extensions import Protocol, get_type_hints, runtime_checkable

from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask, TaskMetadata
from flytekit.core.interface import Interface
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin, ResourceMeta


@runtime_checkable
class SensorConfig(Protocol):
    def to_dict(self) -> typing.Dict[str, Any]:
        """
        Serialize the sensor config to a dictionary.
