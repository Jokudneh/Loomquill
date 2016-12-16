import os
import typing
from enum import Enum
from typing import Any, Dict, List, Optional, OrderedDict, Tuple, Type

from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask, TaskMetadata
from flytekit.core.context_manager import FlyteContext
from flytekit.core.interface import Interface
from flytekit.core.pod_template import PodTemplate
from flytekit.core.python_auto_container import get_registerable_container_image, update_image_spec_copy_handling
from flytekit.core.resources import Resources, ResourceSpec
from flytekit.core.utils import _get_container_definition, _serialize_pod_spec
from flytekit.image_spec.image_spec import ImageSpec
from flytekit.loggers import logger
from flytekit.models import task as _task_model
from flytekit.models.literals import LiteralMap
from flytekit.models.security import Secret, SecurityContext

_PRIMARY_CONTAINER_NAME_FIELD = "primary_container_name"
DOCKER_IMPORT_ERROR_MESSAGE = "Docker is not installed. Please install Docker by running `pip install docker`."


class ContainerTask(PythonTask):
    """
    This is an intermediate class that represents Flyte Tasks that run a container at execution time. This is the vast
    majority of tasks - the typical ``@task`` decorated tasks for instance all run a container. An example of
    something that doesn't run a container would be something like the Athena SQL task.
    """

    class MetadataFormat(Enum):
        JSON = _task_model.DataLoadingConfig.LITERALMAP_FORMAT_JSON
        YAML = _task_model.DataLoadingConfig.LITERALMAP_FORMAT_YAML
        PROTO = _task_model.DataLoadingConfig.LITERALMAP_FORMAT_PROTO

    class IOStrategy(Enum):
        DOWNLOAD_EAGER = _task_model.IOStrategy.DOWNLOAD_MODE_EAGER
        DOWNLOAD_STREAM = _task_model.IOStrategy.DOWNLOAD_MODE_STREAM
        DO_NOT_DOWNLOAD = _task_model.IOStrategy.DOWNLOAD_MODE_NO_DOWNLOAD
        UPLOAD_EAGER = _task_model.IOStrategy.UPLOAD_MODE_EAGER
        UPLOAD_ON_EXIT = _task_model.IOStrategy.UPLOAD_MODE_ON_EXIT
        DO_NOT_UPLOAD = _task_model.IOStrategy.UPLOAD_MODE_NO_UPLOAD

    def __init__(
        self,
        name: str,
        image: typing.Union[str, ImageSpec],
        command: List[str],
        inputs: Optional[OrderedDict[str, Type]] = None,
        metadata: Optional[TaskMetadata] = None,
        arguments: Optional[List[str]] = None,
        outputs: Optional[Dict[str, Type]] = None,
        requests: Optional[Resources] = None,
        limits: Optional[Resources] = None,
        input_data_dir: Optional[str] = None,
        output_data_dir: Optional[str] = None,
        metadata_format: MetadataFormat = MetadataFormat.JSON,
        io_strategy: Optional[IOStrategy] = None,
        secret_requests: Optional[List[Secret]] = None,
        pod_template: Optional["PodTemplate"] = None,
        pod_template_name: Optional[str] = None,
        local_logs: bool = False,
        resources: Optional[Resources] = None,
        **kwargs,
    ):
        sec_ctx = None
        if secret_requests:
            for s in secret_requests:
                if not isinstance(s, Secret):
                    raise AssertionError(f"Secret {s} should be of type flytekit.Secret, received {type(s)}")
            sec_ctx = SecurityContext(secrets=secret_requests)
