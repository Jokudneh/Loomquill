from __future__ import annotations

from typing import Dict, Type

from flytekit.core.launch_plan import ReferenceLaunchPlan
from flytekit.core.task import ReferenceTask
from flytekit.core.workflow import ReferenceWorkflow
from flytekit.exceptions.user import FlyteValidationException
from flytekit.models.core import identifier as _identifier_model


def get_reference_entity(
    resource_type: int,
    project: str,
    domain: str,
    name: str,
    version: str,
    inputs: Dict[str, Type],
    outputs: Dict[str, Type],
):
    """
