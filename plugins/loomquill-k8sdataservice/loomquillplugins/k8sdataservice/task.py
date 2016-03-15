from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Type

from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct

from flytekit import Resources, kwtypes, logger
from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.interface import Interface
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin


@dataclass
class DataServiceConfig(object):
    """DataServiceConfig should be used to configure a DataServiceTask."""

    Name: Optional[str] = None
    Requests: Optional[Resources] = None
    Limits: Optional[Resources] = None
    Port: Optional[int] = None
    Image: Optional[str] = None
    Command: Optional[List[str]] = None
    Replicas: Optional[int] = None
