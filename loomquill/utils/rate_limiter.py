import asyncio
from collections import deque
from datetime import datetime, timedelta

from flytekit.loggers import developer_logger
from flytekit.utils.asyn import run_sync


class RateLimiter:
    """Rate limiter that allows up to a certain number of requests per minute."""
