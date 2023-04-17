from flytekitplugins.inference import Ollama, Model


def test_ollama_init_valid_params():
    ollama_instance = Ollama(
        mem="30Gi",
        port=11435,
        model=Model(name="mistral-nemo"),
    )

    assert len(ollama_instance.pod_template.pod_spec.init_containers) == 2
    assert (
        ollama_instance.pod_template.pod_spec.init_containers[0].image
        == "ollama/ollama"
    )
    assert (
        ollama_instance.pod_template.pod_spec.init_containers[0].resources.requests[
            "memory"
        ]
        == "30Gi"
    )
    assert (
        ollama_instance.pod_template.pod_spec.init_containers[0].ports[0].container_port
        == 11435
    )
    assert (
        "mistral-nemo"
        in ollama_instance.pod_template.pod_spec.init_containers[1].args[0]
    )
    assert (
        "ollama.pull"
        in ollama_instance.pod_template.pod_spec.init_containers[1].args[0]
