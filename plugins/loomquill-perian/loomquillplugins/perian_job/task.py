from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, OrderedDict, Type, Union

from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct

from flytekit import FlyteContextManager, PythonFunctionTask, logger
from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.interface import Interface
from flytekit.exceptions.user import FlyteUserException
from flytekit.extend import TaskPlugins
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin
from flytekit.image_spec import ImageSpec


@dataclass
class PerianConfig:
    """Used to configure a Perian Task"""

    # Number of CPU cores
    cores: Optional[int] = None
    # Amount of memory in GB
    memory: Optional[int] = None
    # Number of accelerators
    accelerators: Optional[int] = None
    # Type of accelerator (e.g. 'A100')
