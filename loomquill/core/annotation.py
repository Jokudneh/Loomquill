from typing import Any, Dict


class FlyteAnnotation:
    """A core object to add arbitrary annotations to flyte types.

    This metadata is ingested as a python dictionary and will be serialized
    into fields on the flyteidl type literals. This data is not accessible at
    runtime but rather can be retrieved from flyteadmin for custom presentation
    of typed parameters.
