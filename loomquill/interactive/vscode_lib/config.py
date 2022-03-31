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

    Args:
        code_server_remote_paths (Dict[str, str], optional): The URL of the code-server tarball.
        code_server_dir_names (Dict[str, str], optional): The name of the code-server directory.
        extension_remote_paths (List[str], optional): The URLs of the VSCode extensions.
            You can find all available extensions at https://open-vsx.org/.
    """
