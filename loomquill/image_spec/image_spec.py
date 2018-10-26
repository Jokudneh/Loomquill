import base64
import copy
import dataclasses
import hashlib
import os
import pathlib
import platform
import re
import sys
import typing
from abc import abstractmethod
from dataclasses import asdict, dataclass
from functools import cached_property, lru_cache
from importlib import metadata
from typing import Any, Dict, List, Optional, Tuple, Union

import click
import requests
from packaging.version import Version

from flytekit.constants import CopyFileDetection
from flytekit.exceptions.user import FlyteAssertion

DOCKER_HUB = "docker.io"
_F_IMG_ID = "_F_IMG_ID"
FLYTE_FORCE_PUSH_IMAGE_SPEC = "FLYTE_FORCE_PUSH_IMAGE_SPEC"
# If the FLYTE_IMG_FAST_FAIL env variable is set to TRUE, ImageSpec will fail the registration rather than assuming
# an image exists if the image cannot be found or built.
FLYTE_IMG_FAST_FAIL = "FLYTE_IMG_FAST_FAIL"


@dataclass
class ImageSpec:
    """
    This class is used to specify the docker image that will be used to run the task.

    Attributes:
        name (str): Name of the image.
        python_version (str): Python version of the image. Use default python in the base image if None.
        builder (Optional[str]): Type of plugin to build the image. Use envd by default.
        source_root (Optional[str]): Source root of the image.
        env (Optional[Dict[str, str]]): Environment variables of the image.
        registry (Optional[str]): Registry of the image.
        packages (Optional[List[str]]): List of python packages to install.
        conda_packages (Optional[List[str]]): List of conda packages to install.
        conda_channels (Optional[List[str]]): List of conda channels.
        requirements (Optional[str]): Path to the requirements.txt file.
        apt_packages (Optional[List[str]]): List of apt packages to install.
        cuda (Optional[str]): Version of cuda to install.
        cudnn (Optional[str]): Version of cudnn to install.
        base_image (Optional[Union[str, 'ImageSpec']]): Base image of the image.
        platform (Optional[str]): Specify the target platforms for the build output (for example, windows/amd64 or linux/amd64,darwin/arm64).
        pip_index (Optional[str]): Specify the custom pip index url.
        pip_extra_index_url (Optional[List[str]]): Specify one or more pip index urls as a list.
        pip_secret_mounts (Optional[List[Tuple[str, str]]]): Specify a list of tuples to mount secret for pip install. Each tuple should contain the path to
            the secret file and the mount path. For example, [(".gitconfig", "/etc/gitconfig")]. This is experimental and
            the interface may change in the future. Configuring this should not change the built image.
        pip_extra_args (Optional[str]): Specify one or more extra pip install arguments as a space-delimited string.
        registry_config (Optional[str]): Specify the path to a JSON registry config file.
        entrypoint (Optional[List[str]]): List of strings to overwrite the entrypoint of the base image with, set to [] to remove the entrypoint.
        commands (Optional[List[str]]): Command to run during the building process.
        tag_format (Optional[str]): Custom string format for image tag. The ImageSpec hash passed in as `spec_hash`. For example,
            to add a "dev" suffix to the image tag, set `tag_format="{spec_hash}-dev"`.
        source_copy_mode (Optional[CopyFileDetection]): This option allows the user to specify which source files to copy from the local host, into the image.
            Not setting this option means to use the default flytekit behavior. The default behavior is:
                - if fast register is used, source files are not copied into the image (because they're already copied
                  into the fast register tar layer).
                - if fast register is not used, then the LOADED_MODULES (aka 'auto') option is used to copy loaded
                  Python files into the image.
            If the option is set by the user, then that option is of course used.
        copy (Optional[List[str]]): List of files/directories to copy to /root. e.g. ["src/file1.txt", "src/file2.txt"].
        python_exec (Optional[str]): Python executable to use for install packages.
        runtime_packages (Optional[List[str]]): List of packages to be installed during runtime. `runtime_packages` requires `pip` to be installed
            in your base image.
                - If you are using an ImageSpec as your base image, please include `pip` into your packages:
                  `ImageSpec(..., packages=["pip"])`.
                - If you want to install runtime packages into a fixed base_image and not use an image builder, you can
                  use `builder="noop"`: `ImageSpec(base_image="ghcr.io/name/my-custom-image", builder="noop").with_runtime_packages(["numpy"])`.
        builder_options (Optional[Dict[str, Any]]): Additional options for the builder. This is a dictionary that will be passed to the builder.
            The options are builder-specific and may not be supported by all builders.
        builder_config (Optional[typing.Dict[str, typing.Any]]): Custom builder images configuration, such as uv and micromamba images.
    """

    name: str = "flytekit"
    python_version: str = None  # Use default python in the base image if None.
    builder: Optional[str] = None
    source_root: Optional[str] = None  # a.txt:auto
    env: Optional[Dict[str, str]] = None
    registry: Optional[str] = None
    packages: Optional[List[str]] = None
    conda_packages: Optional[List[str]] = None
    conda_channels: Optional[List[str]] = None
    requirements: Optional[str] = None
    apt_packages: Optional[List[str]] = None
    cuda: Optional[str] = None
    cudnn: Optional[str] = None
    base_image: Optional[Union[str, "ImageSpec"]] = None
    platform: Optional[str] = None
    pip_index: Optional[str] = None
    pip_extra_index_url: Optional[List[str]] = None
    pip_secret_mounts: Optional[List[Tuple[str, str]]] = None
    pip_extra_args: Optional[str] = None
    registry_config: Optional[str] = None
    entrypoint: Optional[List[str]] = None
    commands: Optional[List[str]] = None
    tag_format: Optional[str] = None
    source_copy_mode: Optional[CopyFileDetection] = None
    copy: Optional[List[str]] = None
    python_exec: Optional[str] = None
    runtime_packages: Optional[List[str]] = None
    builder_options: Optional[Dict[str, Any]] = None
    builder_config: Optional[typing.Dict[str, typing.Any]] = None

    def __post_init__(self):
        from flytekit.clis.helpers import str2bool

        self.name = self.name.lower()
        self._is_force_push = str2bool(os.environ.get(FLYTE_FORCE_PUSH_IMAGE_SPEC, "FALSE"))  # False by default
        self._fast_fail = str2bool(os.environ.get(FLYTE_IMG_FAST_FAIL, "FALSE"))  # False by default
        if self.registry:
            self.registry = self.registry.lower()
            if not validate_container_registry_name(self.registry):
                raise ValueError(
                    f"Invalid container registry name: '{self.registry}'.\n Expected formats:\n"
                    f"- 'localhost:30000' (for local registries)\n"
                    f"- 'ghcr.io/username' (for GitHub Container Registry)\n"
                    f"- 'docker.io/username' (for docker hub)\n"
                )

        if self.platform is None:
            if (
                self.registry
                and self.registry.lower().startswith("localhost:")
                and platform.machine().lower() in ("arm64", "aarch64")
            ):
                # Only change platform to ARM64 if platform is not set and pushing to local registry on ARM64 machine
                self.platform = "linux/arm64"
            else:
                self.platform = "linux/amd64"

        # If not set, help the user set this option as well, to support the older default behavior where existence
        # of the source root implied that copying of files was needed.
        if self.source_root is not None:
            self.source_copy_mode = self.source_copy_mode or CopyFileDetection.LOADED_MODULES

        builder_registry = ImageBuildEngine.get_registry()
        if self.builder is None and builder_registry:
            # Use the builder with the highest priority by default
            self.builder = max(builder_registry, key=lambda name: builder_registry[name][1])

        parameters_str_list = [
            "packages",
            "conda_channels",
            "conda_packages",
