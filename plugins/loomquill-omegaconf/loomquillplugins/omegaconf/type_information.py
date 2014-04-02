import dataclasses
import typing
from collections import ChainMap

from dataclasses_json import DataClassJsonMixin

from flytekit.loggers import logger
from omegaconf import DictConfig, ListConfig, OmegaConf

NoneType = type(None)


def substitute_types(t: typing.Type) -> typing.Type:
    """
    Provides a substitute type hint to use when selecting transformers for serialisation.

    :param t: Original type
    :return: A corrected typehint
    """
    if hasattr(t, "__origin__"):
        # Only encode generic type and let appropriate transformer handle the rest
