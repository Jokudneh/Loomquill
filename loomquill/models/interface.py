import typing

from flyteidl.core import artifact_id_pb2 as art_id
from flyteidl.core import interface_pb2 as _interface_pb2
from flyteidl.core import types_pb2 as _types_pb2

from flytekit.models import common as _common
from flytekit.models import literals as _literals
from flytekit.models import types as _types


class Variable(_common.FlyteIdlEntity):
    def __init__(
        self,
        type,
        description,
        artifact_partial_id: typing.Optional[art_id.ArtifactID] = None,
        artifact_tag: typing.Optional[art_id.ArtifactTag] = None,
    ):
        """
        :param flytekit.models.types.LiteralType type: This describes the type of value that must be provided to
            satisfy this variable.
        :param Text description: This is a help string that can provide context for what this variable means in relation
            to a task or workflow.
        :param artifact_partial_id: Optional Artifact object to control how the artifact is created when the task runs.
        :param artifact_tag: Optional ArtifactTag object to automatically tag things.
        """
        self._type = type
        self._description = description
        self._artifact_partial_id = artifact_partial_id
        self._artifact_tag = artifact_tag

    @property
    def type(self):
        """
        This describes the type of value that must be provided to satisfy this variable.
        :rtype: flytekit.models.types.LiteralType
        """
        return self._type

    @property
    def description(self):
        """
        This is a help string that can provide context for what this variable means in relation to a task or workflow.
        :rtype: Text
        """
        return self._description

    @property
    def artifact_partial_id(self) -> typing.Optional[art_id.ArtifactID]:
        return self._artifact_partial_id
