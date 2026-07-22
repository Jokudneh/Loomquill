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
    return a + " world"


wb = ImperativeWorkflow(name="my.workflow")
wb.add_workflow_input("in1", str)
node = wb.add_entity(t1, a=wb.inputs["in1"])
wb.add_workflow_output("from_n0t1", node.outputs["o0"])

