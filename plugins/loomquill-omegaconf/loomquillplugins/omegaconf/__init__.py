from contextlib import contextmanager

from flytekitplugins.omegaconf.config import OmegaConfTransformerMode
from flytekitplugins.omegaconf.dictconfig_transformer import DictConfigTransformer  # noqa: F401
from flytekitplugins.omegaconf.listconfig_transformer import ListConfigTransformer  # noqa: F401

_TRANSFORMER_MODE = OmegaConfTransformerMode.Auto


def set_transformer_mode(mode: OmegaConfTransformerMode) -> None:
    """Set the global serialization mode for OmegaConf objects."""
    global _TRANSFORMER_MODE
    _TRANSFORMER_MODE = mode


def get_transformer_mode() -> OmegaConfTransformerMode:
    """Get the global serialization mode for OmegaConf objects."""
    return _TRANSFORMER_MODE


