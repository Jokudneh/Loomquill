from datetime import timedelta
import pathlib
import os
import pytest
from jupyter_client.manager import KernelManager, BlockingKernelClient

from flytekit.configuration import Config
from flytekit.remote import FlyteRemote
import ipykernel.kernelspec


CONFIG = os.environ.get("FLYTECTL_CONFIG", str(pathlib.Path.home() / ".flyte" / "config-sandbox.yaml"))
# Run `make build-dev` to build and push the image to the local registry.
IMAGE = os.environ.get("FLYTEKIT_IMAGE", "localhost:30000/flytekit:dev")
PROJECT = "flytesnacks"
DOMAIN = "development"
VERSION = f"v{os.getpid()}"
KERNEL_NAME = "python3-flytekit-integration"


@pytest.fixture(scope="module", autouse=True)
def install_kernel():
