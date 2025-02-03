from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from flytekit import FlyteContextManager, PythonFunctionTask
from flytekit.configuration import SerializationSettings
from flytekit.extend import TaskPlugins
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin
from flytekit.image_spec import ImageSpec


@dataclass
class SlurmFunctionConfig(object):
    """Configure Slurm settings. Note that we focus on sbatch command now.

    Args:
        ssh_config: Options of SSH client connection. For available options, please refer to
            <newly-added-ssh-utils-file>
