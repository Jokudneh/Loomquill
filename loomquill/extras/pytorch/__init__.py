"""
This module provides functionality related tp PyTorch
"""

from flytekit.loggers import logger

# TODO: abstract this out so that there's an established pattern for registering plugins
# that have soft dependencies
try:
    # isolate the exception to the torch import
    import torch

    _torch_installed = True
except (ImportError, OSError):
    _torch_installed = False
