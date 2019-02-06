from datetime import datetime, timedelta
from unittest import mock

import pytest
from botocore.exceptions import ClientError
from flyteidl.core.execution_pb2 import TaskExecution
from flytekitplugins.awssagemaker_inference.boto3_mixin import CustomException
from flytekitplugins.awssagemaker_inference_recommender.connector import (
    SageMakerInferenceRecommenderJobMetadata,
)

from flytekit.extend.backend.base_connector import ConnectorRegistry
from flytekit.interfaces.cli_identifiers import Identifier
from flytekit.models import literals
from flytekit.models.core.identifier import ResourceType
from flytekit.models.task import RuntimeMetadata, TaskMetadata, TaskTemplate

idempotence_token = "74443947857331f7"

REGION = "us-east-2"
JOB_ARN = (
    "arn:aws:sagemaker:us-east-2:1234567890:inference-recommendations-job/"
    "rec-74443947857331f7"
)


def _task_config():
    return {
        "config": {
            "JobName": "rec-{idempotence_token}",
            "JobType": "Default",
            "JobDescription": "Smoke recommendations for ranker-prod",
            "RoleArn": "{inputs.role_arn}",
            # Default-job InputConfig allows only ModelPackageVersionArn (or
            # ModelName + ContainerConfig). JobDurationInSeconds /
            # TrafficPattern / ResourceLimit / EndpointConfigurations and the
            # top-level StoppingConditions are all Advanced-only — AWS rejects
            # them with a ValidationException if set here.
            "InputConfig": {
                "ModelPackageVersionArn": "{inputs.model_package_version_arn}",
            },
        },
        "region": REGION,
    }


def _task_template():
    task_id = Identifier(
        resource_type=ResourceType.TASK,
        project="project",
        domain="domain",
        name="name",
        version="version",
    )
    task_metadata = TaskMetadata(
        discoverable=True,
        runtime=RuntimeMetadata(RuntimeMetadata.RuntimeType.FLYTE_SDK, "1.0.0", "python"),
        timeout=timedelta(days=1),
        retries=literals.RetryStrategy(3),
        interruptible=True,
        discovery_version="0.1.1b0",
        deprecated_error_message="This is deprecated!",
        cache_serializable=True,
        pod_template_name="A",
        cache_ignore_input_vars=(),
    )
    return TaskTemplate(
        id=task_id,
        custom=_task_config(),
        metadata=task_metadata,
        interface=None,
        type="sagemaker-inference-recommender-job",
    )

