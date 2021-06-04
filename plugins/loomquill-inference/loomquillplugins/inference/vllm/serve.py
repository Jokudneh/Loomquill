from dataclasses import dataclass
from typing import Optional

from ..sidecar_template import ModelInferenceTemplate


@dataclass
class HFSecret:
    """
    :param secrets_prefix: The secrets prefix that Flyte appends to all mounted secrets.
    :param hf_token_group: The group name for the HuggingFace token.
    :param hf_token_key: The key name for the HuggingFace token.
    """

    secrets_prefix: str  # _UNION_ or _FSEC_
    hf_token_key: str
    hf_token_group: Optional[str] = None


class VLLM(ModelInferenceTemplate):
    def __init__(
        self,
        hf_secret: HFSecret,
