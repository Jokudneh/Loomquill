from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from flytekit.interactive.vscode_lib.vscode_constants import (
    DEFAULT_CODE_SERVER_DIR_NAMES,
    DEFAULT_CODE_SERVER_EXTENSIONS,
    DEFAULT_CODE_SERVER_REMOTE_PATHS,
)


@dataclass
class VscodeConfig:
    """
    VscodeConfig is the config contains default URLs of the VSCode server and extension remote paths.

