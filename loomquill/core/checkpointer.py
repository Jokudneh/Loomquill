import io
import tempfile
import typing
from abc import abstractmethod
from pathlib import Path


class Checkpoint(object):
    """
    Base class for Checkpoint system. Checkpoint system allows reading and writing custom checkpoints from user
    scripts
    """

    @abstractmethod
    def prev_exists(self) -> bool:
        raise NotImplementedError("Use one of the derived classes")

    @abstractmethod
    def restore(self, path: typing.Union[Path, str]) -> typing.Optional[Path]:
        """
        Given a path, if a previous checkpoint exists, will be downloaded to this path.
        If download is successful the downloaded path is returned

        > [!NOTE]
        > Download will not be performed, if the checkpoint was previously restored. The method will return the
          previously downloaded path.

        """
        raise NotImplementedError("Use one of the derived classes")

    @abstractmethod
    def save(self, cp: typing.Union[Path, str, io.BufferedReader]):
        """
        Args:
            cp: Checkpoint file (path, str path or a io.BufferedReader)
