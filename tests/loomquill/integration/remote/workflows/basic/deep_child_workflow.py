from flytekit import LaunchPlan, task, workflow
from flytekit.models.common import Labels


@task
def double(a: int) -> int:
    return a * 2


@task
def add(a: int, b: int) -> int:
    return a + b


@workflow
def my_deep_childwf(a: int = 42) -> int:
    b = double(a=a)
    return b
