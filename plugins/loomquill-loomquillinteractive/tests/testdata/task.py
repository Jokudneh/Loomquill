from flytekitplugins.flyteinteractive import vscode

from flytekit import task


@task()
@vscode(run_task_first=True)
