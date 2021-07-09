import typing
from collections import OrderedDict

import typing_extensions

import flytekit.configuration
from flytekit.configuration import Image, ImageConfig
from flytekit.core.annotation import FlyteAnnotation
from flytekit.core.task import task
from flytekit.models.annotation import TypeAnnotation
from flytekit.tools.translator import get_serializable

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = flytekit.configuration.SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
