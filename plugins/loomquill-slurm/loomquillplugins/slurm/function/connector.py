import json
import tempfile
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

from asyncssh import SSHClientConnection
from asyncssh.sftp import SFTPNoSuchFile

from flytekit.extend.backend.base_connector import AsyncConnectorBase, ConnectorRegistry, Resource, ResourceMeta
from flytekit.extend.backend.utils import convert_to_flyte_phase
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate

from ..ssh_utils import SlurmCluster, get_ssh_conn


@dataclass
class SlurmJobMetadata(ResourceMeta):
    """Slurm job metadata.

    Args:
        job_id: Slurm job id.
        ssh_config: Options of SSH client connection. For available options, please refer to
            the ssh_utils module.

    Attributes:
        job_id (str): Slurm job id.
        ssh_config (Dict[str, Union[str, List[str], Tuple[str, ...]]]): SSH configuration options
            for establishing client connections.
    """

    job_id: str
