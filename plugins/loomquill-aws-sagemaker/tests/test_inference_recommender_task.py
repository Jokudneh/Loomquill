import pytest
from flytekitplugins.awssagemaker_inference_recommender import (
    SageMakerDescribeInferenceRecommenderJobTask,
    SageMakerInferenceRecommenderJobTask,
    SageMakerStopInferenceRecommenderJobTask,
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


def test_inference_recommender_job_task_interface_and_custom():
