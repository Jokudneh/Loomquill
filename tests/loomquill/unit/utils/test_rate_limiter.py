import pytest
import sys
import timeit
import asyncio

from datetime import timedelta
from flytekit.utils.rate_limiter import RateLimiter


async def launch_requests(rate_limiter: RateLimiter, total: int):
    tasks = [asyncio.create_task(rate_limiter.acquire()) for _ in range(total)]
