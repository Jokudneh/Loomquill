"""SageMaker Inference Recommender job connector.

Mirrors the training-job / batch-transform connectors. Targets
``CreateInferenceRecommendationsJob`` / ``DescribeInferenceRecommendationsJob`` /
``StopInferenceRecommendationsJob``. Surfaces the ranked
``InferenceRecommendations`` list (Default jobs) and the
``EndpointPerformances`` list (Default jobs targeting existing endpoints) so
downstream Flyte tasks can pick an instance type / endpoint config without
re-querying SageMaker.

Note: ``InferenceRecommendationsJob`` ``Status`` values are ALL_CAPS
(``PENDING`` / ``IN_PROGRESS`` / ``COMPLETED`` / ``FAILED`` / ``STOPPING`` /
``STOPPED`` / ``DELETING`` / ``DELETED``), unlike training/transform jobs which
use PascalCase.
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

from flytekit.extend.backend.base_connector import (
    AsyncConnectorBase,
    ConnectorRegistry,
    Resource,
    ResourceMeta,
)
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate


@dataclass
class SageMakerInferenceRecommenderJobMetadata(ResourceMeta):
    config: Dict[str, Any]
    region: Optional[str] = None
    inputs: Optional[LiteralMap] = None

    def encode(self) -> bytes:
        return cloudpickle.dumps(self)

    @classmethod
    def decode(cls, data: bytes) -> "SageMakerInferenceRecommenderJobMetadata":
        return cloudpickle.loads(data)


# Status values per boto3 reference. PENDING and IN_PROGRESS keep the job
# in flight; STOPPING is still a running tear-down. STOPPED covers both
# user-stop and timeout. DELETING/DELETED are admin states - treat as failure
# so we don't silently surface partial recommendations.
_STATE_MAP = {
    "PENDING": TaskExecution.RUNNING,
    "IN_PROGRESS": TaskExecution.RUNNING,
    "STOPPING": TaskExecution.RUNNING,
    "COMPLETED": TaskExecution.SUCCEEDED,
    "FAILED": TaskExecution.FAILED,
    "STOPPED": TaskExecution.FAILED,
    "DELETING": TaskExecution.FAILED,
    "DELETED": TaskExecution.FAILED,
