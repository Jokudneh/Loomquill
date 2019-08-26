from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.interface import Interface
from flytekit.extend import TaskPlugins
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin
from flytekit.extras.tasks.shell import OutputLocation
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import FlyteFile


@dataclass
class SlurmConfig(object):
    """
    Configure Slurm settings. Note that we focus on sbatch command now.

    Compared with spark, please refer to:
    https://api-docs.databricks.com/python/pyspark/latest/api/pyspark.SparkContext.html.

    Attributes:
        ssh_config (Dict[str, Any]): Options of SSH client connection. For available options, please refer to
            <newly-added-ssh-utils-file>.
        sbatch_config (Optional[Dict[str, str]]): Options of sbatch command. For available options, please refer to
            https://slurm.schedmd.com/sbatch.html.
        batch_script_args (Optional[List[str]]): Additional args for the batch script on Slurm cluster.
    """

    ssh_config: Dict[str, Any]
    sbatch_config: Optional[Dict[str, str]] = None
    batch_script_args: Optional[List[str]] = None

    def __post_init__(self):
        if self.sbatch_config is None:
            self.sbatch_config = {}


@dataclass
class SlurmScriptConfig(SlurmConfig):
