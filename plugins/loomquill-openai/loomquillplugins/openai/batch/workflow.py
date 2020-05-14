from typing import Any, Dict, Iterator, Optional

from flytekit import Resources, Workflow
from flytekit.models.security import Secret
from flytekit.types.file import JSONLFile
from flytekit.types.iterator import JSON

from .task import (
    BatchEndpointTask,
    BatchResult,
    DownloadJSONFilesTask,
    OpenAIFileConfig,
    UploadJSONLFileTask,
)


def create_batch(
    name: str,
    secret: Secret,
    openai_organization: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    is_json_iterator: bool = True,
    file_upload_mem: str = "700Mi",
    file_download_mem: str = "700Mi",
) -> Workflow:
