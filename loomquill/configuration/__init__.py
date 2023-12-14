"""
# Configuration

## Flytekit Configuration Sources

There are multiple ways to configure flytekit settings:

### Command Line Arguments
This is the recommended way of setting configuration values for many cases. For example, see `pyflyte package` command.

### Python Config Object
A `Config` object can be used directly, e.g. when initializing a `FlyteRemote` object. See the Control Plane design docs for examples on how to specify a `Config` object.

### Environment Variables
Users can specify these at compile time, but when your task is run, Flyte Propeller will also set configuration to ensure correct interaction with the platform. The environment variables must be specified with the format `FLYTE_{SECTION}_{OPTION}`, all in upper case. For example, to specify the `PlatformConfig.endpoint` setting, the environment variable would be `FLYTE_PLATFORM_URL`.

> [!NOTE]
> Environment variables won't work for image configuration, which need to be specified with the `pyflyte package --image ...` option or in a configuration file.

### YAML Format Configuration File
A configuration file that contains settings for both `flytectl` and `flytekit`. This is the recommended configuration file format. Invoke the `flytectl config init` command to create a boilerplate `~/.flyte/config.yaml` file, and `flytectl --help` to learn about all of the configuration yaml options.

Example `config.yaml` file:

```YAML
# Sample config file

admin:
  # For GRPC endpoints you might want to use dns:///flyte.myexample.com
  endpoint: dns:///localhost:8089
  authType: Pkce
  insecure: true

logger:
  show-source: true
  level: 0

console:
  endpoint: http://localhost:8080
  insecure: true

# This section is used only in the control plane to trigger a remote execution
storage:
  type: minio
  stow:
    kind: s3
    config:
      auth_type: accesskey
      access_key_id: minio
      secret_key: miniostorage
      endpoint: http://localhost:9000
      region: us-east-1
      disable_ssl: true
      addressing_style: "path"
```

### INI Format Configuration File
A configuration file for `flytekit`. By default, `flytekit` will look for a file in two places:

1. First, a file named `flytekit.config` in the Python interpreter's working directory.
2. A file in `~/.flyte/config` in the home directory as detected by Python.

Example `flytekit.config` file:

```ini
[sdk]
workflow_packages=my_cool_workflows, other_workflows
```

> [!WARNING]
> The INI format configuration is considered a legacy configuration format. We recommend using the yaml format instead if you're using a configuration file.

## How is configuration used?

Configuration usage can roughly be bucketed into the following areas:

- **Compile-time settings**: these are settings like the default image and named images, where to look for Flyte code, etc.
- **Platform settings**: Where to find the Flyte backend (Admin DNS, whether to use SSL)
- **Registration Run-time settings**: these are things like the K8s service account to use, a specific S3/GCS bucket to write off-loaded data (dataframes and files) to, notifications, labels & annotations, etc.
- **Data access settings**: Is there a custom S3 endpoint in use? Backoff/retry behavior for accessing S3/GCS, key and password, etc.
- **Other settings** - Statsd configuration, which is a run-time applicable setting but is not necessarily relevant to the Flyte platform.

## Configuration Objects

The following objects are encapsulated in a parent object called `Config`:

### Serialization Time Settings

These are serialization/compile-time settings that are used when using commands like `pyflyte package` or `pyflyte register`. These configuration settings are typically passed in as flags to the above CLI commands.

The image configurations are typically either passed in via an `--image` flag, or can be specified in the `yaml` or `ini` configuration files (see examples above).

- **Image**: Represents a container image with optional configuration overrides.
- **ImageConfig**: Represents an image configuration for a given project/domain combination.
- **SerializationSettings**: Controls how to serialize Flyte entities when registering with Admin.
- **FastSerializationSettings**: Configuration for faster serialization settings.

### Execution Time Settings

Users typically shouldn't be concerned with these configurations, as they are typically set by FlytePropeller or FlyteAdmin. The configurations below are useful for authenticating to a Flyte backend, configuring data access credentials, secrets, and statsd metrics.

- **PlatformConfig**: Configuration for how to connect to the Flyte platform.
- **StatsConfig**: Configuration for how to emit statsd metrics.
- **SecretsConfig**: Configuration for how to access secrets.
- **S3Config**: Amazon S3 specific configuration.
- **GCSConfig**: Google Cloud Storage specific configuration.
- **DataConfig**: Configuration for data access.

"""

from __future__ import annotations

import base64
import datetime
import enum
import gzip
import os
import pathlib
import re
import tempfile
import typing
from dataclasses import dataclass, field
from io import BytesIO
from typing import Dict, List, Optional

import yaml
from dataclasses_json import DataClassJsonMixin

from flytekit.configuration import internal as _internal
from flytekit.configuration.default_images import DefaultImages
from flytekit.configuration.file import ConfigEntry, ConfigFile, get_config_file, read_file_if_exists, set_if_exists
from flytekit.core.resources import ResourceSpec
from flytekit.image_spec import ImageSpec
from flytekit.image_spec.image_spec import ImageBuildEngine
from flytekit.loggers import logger

