from flytekit import task, workflow


@task
def t(m: str) -> str:
    return m

