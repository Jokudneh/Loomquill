from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from mashumaro.mixins.json import DataClassJSONMixin

import flytekit
from flytekit import Resources, kwtypes, lazy_module
from flytekit.configuration import SerializationSettings
from flytekit.configuration.default_images import DefaultImages, PythonVersion
from flytekit.core.base_task import PythonTask
from flytekit.core.interface import Interface
from flytekit.core.python_customized_container_task import PythonCustomizedContainerTask
from flytekit.core.shim_task import ShimTaskExecutor
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin
from flytekit.models.security import Secret
from flytekit.models.task import TaskTemplate
from flytekit.types.file import JSONLFile

openai = lazy_module("openai")


@dataclass
class BatchResult(DataClassJSONMixin):
    output_file: Optional[JSONLFile] = None
    error_file: Optional[JSONLFile] = None


class BatchEndpointTask(AsyncConnectorExecutorMixin, PythonTask):
    _TASK_TYPE = "openai-batch"

    def __init__(
        self,
