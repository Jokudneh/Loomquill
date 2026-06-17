import pytest
from flytekitplugins.awssagemaker_training import (
    SageMakerDescribeTrainingJobTask,
    SageMakerStopTrainingJobTask,
    SageMakerTrainingJobTask,
)

from flytekit import kwtypes
from flytekit.configuration import Image, ImageConfig, SerializationSettings


def _ser_settings():
    default_img = Image(name="default", fqn="test", tag="tag")
    return SerializationSettings(
        project="project",
        domain="domain",
        version="123",
        image_config=ImageConfig(default_image=default_img, images=[default_img]),
        env={},
    )


def test_training_job_task_interface_and_custom():
    task = SageMakerTrainingJobTask(
        name="train_xgb",
        config={
            "TrainingJobName": "xgb-{idempotence_token}",
            "AlgorithmSpecification": {
                "TrainingImage": "{images.training_image}",
                "TrainingInputMode": "File",
            },
            "RoleArn": "{inputs.execution_role_arn}",
            "ResourceConfig": {
                "InstanceType": "ml.m5.xlarge",
                "InstanceCount": 1,
                "VolumeSizeInGB": 30,
            },
