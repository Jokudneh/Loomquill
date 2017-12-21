from flytekit import PodTemplate, task
from flytekit.configuration import SerializationSettings, ImageConfig, Image


def test_mutation():
    pod_template_before = PodTemplate(
        labels={"lKeyA": "lValA", "lKeyB": "lValB"},
