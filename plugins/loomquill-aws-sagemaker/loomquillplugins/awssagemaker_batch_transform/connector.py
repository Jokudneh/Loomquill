"""SageMaker batch-transform connector.

Mirrors the training-job connector. Targets ``CreateTransformJob`` /
``DescribeTransformJob`` / ``StopTransformJob``. Surfaces the predictions
``S3OutputPath`` so downstream Flyte tasks can read scores written by SageMaker
without any extra plumbing.

Note: ``TransformJobStatus`` has no ``Deleting`` state and there is no
``SecondaryStatus`` — running phase has no live progress signal beyond the job
being in flight.
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

