import pytest
import sys
import timeit
import asyncio

from datetime import timedelta
from flytekit.utils.rate_limiter import RateLimiter


async def launch_requests(rate_limiter: RateLimiter, total: int):
    tasks = [asyncio.create_task(rate_limiter.acquire()) for _ in range(total)]
    await asyncio.gather(*tasks)


async def helper_for_async(rpm: int, total: int):
    rate_limiter = RateLimiter(rpm=rpm)
    rate_limiter.delay = timedelta(seconds=1)
    await launch_requests(rate_limiter, total)

