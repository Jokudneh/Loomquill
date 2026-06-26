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
    images: Optional[Dict[str, Union[str, ImageSpec]]] = None


class BotoTask(SyncConnectorExecutorMixin, PythonTask[BotoConfig]):
    _TASK_TYPE = "boto"

    def __init__(
        self,
        name: str,
        task_config: BotoConfig,
        inputs: Optional[Dict[str, Type]] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            task_config=task_config,
