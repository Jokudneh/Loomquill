"""
This is a deprecated module. Model files for plugins should go alongside the microlib.
See ``plugins/flytekit-kf-pytorch/flytekitplugins/kfpytorch/models.py`` as an example.
"""

from flyteidl.plugins import qubole_pb2 as _qubole

from flytekit.models import common as _common


class HiveQuery(_common.FlyteIdlEntity):
    def __init__(self, query, timeout_sec, retry_count):
        """
        Initializes a new HiveQuery.

        :param Text query: The query string.
        :param int timeout_sec:
        :param int retry_count:

        """
        self._query = query
        self._timeout_sec = timeout_sec
        self._retry_count = retry_count

    @property
    def query(self):
        """
        The query string.
        :rtype: str
        """
        return self._query

    @property
    def timeout_sec(self):
        """
        :rtype: int
        """
        return self._timeout_sec

    @property
    def retry_count(self):
        """
        :rtype: int
        """
        return self._retry_count

    def to_flyte_idl(self):
        """
        :rtype: _qubole.HiveQuery
        """
