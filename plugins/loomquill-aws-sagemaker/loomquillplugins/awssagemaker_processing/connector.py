"""SageMaker processing-job connector.

Mirrors ``awssagemaker_training.connector`` (long-running async lifecycle:
create → describe-poll → stop) but targets ``CreateProcessingJob`` instead of
``CreateTrainingJob``. Surfaces the processed-output S3 URIs in outputs so
downstream Flyte tasks (a ``SageMakerTrainingJobTask`` consuming engineered
features, a ``SageMakerModelTask``, or a custom gate task) can consume them
without any extra plumbing.

Note: ``ProcessingJobStatus`` values (``InProgress`` / ``Completed`` /
``Failed`` / ``Stopping`` / ``Stopped``) match the PascalCase training-job
convention, but processing jobs have no ``SecondaryStatus`` — ``ExitMessage`` /
``FailureReason`` are the useful single lines on terminal states.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import cloudpickle
from flyteidl.core.execution_pb2 import TaskExecution
from flytekitplugins.awssagemaker_inference.boto3_mixin import (
    Boto3ConnectorMixin,
    CustomException,
)
from flytekitplugins.awssagemaker_inference.pythonic_base import (
    PythonicSageMakerJobConnector,
    _build_environment,
    _container_entrypoint,
    _tags_to_list,
)

from flytekit.extend.backend.base_connector import (
    AsyncConnectorBase,
    ConnectorRegistry,
    Resource,
    ResourceMeta,
)
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate


@dataclass
class SageMakerProcessingJobMetadata(ResourceMeta):
    config: Dict[str, Any]
    region: Optional[str] = None
    inputs: Optional[LiteralMap] = None

    def encode(self) -> bytes:
        return cloudpickle.dumps(self)

    @classmethod
