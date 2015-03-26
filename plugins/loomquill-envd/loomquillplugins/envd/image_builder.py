import os
import pathlib
import shutil
import subprocess
from dataclasses import asdict
from importlib import metadata

import click
from packaging.version import Version
from rich import print
from rich.pretty import Pretty

from flytekit.configuration import DefaultImages
from flytekit.constants import CopyFileDetection
from flytekit.core import context_manager
from flytekit.core.constants import REQUIREMENTS_FILE_NAME
from flytekit.image_spec.image_spec import _F_IMG_ID, ImageBuildEngine, ImageSpec, ImageSpecBuilder
from flytekit.tools.ignore import DockerIgnore, GitIgnore, IgnoreGroup, StandardIgnore
from flytekit.tools.script_mode import ls_files

FLYTE_LOCAL_REGISTRY = "localhost:30000"
FLYTE_ENVD_CONTEXT = "FLYTE_ENVD_CONTEXT"


class EnvdImageSpecBuilder(ImageSpecBuilder):
    """
    This class is used to build a docker image using envd.
    """

    def build_image(self, image_spec: ImageSpec):
        cfg_path = create_envd_config(image_spec)

        if image_spec.registry_config:
            bootstrap_command = f"envd bootstrap --registry-config {image_spec.registry_config}"
            execute_command(bootstrap_command)

        build_command = f"envd build --path {pathlib.Path(cfg_path).parent}  --platform {image_spec.platform}"
        if image_spec.registry and os.getenv("FLYTE_PUSH_IMAGE_SPEC", "True").lower() in ("true", "1"):
            build_command += f" --output type=image,name={image_spec.image_name()},push=true"
        else:
            build_command += f" --tag {image_spec.image_name()}"
        envd_context_switch(image_spec.registry)
        try:
            execute_command(build_command)
        except Exception as e:
