from datetime import datetime, timedelta
from unittest import mock

import pytest
from botocore.exceptions import ClientError
from flyteidl.core.execution_pb2 import TaskExecution
from flytekitplugins.awssagemaker_hyperparameter_tuning.connector import (
    SageMakerHyperParameterTuningJobMetadata,
)
from flytekitplugins.awssagemaker_inference.boto3_mixin import CustomException

from flytekit.extend.backend.base_connector import ConnectorRegistry
from flytekit.interfaces.cli_identifiers import Identifier
from flytekit.models import literals
from flytekit.models.core.identifier import ResourceType
from flytekit.models.task import RuntimeMetadata, TaskMetadata, TaskTemplate

idempotence_token = "74443947857331f7"

REGION = "us-east-2"
TUNING_JOB_NAME = "xgb-tune-{idempotence_token}"
TUNING_JOB_ARN = (
    "arn:aws:sagemaker:us-east-2:1234567890:hyper-parameter-tuning-job/"
    "xgb-tune-74443947857331f7"
)
BEST_TRAINING_JOB_NAME = "xgb-tune-74443947857331f7-007-3f4a5b6c"
BEST_TRAINING_JOB_ARN = (
    "arn:aws:sagemaker:us-east-2:1234567890:training-job/"
    "xgb-tune-74443947857331f7-007-3f4a5b6c"
)
S3_MODEL_ARTIFACTS = (
    "s3://my-bucket/output/xgb-tune-74443947857331f7-007-3f4a5b6c/output/model.tar.gz"
)


def _task_config():
    return {
        "config": {
            "HyperParameterTuningJobName": TUNING_JOB_NAME,
            "HyperParameterTuningJobConfig": {
                "Strategy": "Bayesian",
                "HyperParameterTuningJobObjective": {
                    "Type": "Maximize",
                    "MetricName": "validation:auc",
                },
                "ResourceLimits": {
                    "MaxNumberOfTrainingJobs": 4,
                    "MaxParallelTrainingJobs": 2,
                },
                "ParameterRanges": {
                    "ContinuousParameterRanges": [
                        {"Name": "eta", "MinValue": "0.01", "MaxValue": "0.5"},
                    ],
                    "IntegerParameterRanges": [
                        {"Name": "max_depth", "MinValue": "3", "MaxValue": "9"},
                    ],
                },
            },
            "TrainingJobDefinition": {
                "AlgorithmSpecification": {
                    "TrainingImage": "{images.training_image}",
                    "TrainingInputMode": "File",
                    "MetricDefinitions": [
                        {"Name": "validation:auc", "Regex": "auc=([0-9\\.]+)"},
                    ],
                },
                "RoleArn": "{inputs.execution_role_arn}",
                "OutputDataConfig": {"S3OutputPath": "{inputs.output_prefix}"},
                "ResourceConfig": {
                    "InstanceType": "ml.m5.large",
                    "InstanceCount": 1,
                    "VolumeSizeInGB": 10,
                },
                "StoppingCondition": {"MaxRuntimeInSeconds": 1800},
            },
        },
        "region": REGION,
        "images": {
            "training_image": "1234567890.dkr.ecr.us-east-2.amazonaws.com/xgboost:latest"
        },
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
        type="sagemaker-hyperparameter-tuning-job",
    )


def _completed_describe_tuning_response():
    return {
        "HyperParameterTuningJobName": "xgb-tune-74443947857331f7",
        "HyperParameterTuningJobArn": TUNING_JOB_ARN,
        "HyperParameterTuningJobStatus": "Completed",
        "TrainingJobStatusCounters": {
            "Completed": 4,
            "InProgress": 0,
            "RetryableError": 0,
            "NonRetryableError": 0,
            "Stopped": 0,
        },
        "ObjectiveStatusCounters": {"Succeeded": 4, "Pending": 0, "Failed": 0},
        "BestTrainingJob": {
            "TrainingJobName": BEST_TRAINING_JOB_NAME,
            "TrainingJobArn": BEST_TRAINING_JOB_ARN,
            "TrainingJobStatus": "Completed",
            "ObjectiveStatus": "Succeeded",
            "FinalHyperParameterTuningJobObjectiveMetric": {
                "MetricName": "validation:auc",
                "Value": 0.93,
            },
            "TunedHyperParameters": {"eta": "0.21", "max_depth": "7"},
            "TrainingStartTime": datetime(2026, 4, 30, 12, 0, 0),
            "TrainingEndTime": datetime(2026, 4, 30, 12, 8, 0),
        },
    }


def _describe_training_response():
    return {
        "TrainingJobName": BEST_TRAINING_JOB_NAME,
        "TrainingJobArn": BEST_TRAINING_JOB_ARN,
        "TrainingJobStatus": "Completed",
        "ModelArtifacts": {"S3ModelArtifacts": S3_MODEL_ARTIFACTS},
    }


def _routing_side_effect(method_to_response):
    """Build a side_effect that dispatches on the ``method`` kwarg of _call.

    The HPO connector's get() makes up to two boto3 calls per poll:
    describe_hyper_parameter_tuning_job, and on Completed, describe_training_job.
    Tests need to return the right payload for each.
    """

    async def _side_effect(*args, **kwargs):
        method = kwargs.get("method")
        if method not in method_to_response:
            raise AssertionError(f"unexpected _call(method={method!r})")
        return method_to_response[method]

    return _side_effect
