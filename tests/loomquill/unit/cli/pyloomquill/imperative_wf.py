import typing

from flytekit import Workflow, task


@task
def t1(a: str) -> str:
    return a + " world"

