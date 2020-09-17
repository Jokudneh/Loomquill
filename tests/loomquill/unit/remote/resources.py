from flytekit import task, workflow


@task
def say_hello(a: int) -> str:
