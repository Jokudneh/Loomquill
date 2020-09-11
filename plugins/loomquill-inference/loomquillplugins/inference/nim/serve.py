from dataclasses import dataclass
from typing import Optional

from ..sidecar_template import ModelInferenceTemplate


@dataclass
class NIMSecrets:
    """
    :param ngc_secret_key: The key name for the NGC API key.
    :param secrets_prefix: The secrets prefix that Flyte appends to all mounted secrets.
    :param ngc_image_secret: The name of the Kubernetes secret containing the NGC image pull credentials.
    :param ngc_secret_group: The group name for the NGC API key.
    :param hf_token_group: The group name for the HuggingFace token.
    :param hf_token_key: The key name for the HuggingFace token.
    """

    ngc_secret_key: str
    secrets_prefix: str  # _UNION_ or _FSEC_
    ngc_image_secret: Optional[str] = None  # image pull kubernetes secret
    ngc_secret_group: Optional[str] = None
    hf_token_group: Optional[str] = None
    hf_token_key: Optional[str] = None


class NIM(ModelInferenceTemplate):
    def __init__(
        self,
        secrets: NIMSecrets,
        image: str = "nvcr.io/nim/meta/llama3-8b-instruct:1.0.0",
        health_endpoint: str = "v1/health/ready",
        port: int = 8000,
        cpu: int = 1,
        gpu: int = 1,
        mem: str = "20Gi",
        ephemeral_storage: str = "20Gi",
        shm_size: str = "16Gi",
        env: Optional[
            dict[str, str]
        ] = None,  # https://docs.nvidia.com/nim/large-language-models/latest/configuration.html#environment-variables
        hf_repo_ids: Optional[list[str]] = None,
        lora_adapter_mem: Optional[str] = None,
    ):
        """
        Initialize NIM class for managing a Kubernetes pod template.

        :param image: The Docker image to be used for the model server container. Default is "nvcr.io/nim/meta/llama3-8b-instruct:1.0.0".
        :param health_endpoint: The health endpoint for the model server container. Default is "v1/health/ready".
        :param port: The port number for the model server container. Default is 8000.
        :param cpu: The number of CPU cores requested for the model server container. Default is 1.
        :param gpu: The number of GPU cores requested for the model server container. Default is 1.
        :param mem: The amount of memory requested for the model server container. Default is "20Gi".
        :param ephemeral_storage: The amount of ephemeral storage requested for the model server container. Default is "20Gi".
        :param shm_size: The size of the shared memory volume. Default is "16Gi".
        :param env: A dictionary of environment variables to be set in the model server container.
        :param hf_repo_ids: A list of Hugging Face repository IDs for LoRA adapters to be downloaded.
        :param lora_adapter_mem: The amount of memory requested for the init container that downloads LoRA adapters.
        :param secrets: Instance of NIMSecrets for managing secrets.
        """
