import os
from pathlib import Path
from textwrap import dedent

import pytest
from flytekitplugins.envd.image_builder import EnvdImageSpecBuilder, create_envd_config

from flytekit.image_spec.image_spec import ImageBuildEngine, ImageSpec
import tempfile

@pytest.fixture(scope="module", autouse=True)
def register_envd_higher_priority():
    # Register a new envd platform with the highest priority so the test in this file uses envd
    highest_priority_builder = max(ImageBuildEngine._REGISTRY, key=lambda name: ImageBuildEngine._REGISTRY[name][1])
    highest_priority = ImageBuildEngine._REGISTRY[highest_priority_builder][1]
    yield ImageBuildEngine.register(
        "envd_high_priority",
        EnvdImageSpecBuilder(),
        priority=highest_priority + 1,
    )
    del ImageBuildEngine._REGISTRY["envd_high_priority"]


def test_image_spec():
    base_image = ImageSpec(
        packages=["numpy"],
        python_version="3.9",
        registry="",
        base_image="cr.flyte.org/flyteorg/flytekit:py3.9-latest",
    )
    # Replace the base image name with the default flytekit image name,
    # so Envd can find the base image when building imageSpec below
    ImageBuildEngine._IMAGE_NAME_TO_REAL_NAME[base_image.image_name()] = "cr.flyte.org/flyteorg/flytekit:py3.9-latest"

    with tempfile.TemporaryDirectory(dir=Path.cwd().as_posix()) as temp_dir:
        copy_file = Path(temp_dir) / "copy_file.txt"
        copy_file.write_text("copy_file_content")

        image_spec = ImageSpec(
            packages=["pandas"],
            apt_packages=["git"],
