import tempfile
from collections import OrderedDict

import mock

import flytekit.configuration
from flytekit import ContainerTask, Resources, kwtypes
from flytekit.configuration import Image, ImageConfig
from flytekit.core.python_customized_container_task import PythonCustomizedContainerTask, TaskTemplateResolver
from flytekit.core.utils import write_proto_to_file
from flytekit.tools.translator import get_serializable

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = flytekit.configuration.SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)
