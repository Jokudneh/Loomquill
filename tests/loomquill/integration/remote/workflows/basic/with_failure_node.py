import typing

import flytekit as fl
from flytekit import WorkflowFailurePolicy
from flytekit.types.error.error import FlyteError


@fl.task
def create_cluster(name: str):
    print(f"Creating cluster: {name}")
