from datetime import datetime, timedelta
from unittest import mock

import pytest
from botocore.exceptions import ClientError
from flyteidl.core.execution_pb2 import TaskExecution
from flytekitplugins.awssagemaker_inference.boto3_mixin import CustomException
from flytekitplugins.awssagemaker_processing.connector import (
    SageMakerProcessingJobMetadata,
    _build_outputs,
)

from flytekit.extend.backend.base_connector import ConnectorRegistry
from flytekit.interfaces.cli_identifiers import Identifier
from flytekit.models import literals
from flytekit.models.core.identifier import ResourceType
from flytekit.models.task import RuntimeMetadata, TaskMetadata, TaskTemplate

idempotence_token = "74443947857331f7"

REGION = "us-east-2"
PROCESSING_JOB_NAME = "prep-{idempotence_token}"
PROCESSING_JOB_ARN = (
    "arn:aws:sagemaker:us-east-2:1234567890:processing-job/prep-74443947857331f7"
)
S3_OUTPUT = "s3://my-bucket/processing/prep-74443947857331f7/output/train"


def _task_config():
    return {
        "config": {
            "ProcessingJobName": PROCESSING_JOB_NAME,
            "AppSpecification": {
                "ImageUri": "{images.processing_image}",
                "ContainerEntrypoint": ["python3", "/opt/ml/processing/preprocess.py"],
            },
            "RoleArn": "{inputs.execution_role_arn}",
            "ProcessingResources": {
                "ClusterConfig": {
                    "InstanceType": "ml.m5.xlarge",
                    "InstanceCount": 1,
                    "VolumeSizeInGB": 30,
                }
            },
            "ProcessingOutputConfig": {
                "Outputs": [
                    {
                        "OutputName": "train",
                        "S3Output": {
                            "S3Uri": "{inputs.output_prefix}",
                            "LocalPath": "/opt/ml/processing/output",
                            "S3UploadMode": "EndOfJob",
                        },
                    }
                ]
            },
            "StoppingCondition": {"MaxRuntimeInSeconds": 3600},
        },
        "region": REGION,
        "images": {"processing_image": "1234567890.dkr.ecr.us-east-2.amazonaws.com/sklearn:latest"},
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
        type="sagemaker-processing-job",
    )


def _completed_describe_response():
    return {
        "ProcessingJobName": "prep-74443947857331f7",
        "ProcessingJobArn": PROCESSING_JOB_ARN,
        "ProcessingJobStatus": "Completed",
        "ProcessingOutputConfig": {
            "Outputs": [
                {
                    "OutputName": "train",
                    "S3Output": {"S3Uri": S3_OUTPUT, "LocalPath": "/opt/ml/processing/output"},
                }
            ]
        },
        "ExitMessage": "Completed: Job completed successfully",
        "ProcessingStartTime": datetime(2026, 4, 30, 12, 0, 0),
        "ProcessingEndTime": datetime(2026, 4, 30, 12, 5, 0),
