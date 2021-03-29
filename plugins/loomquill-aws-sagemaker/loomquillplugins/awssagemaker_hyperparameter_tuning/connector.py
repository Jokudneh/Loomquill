"""SageMaker hyperparameter-tuning-job connector.

Mirrors the training-job connector: same long-running async lifecycle
(create -> describe-poll -> stop) but targets ``CreateHyperParameterTuningJob``.
On completion, surfaces ``BestTrainingJob`` plus the trained
``S3ModelArtifacts`` (looked up via a single follow-up
``describe_training_job`` call, since ``DescribeHyperParameterTuningJob`` does
not include it) so the result chains straight into ``SageMakerModelTask``
without any extra workflow plumbing.
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

from flytekit.extend.backend.base_connector import (
    AsyncConnectorBase,
    ConnectorRegistry,
    Resource,
    ResourceMeta,
)
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate


@dataclass
class SageMakerHyperParameterTuningJobMetadata(ResourceMeta):
    config: Dict[str, Any]
    region: Optional[str] = None
    inputs: Optional[LiteralMap] = None

    def encode(self) -> bytes:
        return cloudpickle.dumps(self)

    @classmethod
    def decode(cls, data: bytes) -> "SageMakerHyperParameterTuningJobMetadata":
        return cloudpickle.loads(data)


# HyperParameterTuningJobStatus -> Flyte phase.
# - Stopping is "still in flight" (SageMaker is asking each child training job to stop
#   gracefully) so we report Running while the tear-down happens.
