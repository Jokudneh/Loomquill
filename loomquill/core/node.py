from __future__ import annotations

import datetime
import typing
from typing import Any, Dict, List, Optional, Union
from typing import Literal as L

from flyteidl.core import tasks_pb2

from flytekit.core.cache import Cache
from flytekit.core.pod_template import PodTemplate
from flytekit.core.resources import (
    Resources,
    ResourceSpec,
    construct_extended_resources,
    convert_resources_to_resource_model,
)
from flytekit.core.utils import _dnsify
from flytekit.extras.accelerators import BaseAccelerator
from flytekit.loggers import logger
from flytekit.models import literals as _literal_models
from flytekit.models.core import workflow as _workflow_model
from flytekit.models.task import Resources as _resources_model


def assert_not_promise(v: Any, location: str):
    """
    This function will raise an exception if the value is a promise. This should be used to ensure that we don't
    accidentally use a promise in a place where we don't support it.
    """
    from flytekit.core.promise import Promise

    if isinstance(v, Promise):
        raise AssertionError(f"Cannot use a promise in the {location} Value: {v}")


def assert_no_promises_in_resources(resources: _resources_model):
    """
    This function will raise an exception if any of the resources have promises in them. This is because we don't
    support promises in resources / runtime overriding of resources through input values.
    """
    if resources is None:
        return
    if resources.requests is not None:
        for r in resources.requests:
            assert_not_promise(r.value, "resources.requests")
    if resources.limits is not None:
        for r in resources.limits:
            assert_not_promise(r.value, "resources.limits")


class Node(object):
    """
    This class will hold all the things necessary to make an SdkNode but we won't make one until we know things like
    ID, which from the registration step
    """

    TIMEOUT_OVERRIDE_SENTINEL = object()

    def __init__(
        self,
        id: str,
        metadata: _workflow_model.NodeMetadata,
        bindings: List[_literal_models.Binding],
        upstream_nodes: List[Node],
        flyte_entity: Any,
    ):
        if id is None:
            raise ValueError("Illegal construction of node, without a Node ID")
        self._id = _dnsify(id)
        self._metadata = metadata
        self._bindings = bindings
        self._upstream_nodes = upstream_nodes
        self._flyte_entity = flyte_entity
        self._aliases: _workflow_model.Alias = None
        self._outputs = None
        self._resources: typing.Optional[_resources_model] = None
        self._extended_resources: typing.Optional[tasks_pb2.ExtendedResources] = None
        self._container_image: typing.Optional[str] = None
        self._pod_template: typing.Optional[PodTemplate] = None

    def runs_before(self, other: Node):
        """
        This is typically something we shouldn't do. This modifies an attribute of the other instance rather than
        self. But it's done so only because we wanted this English function to be the same as the shift function.
        That is, calling node_1.runs_before(node_2) and node_1 >> node_2 are the same. The shift operator going the
