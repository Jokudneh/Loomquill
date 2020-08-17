import os
from pathlib import Path

# Where the code-server tar and plugins are downloaded to
EXECUTABLE_NAME = "code-server"
DOWNLOAD_DIR = Path.home() / ".code-server"
HOURS_TO_SECONDS = 60 * 60
DEFAULT_UP_SECONDS = 10 * HOURS_TO_SECONDS  # 10 hours
DEFAULT_CODE_SERVER_REMOTE_PATHS = {
