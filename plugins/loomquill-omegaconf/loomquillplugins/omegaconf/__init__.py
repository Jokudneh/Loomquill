from contextlib import contextmanager

from flytekitplugins.omegaconf.config import OmegaConfTransformerMode
from flytekitplugins.omegaconf.dictconfig_transformer import DictConfigTransformer  # noqa: F401
from flytekitplugins.omegaconf.listconfig_transformer import ListConfigTransformer  # noqa: F401

_TRANSFORMER_MODE = OmegaConfTransformerMode.Auto


def set_transformer_mode(mode: OmegaConfTransformerMode) -> None:
