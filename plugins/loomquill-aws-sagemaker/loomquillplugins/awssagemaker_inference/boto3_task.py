from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, Union

from flytekit import ImageSpec, kwtypes
from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.interface import Interface
from flytekit.extend.backend.base_connector import SyncConnectorExecutorMixin
from flytekit.image_spec.image_spec import ImageBuildEngine


@dataclass
class BotoConfig(object):
    service: str
    method: str
    config: Dict[str, Any]
    region: Optional[str] = None
