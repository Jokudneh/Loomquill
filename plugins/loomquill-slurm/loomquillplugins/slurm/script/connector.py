import json
import tempfile
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Type

from asyncssh import SSHClientConnection
from asyncssh.sftp import SFTPError

import flytekit
from flytekit.core.type_engine import TypeEngine
from flytekit.extend.backend.base_connector import AsyncConnectorBase, ConnectorRegistry, Resource, ResourceMeta
from flytekit.extend.backend.utils import convert_to_flyte_phase
from flytekit.extras.tasks.shell import OutputLocation, _PythonFStringInterpolizer
from flytekit.loggers import logger
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate

from ..ssh_utils import SlurmCluster, get_ssh_conn


@dataclass
class SlurmJobMetadata(ResourceMeta):
    """
    Slurm job metadata.

    Attributes:
        job_id (str): Slurm job id.
        ssh_config (Dict[str, Any]): SSH connection configuration options.
        outputs (Dict[str, str]): Mapping from the output variable name to the output location.
    """

    job_id: str
    ssh_config: Dict[str, Any]
    outputs: Dict[str, str]


class SlurmScriptConnector(AsyncConnectorBase):
    name = "Slurm Script Connector"

    # SSH connection pool for multi-host environment
    slurm_cluster_to_ssh_conn: Dict[SlurmCluster, SSHClientConnection] = {}

    # Dummy script content
    DUMMY_SCRIPT = "#!/bin/bash"

    def __init__(self) -> None:
        super(SlurmScriptConnector, self).__init__(task_type_name="slurm", metadata_type=SlurmJobMetadata)

    async def create(
        self,
        task_template: TaskTemplate,
        inputs: Optional[LiteralMap] = None,
        **kwargs,
    ) -> SlurmJobMetadata:
        uniq_script_path = f"/tmp/task_{uuid.uuid4().hex}.slurm"
        outputs = {}

        # Retrieve task config
        ssh_config = task_template.custom["ssh_config"]
        batch_script_args = task_template.custom["batch_script_args"]
        sbatch_config = task_template.custom["sbatch_config"]

        # Construct sbatch command for Slurm cluster
        upload_script = False
        if "script" in task_template.custom:
