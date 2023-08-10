import os
import sys
import traceback
from functools import wraps as _wraps
from sys import exc_info as _exc_info
from traceback import format_tb as _format_tb
from warnings import warn

import flytekit
from flytekit.exceptions import base as _base_exceptions
from flytekit.exceptions import system as _system_exceptions
from flytekit.exceptions import user as _user_exceptions
from flytekit.loggers import is_rich_logging_enabled
from flytekit.models.core import errors as _error_model


class FlyteScopedException(Exception):
    def __init__(self, context, exc_type, exc_value, exc_tb, top_trim=0, bottom_trim=0, kind=None):
        warn(f"{self.__class__.__name__} is deprecated.", DeprecationWarning, stacklevel=2)
        self._exc_type = exc_type
        self._exc_value = exc_value
        self._exc_tb = exc_tb
        self._top_trim = top_trim
        self._bottom_trim = bottom_trim
        self._context = context
        self._kind = kind
        super(FlyteScopedException, self).__init__(str(self.value))

    @property
    def verbose_message(self):
        tb = self.traceback
        to_trim = self._top_trim
        while to_trim > 0 and tb.tb_next is not None:
            tb = tb.tb_next

        top_tb = tb
        limit = 0
        while tb is not None:
            limit += 1
            tb = tb.tb_next
        limit = max(0, limit - self._bottom_trim)

        lines = _format_tb(top_tb, limit=limit)
        lines = [line.rstrip() for line in lines]
        traceback_str = "\n    ".join([""] + lines)

        format_str = "Traceback (most recent call last):\n" "{traceback}\n" "\n" "Message:\n" "\n" "    {message}"
        return format_str.format(traceback=traceback_str, message=f"{self.type.__name__}: {self.value}")

    def __str__(self):
        return str(self.value)

    @property
    def value(self):
        if isinstance(self._exc_value, FlyteScopedException):
            return self._exc_value.value
        return self._exc_value

    @property
    def traceback(self):
        if isinstance(self._exc_value, FlyteScopedException):
            return self._exc_value.traceback
        return self._exc_tb
