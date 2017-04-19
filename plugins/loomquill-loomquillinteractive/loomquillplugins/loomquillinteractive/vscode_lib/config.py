# This file has been moved to flytekit.interactive.vscode_lib.config
# Import flytekit.interactive module to keep backwards compatibility
from flytekit.interactive.vscode_lib.config import (  # noqa: F401
    DEFAULT_CODE_SERVER_DIR_NAMES,
    DEFAULT_CODE_SERVER_EXTENSIONS,
    DEFAULT_CODE_SERVER_REMOTE_PATHS,
    VscodeConfig,
)

# Extension URLs for additional extensions
COPILOT_EXTENSION = (
    "https://raw.githubusercontent.com/flyteorg/flytetools/master/flytekitplugins/flyin/GitHub.copilot-1.138.563.vsix"
)
