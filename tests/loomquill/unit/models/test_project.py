import pytest

from flytekit.models import project


def test_project_with_default_state():
    obj = project.Project("project_id", "project_name", "project_description")
    assert obj.id == "project_id"
