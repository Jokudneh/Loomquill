from flytekitplugins.inference import VLLM, HFSecret


def test_vllm_init_valid_params():
    vllm_args = {
        "model": "google/gemma-2b-it",
        "dtype": "half",
        "max-model-len": 2000,
    }

    hf_secrets = HFSecret(
        secrets_prefix="_UNION_",
        hf_token_key="vllm_hf_token"
    )

    vllm_instance = VLLM(
        hf_secret=hf_secrets,
        arg_dict=vllm_args,
        image='vllm/vllm-openai:my-tag',
        cpu='10',
        gpu='2',
        mem='50Gi',