PROJECT_PLACEHOLDER = "{{ registration.project }}"
DOMAIN_PLACEHOLDER = "{{ registration.domain }}"
VERSION_PLACEHOLDER = "{{ registration.version }}"
DEFAULT_RUNTIME_PYTHON_INTERPRETER = "/opt/venv/bin/python3"
DEFAULT_FLYTEKIT_ENTRYPOINT_FILELOC = "bin/entrypoint.py"
DEFAULT_IMAGE_NAME = "default"
DEFAULT_IN_CONTAINER_SRC_PATH = "/root"
_IMAGE_FQN_TAG_REGEX = re.compile(r"([^:]+)(?=:.+)?")
SERIALIZED_CONTEXT_ENV_VAR = "_F_SS_C"


@dataclass(init=True, repr=True, eq=True, frozen=True)
class Image(DataClassJsonMixin):
    """
    Image is a structured wrapper for task container images used in object serialization.

    Attributes:
        name (str): A user-provided name to identify this image.
        fqn (str): Fully qualified image name. This consists of
            #. a registry location
            #. a username
            #. a repository name
            For example: `hostname/username/reponame`
        tag (str): Optional tag used to specify which version of an image to pull
        digest (str): Optional digest used to specify which version of an image to pull
    """

    name: str
    fqn: str
    tag: Optional[str] = None
    digest: Optional[str] = None

    def __post_init__(self):
        if not ((self.tag is None) or (self.digest is None)):
            raise ValueError(f"Cannot specify both tag and digest. Got tag={self.tag} and digest={self.digest}")

    @property
    def full(self) -> str:
        """ "
        Return the full image name with tag or digest, whichever is available.

        When using a tag the separator is `:` and when using a digest the separator is `@`.
        """
        return f"{self.fqn}@{self.digest}" if self.digest else f"{self.fqn}:{self.tag}"

    @property
    def version(self) -> Optional[str]:
        """
        Return the version of the image. This could be the tag or digest, whichever is available.
        """
        return self.digest or self.tag

    @staticmethod
    def look_up_image_info(name: str, image_identifier: str, allow_no_tag_or_digest: bool = False) -> Image:
        """
        Creates an `Image` object from an image identifier string or a path to an ImageSpec yaml file.

        This function is used when registering tasks/workflows with Admin. When using
        the canonical Python-based development cycle, the version that is used to
        register workflows and tasks with Admin should be the version of the image
        itself, which should ideally be something unique like the git revision SHA1 of
        the latest commit.

        :param name:
        :param image_identifier: Either the full image identifier string e.g. somedocker.com/myimage:someversion123
            or a path to a file containing a `ImageSpec`.
        :param allow_no_tag_or_digest:
        :rtype: Image
        """
        if pathlib.Path(image_identifier).is_file():
            with open(image_identifier, "r") as f:
                image_spec_dict = yaml.safe_load(f)
                image_spec = ImageSpec(**image_spec_dict)
                ImageBuildEngine.build(image_spec)
                image_identifier = image_spec.image_name()

        fqn, tag, digest = _parse_image_identifier(image_identifier)

        if not allow_no_tag_or_digest and tag is None and digest is None:
            raise AssertionError(f"Incorrectly formatted image {image_identifier}, missing tag or digest")
        return Image(name=name, fqn=fqn, tag=tag, digest=digest)


def _parse_image_identifier(image_identifier: str) -> typing.Tuple[str, Optional[str], Optional[str]]:
    """
    Largely copied from `docker.utils.parse_repository_tag`, but returns tags and digests separately.
    Returns:
        Tuple[str, str, str]: fully_qualified_name, tag, digest
    """
    parts = image_identifier.rsplit("@", 1)
    if len(parts) == 2:
        # The image identifier used a digest e.g. `xyz.com/abc@sha256:26c68657ccce2cb0a31b330cb0be2b5e108d467f641c62e13ab40cbec258c68d`
        return parts[0], None, parts[1]
    parts = image_identifier.rsplit(":", 1)
    if len(parts) == 2 and "/" not in parts[1]:
        # The image identifier used a tag e.g. `xyz.com/abc:latest`
        return parts[0], parts[1], None
    # The image identifier had no tag or digest e.g. `xyz.com/abc`
    return image_identifier, None, None


@dataclass(init=True, repr=True, eq=True, frozen=True)
class ImageConfig(DataClassJsonMixin):
    """
    We recommend you to use ImageConfig.auto(img_name=None) to create an ImageConfig.
    For example, ImageConfig.auto(img_name=""ghcr.io/flyteorg/flytecookbook:v1.0.0"") will create an ImageConfig.

    ImageConfig holds available images which can be used at registration time. A default image can be specified
    along with optional additional images. Each image in the config must have a unique name.

    Attributes:
        default_image (Optional[Image]): The default image to be used as a container for task serialization.
        images (List[Image]): Optional, additional images which can be used in task container definitions.
    """

    default_image: Optional[Image] = None
    images: Optional[List[Image]] = None

    def find_image(self, name) -> Optional[Image]:
        """
        Return an image, by name, if it exists.
        """
        lookup_images = [self.default_image] if self.default_image else []
        if self.images:
            lookup_images.extend(self.images)

        for i in lookup_images:
            if i.name == name:
                return i
        return None

    @staticmethod
    def validate_image(_: typing.Any, param: str, values: tuple) -> ImageConfig:
