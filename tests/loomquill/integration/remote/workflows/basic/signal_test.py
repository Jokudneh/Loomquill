from datetime import timedelta
from flytekit import task, workflow, wait_for_input, approve, conditional
import typing

@task
def reporting_wf(title_input: str, data: typing.List[float]) -> dict:
