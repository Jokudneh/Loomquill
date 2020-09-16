from datetime import datetime, timedelta
from unittest import mock

import pytest
from botocore.exceptions import ClientError
from flyteidl.core.execution_pb2 import TaskExecution
from flytekitplugins.awssagemaker_inference.boto3_mixin import CustomException
from flytekitplugins.awssagemaker_training.connector import (
    SageMakerTrainingJobMetadata,
)

from flytekit.extend.backend.base_connector import ConnectorRegistry
from flytekit.interfaces.cli_identifiers import Identifier
from flytekit.models import literals
from flytekit.models.core.identifier import ResourceType
from flytekit.models.task import RuntimeMetadata, TaskMetadata, TaskTemplate

idempotence_token = "74443947857331f7"

REGION = "us-east-2"
TRAINING_JOB_NAME = "xgb-{idempotence_token}"
TRAINING_JOB_ARN = (
    "arn:aws:sagemaker:us-east-2:1234567890:training-job/xgb-74443947857331f7"
)
S3_MODEL_ARTIFACTS = "s3://my-bucket/output/xgb-74443947857331f7/output/model.tar.gz"


def _task_config():
    return {
        "config": {
            "TrainingJobName": TRAINING_JOB_NAME,
            "AlgorithmSpecification": {
                "TrainingImage": "{images.training_image}",
                "TrainingInputMode": "File",
            },
            "RoleArn": "{inputs.execution_role_arn}",
            "OutputDataConfig": {"S3OutputPath": "{inputs.output_prefix}"},
            "ResourceConfig": {
                "InstanceType": "ml.m5.xlarge",
                "InstanceCount": 1,
                "VolumeSizeInGB": 30,
            },
            "StoppingCondition": {"MaxRuntimeInSeconds": 3600},
        },
        "region": REGION,
        "images": {"training_image": "1234567890.dkr.ecr.us-east-2.amazonaws.com/xgboost:latest"},
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
