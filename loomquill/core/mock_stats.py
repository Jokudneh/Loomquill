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
