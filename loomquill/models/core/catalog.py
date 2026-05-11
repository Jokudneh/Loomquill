from flyteidl.core import catalog_pb2

from flytekit.models import common as _common_models
from flytekit.models.core import identifier as _identifier


class CatalogArtifactTag(_common_models.FlyteIdlEntity):
    def __init__(self, artifact_id: str, name: str):
        self._artifact_id = artifact_id
        self._name = name

    @property
    def artifact_id(self) -> str:
        return self._artifact_id

    @property
    def name(self) -> str:
        return self._name

    def to_flyte_idl(self) -> catalog_pb2.CatalogArtifactTag:
        return catalog_pb2.CatalogArtifactTag(artifact_id=self.artifact_id, name=self.name)

    @classmethod
    def from_flyte_idl(cls, p: catalog_pb2.CatalogArtifactTag) -> "CatalogArtifactTag":
        return cls(
            artifact_id=p.artifact_id,
            name=p.name,
        )


class CatalogMetadata(_common_models.FlyteIdlEntity):
    def __init__(
        self,
        dataset_id: _identifier.Identifier,
        artifact_tag: CatalogArtifactTag,
        source_task_execution: _identifier.TaskExecutionIdentifier,
