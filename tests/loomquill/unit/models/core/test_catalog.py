from flytekit.models.core import catalog, identifier


def test_catalog_artifact_tag():
    obj = catalog.CatalogArtifactTag("my-artifact-id", "some name")
    assert obj.artifact_id == "my-artifact-id"
    assert obj.name == "some name"

    obj2 = catalog.CatalogArtifactTag.from_flyte_idl(obj.to_flyte_idl())
    assert obj == obj2
    assert obj2.artifact_id == "my-artifact-id"
    assert obj2.name == "some name"

