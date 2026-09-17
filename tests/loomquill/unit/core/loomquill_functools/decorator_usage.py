from flytekit import task

from .decorator_source import task_setup


@task
@task_setup
