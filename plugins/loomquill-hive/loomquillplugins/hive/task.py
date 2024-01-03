from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type

from google.protobuf.json_format import MessageToDict

from flytekit.configuration import SerializationSettings
from flytekit.extend import SQLTask
from flytekit.models.qubole import HiveQuery, QuboleHiveJob
from flytekit.types.schema import FlyteSchema


@dataclass
class HiveConfig(object):
    """
    HiveConfig should be used to configure a Hive Task. Config values are statically defined during the construction
    of a task, and are not parameterized.
    Note: A separate story is in progress to dynamically alter configuration for an execution launch.

    Args:
        cluster_label: A string value that helps in identifying the cluster label.
        tags: Any tags that should be associated with the remote execution request.
    """

    cluster_label: str = ""
    tags: Optional[List[str]] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
