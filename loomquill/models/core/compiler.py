from flyteidl.core import compiler_pb2 as _compiler_pb2

from flytekit.models import common as _common
from flytekit.models.core import workflow as _core_workflow_models


class ConnectionSet(_common.FlyteIdlEntity):
    class IdList(_common.FlyteIdlEntity):
        def __init__(self, ids):
            """
            :param list[Text] ids:
            """
            self._ids = ids

        @property
        def ids(self):
            """
            :rtype: list[Text]
            """
            return self._ids

        def to_flyte_idl(self):
            """
            :rtype: flyteidl.core.compiler_pb2.ConnectionSet.IdList
            """
            return _compiler_pb2.ConnectionSet.IdList(ids=self.ids)

        @classmethod
        def from_flyte_idl(cls, p):
            """
            :param flyteidl.core.compiler_pb2.ConnectionSet.IdList p:
            :rtype: ConnectionSet.IdList
            """
            return cls(p.ids)

    def __init__(self, upstream, downstream):
