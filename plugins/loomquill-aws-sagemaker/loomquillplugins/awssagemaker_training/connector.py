"""SageMaker training-job connector.

Mirrors the pattern in ``awssagemaker_inference.connector`` (long-running async
lifecycle: create → describe-poll → stop) but targets ``CreateTrainingJob``
instead of ``CreateEndpoint``. Surfaces the trained ``S3ModelArtifacts`` URI and
final metrics in outputs so downstream Flyte tasks (a ``SageMakerModelTask`` for
deployment, or a custom Flyte gate task for accuracy thresholds) can consume them
without any extra plumbing.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

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
class SageMakerTrainingJobMetadata(ResourceMeta):
    config: Dict[str, Any]
    region: Optional[str] = None
    inputs: Optional[LiteralMap] = None

    def encode(self) -> bytes:
        return cloudpickle.dumps(self)

    @classmethod
    def decode(cls, data: bytes) -> "SageMakerTrainingJobMetadata":
        return cloudpickle.loads(data)


# TrainingJobStatus → Flyte phase (verified against current boto3 reference).
