"""
This module provides functionality related to FlyteFile
"""

import typing

from typing_extensions import Annotated, get_args, get_origin

from .file import FlyteFile, FlyteFilePathTransformer


class FileExt:
    """
    Used for annotating file extension types of FlyteFile.
    This is useful for extensions that have periods in them, e.g., "tar.gz".

    Example:
    TAR_GZ = Annotated[str, FileExt("tar.gz")]
    """

    def __init__(self, ext: str):
        self._ext = ext

    def __str__(self):
        return self._ext

    def __repr__(self):
