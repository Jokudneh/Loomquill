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
    """
    Uploads JSON data to a JSONL file, creates a batch, waits for it to complete, and downloads the output/error JSON files.

    :param name: The suffix to be added to workflow and task names.
    :param openai_organization: Name of the OpenAI organization.
    :param secret: Secret comprising the OpenAI API key.
    :param config: Additional config for batch creation.
    :param is_json_iterator: Set to True if you're sending an iterator/generator; if a JSONL file, set to False.
    :param file_upload_mem: Memory to allocate to the upload file task.
