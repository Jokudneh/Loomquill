from flytekitplugins.openai import create_batch

from flytekit import Secret


def test_openai_batch_wf():
    openai_batch_wf = create_batch(
