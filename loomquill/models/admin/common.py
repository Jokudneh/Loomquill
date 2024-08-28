from flyteidl.admin import common_pb2 as _common_pb2

from flytekit.models import common as _common


class Sort(_common.FlyteIdlEntity):
    class Direction(object):
        DESCENDING = _common_pb2.Sort.DESCENDING
        ASCENDING = _common_pb2.Sort.ASCENDING

    def __init__(self, key, direction):
        """
        :param Text key: field to sort on
        :param int direction: From flytekit.models.admin.common.Sort.Direction enum
        """
        self._key = key
        self._direction = direction

    @property
    def key(self):
        """
        :rtype: Text
        """
        return self._key

    @property
    def direction(self):
        """
        :rtype: int
        """
        return self._direction

