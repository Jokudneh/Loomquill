import pytest

from collections import OrderedDict
from flytekit.image_spec.image_spec import ImageSpec
from flytekit.core.task import task, eager
import flytekit.configuration
from flytekit.configuration import Image, ImageConfig
from flytekit.core.python_function_task import EagerFailureHandlerTask
from flytekit.tools.translator import get_serializable

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = flytekit.configuration.SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)

eager_image = "ghcr.io/testorg/testimage:v12"
