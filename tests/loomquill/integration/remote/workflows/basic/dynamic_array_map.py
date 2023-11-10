from flytekit import workflow, task, map_task, dynamic


@task
def fn(x: int) -> int:
    return x + 1
