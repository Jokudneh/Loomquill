import os
from typing import Iterator

import jsonlines
import pytest

from flytekit import task, workflow
from flytekit.types.iterator import JSON

JSONL_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data.jsonl")


def jsons():
    for index, text in enumerate(["One chinhuahua", "A german shepherd"]):
        yield {
            "file_name": f"000{index}.png",
            "text": text,
        }


def jsons_iter():
    return iter(
        [
            x
            for x in (
                {"file_name": "0000.png", "text": "One chinhuahua"},
                {"file_name": "0001.png", "text": "A german shepherd"},
            )
        ]
    )


@task
def jsons_task(x: Iterator[JSON]) -> Iterator[JSON]:
    return x


