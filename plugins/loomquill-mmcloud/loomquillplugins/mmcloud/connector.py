import json
import shlex
import subprocess
from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from typing import Optional

from flytekitplugins.mmcloud.utils import async_check_output, mmcloud_status_to_flyte_phase

from flytekit import current_context
from flytekit.extend.backend.base_connector import AsyncConnectorBase, ConnectorRegistry, Resource, ResourceMeta
from flytekit.loggers import logger
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate


@dataclass
class MMCloudMetadata(ResourceMeta):
    job_id: str


class MMCloudConnector(AsyncConnectorBase):
    name = "MMCloud Connector"

    def __init__(self):
        super().__init__(task_type_name="mmcloud_task", metadata_type=MMCloudMetadata)
        self._response_format = ["--format", "json"]

    async def async_login(self):
        """
        Log in to Memory Machine Cloud OpCenter.
        """
        try:
            # If already logged in, this will reset the session timer
            login_info_command = ["float", "login", "--info"]
            await async_check_output(*login_info_command)
        except subprocess.CalledProcessError:
            logger.info("Attempting to log in to OpCenter")
            try:
                secrets = current_context().secrets
                login_command = [
                    "float",
                    "login",
                    "--address",
                    secrets.get("mmc_address"),
                    "--username",
                    secrets.get("mmc_username"),
                    "--password",
                    secrets.get("mmc_password"),
                ]
                await async_check_output(*login_command)
            except subprocess.CalledProcessError:
                logger.exception("Failed to log in to OpCenter")
                raise

            logger.info("Logged in to OpCenter")

    async def create(
