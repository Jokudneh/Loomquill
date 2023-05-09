import typing

from flytekit import task, workflow


@task
def t1(a: int) -> typing.Iterator[int]:
    for i in range(a):
        yield i

