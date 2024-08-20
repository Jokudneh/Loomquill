import typing

from flytekit import task, workflow


@task
def t1(a: int) -> typing.Iterator[int]:
    for i in range(a):
        yield i


@task
def t2(ls: typing.Iterator[int]) -> typing.List[int]:
