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
    See the documentation for {{< py_class_ref flytekit.reference_task >}} and {{< py_class_ref flytekit.reference_workflow >}} as well.

    This function is the general form of the two aforementioned functions. It's better for programmatic usage, as
    the interface is passed in as arguments instead of analyzed from type annotations.

    <!--
    .. literalinclude:: ../../../tests/flytekit/unit/core/test_references.py
       :start-after: # docs_ref_start
       :end-before: # docs_ref_end
       :language: python
