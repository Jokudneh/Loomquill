import asyncio
import mimetypes
import os
from typing import Any, Callable, Optional

from fsspec.callbacks import _DEFAULT_CALLBACK
from s3fs import S3FileSystem
from s3fs.core import S3_RETRYABLE_ERRORS, version_id_kw

from .constants import (
    DEFAULT_CONCURRENT_DOWNLOAD,
    DEFAULT_CONCURRENT_UPLOAD,
    DEFAULT_DOWNLOAD_BODY_READ_SIZE,
    DEFAULT_DOWNLOAD_CHUNK_SIZE,
    DEFAULT_UPLOAD_CHUNK_SIZE,
    SINGLE_OBJECT_UPLOAD_LIMIT,
)


class AsyncS3FileSystem(S3FileSystem):
    def __init__(self, **s3kwargs):
        super().__init__(**s3kwargs)

    async def _put_file(
        self,
        lpath: str,
        rpath: str,
        callback: Callable = _DEFAULT_CALLBACK,
        chunksize: int = DEFAULT_UPLOAD_CHUNK_SIZE,
        concurrent_upload: int = DEFAULT_CONCURRENT_UPLOAD,
        **kwargs: Any,
    ):
        """
        Put a file from lpath to rpath.
        Args:
            lpath (str): The local path of the file to be uploaded.
            rpath (str): The remote path which the file should be uploaded to.
            callback (Callable): The callback function.
            chunksize (int): Upload chunksize. Defaults to 50 * 2**20 (50MB).
            concurrent_upload (int): The number of concurrent upload when using multipart upload. Defaults to 4.
            **kwargs (Any): Additional arguments passed to S3 calls.
        """
        bucket, key, _ = self.split_path(rpath)
        if os.path.isdir(lpath):
            if key:
                # don't make remote "directory"
                return
            else:
                await self._mkdir(lpath)
        size = os.path.getsize(lpath)
        callback.set_size(size)

        if "ContentType" not in kwargs:
            content_type, _ = mimetypes.guess_type(lpath)
            if content_type is not None:
                kwargs["ContentType"] = content_type

        with open(lpath, "rb") as f0:
            if size < min(SINGLE_OBJECT_UPLOAD_LIMIT, 2 * chunksize):
