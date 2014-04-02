"""
Utilities of asyncssh connections.
"""

import os
import sys
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union

import asyncssh
from asyncssh import SSHClientConnection

from flytekit import logger
from flytekit.extend.backend.utils import get_connector_secret

T = TypeVar("T", bound="SSHConfig")
SLURM_PRIVATE_KEY = "FLYTE_SLURM_PRIVATE_KEY"


@dataclass
class SlurmCluster:
    """A Slurm cluster instance is defined by a pair of (Slurm host, username).

    Attributes:
        host (str): The hostname or address to connect to.
        username (Optional[str]): The username to authenticate as on the server.
    """

    host: str
    username: Optional[str] = None

    def __hash__(self):
