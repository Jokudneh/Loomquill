from flytekit.models import named_entity


def test_identifier():
    obj = named_entity.NamedEntityIdentifier("proj", "development", "MyWorkflow")
