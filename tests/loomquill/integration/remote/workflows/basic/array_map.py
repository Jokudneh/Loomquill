import typing
from functools import partial

from flytekit import map_task, task, workflow


@task
def fn(x: int, y: int) -> int:
