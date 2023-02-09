import pytest
from mock import patch as _system_patch

import flytekit.configuration
from flytekit.configuration import Image, ImageConfig
from flytekit.core.task import task
from flytekit.core.testing import patch as flyte_patch
from flytekit.core.workflow import ImperativeWorkflow, workflow

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = flytekit.configuration.SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)


@task
def t1(a: str) -> str:
