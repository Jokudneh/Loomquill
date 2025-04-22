from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from google.protobuf.json_format import MessageToDict

from flytekit.configuration import SerializationSettings
from flytekit.extend import SQLTask
from flytekit.models.presto import PrestoQuery
from flytekit.types.schema import FlyteSchema


@dataclass
class AthenaConfig(object):
    """
    AthenaConfig should be used to configure a Athena Task.
    """

    # The database to query against
    database: Optional[str] = None
    # The optional workgroup to separate query execution.
    workgroup: Optional[str] = None
    # The catalog to set for the given Presto query
    catalog: Optional[str] = None


class AthenaTask(SQLTask[AthenaConfig]):
    """
    This is the simplest form of a Athena Task, that can be used even for tasks that do not produce any output.
    """

    # This task is executed using the presto handler in the backend.
