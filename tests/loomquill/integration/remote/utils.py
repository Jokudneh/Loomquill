"""
Common utilities for flyte remote runs in integration tests.
"""
import os
import json
import tempfile
import pathlib

import botocore.session
from botocore.client import BaseClient
from flytekit.configuration import Config
from flytekit.remote.remote import FlyteRemote


# Define constants
CONFIG = os.environ.get("FLYTECTL_CONFIG", str(pathlib.Path.home() / ".flyte" / "config-sandbox.yaml"))
PROJECT = "flytesnacks"
DOMAIN = "development"


class SimpleFileTransfer:
    """Utilities for file transfer to minio s3 bucket.

    Mainly support single file uploading and automatic teardown.
    """

    def __init__(self) -> None:
        self._remote = FlyteRemote(
            config=Config.auto(config_file=CONFIG),
            default_project=PROJECT,
            default_domain=DOMAIN
        )
        self._s3_client = self._get_minio_s3_client(self._remote)
