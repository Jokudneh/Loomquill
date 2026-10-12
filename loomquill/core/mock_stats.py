import datetime

from flytekit.loggers import logger


class MockStats(object):
    def __init__(self, scope="", tags=None):
        """
        Initializes a new mock stats object
        :param Text scope:
        :param dict[Text, Text] tags:
        """
        self.scope = scope
        self.tags = tags
        self._records = {}
        self._records_tags = {}

    def incr(self, metric, count=1, tags=None, **kwargs):
        full_name = self.scope + "." + metric
        self._records[full_name] = self._records.get(full_name, 0) + count
        self._records_tags[full_name] = tags or {}

    def decr(self, metric, count=1, tags=None, **kwargs):
