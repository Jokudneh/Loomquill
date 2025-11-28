import json
import typing

from flytekit import task, workflow


@task
def convert_to_string(d: typing.Dict[str, str]) -> str:
