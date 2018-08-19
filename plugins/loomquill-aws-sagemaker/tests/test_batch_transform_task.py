import pytest
from flytekitplugins.awssagemaker_batch_transform import (
    SageMakerDescribeTransformJobTask,
    SageMakerStopTransformJobTask,
    SageMakerTransformJobTask,
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


def test_transform_job_task_interface_and_custom():
    task = SageMakerTransformJobTask(
        name="batch_score",
