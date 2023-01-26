import os
from unittest import mock
from unittest.mock import MagicMock, mock_open

import pytest
from flytekitplugins.async_fsspec import AsyncS3FileSystem
from flytekitplugins.async_fsspec.s3fs.constants import DEFAULT_DOWNLOAD_CHUNK_SIZE, DEFAULT_UPLOAD_CHUNK_SIZE


@mock.patch("flytekitplugins.async_fsspec.AsyncS3FileSystem._parent")
@mock.patch("flytekitplugins.async_fsspec.AsyncS3FileSystem.invalidate_cache")
@mock.patch("flytekitplugins.async_fsspec.AsyncS3FileSystem._call_s3")
@mock.patch("mimetypes.guess_type")
@mock.patch("os.path.getsize")
@pytest.mark.asyncio
async def test_put_file_single_object_upload(
    mock_getsize, mock_guess_type, mock_call_s3, mock_invalidate_cache, mock_parent
):
    mock_bucket = "mock-bucket"
    mock_file_name = "mock_file_name"
    mock_file_size = 32 * 2**20  # 32MB
    mock_getsize.return_value = mock_file_size
    mock_guess_type.return_value = (None, None)
    mock_parent.return_value = None
    mock_body = os.urandom(mock_file_size)
    m = mock_open(read_data=mock_body)

    with mock.patch("builtins.open", m):
        asyncs3fs = AsyncS3FileSystem()
        await asyncs3fs._put_file(lpath=f"/{mock_file_name}", rpath=f"s3://{mock_bucket}/{mock_file_name}")

    mock_call_s3.assert_called_once_with("put_object", Bucket=mock_bucket, Key=mock_file_name, Body=mock_body)


@mock.patch("flytekitplugins.async_fsspec.AsyncS3FileSystem._parent")
@mock.patch("flytekitplugins.async_fsspec.AsyncS3FileSystem.invalidate_cache")
@mock.patch("flytekitplugins.async_fsspec.AsyncS3FileSystem._call_s3")
@mock.patch("mimetypes.guess_type")
@mock.patch("os.path.getsize")
@pytest.mark.asyncio
async def test_put_file_multipart_upload(
    mock_getsize, mock_guess_type, mock_call_s3, mock_invalidate_cache, mock_parent
):
    mock_bucket = "mock-bucket"
    mock_file_name = "mock_file_name"
    mock_upload_id = "mock_upload_id"
    mock_ETag = "mock_ETag"
    mock_file_size = 256 * 2**20  # 256MB
    mock_getsize.return_value = mock_file_size
    mock_guess_type.return_value = (None, None)

    def call_s3_side_effect(*args, **kwargs):
        if args[0] == "create_multipart_upload":
            return {"UploadId": mock_upload_id}
        elif args[0] == "upload_part":
            part_number = kwargs["PartNumber"]
            return {"ETag": f"{mock_ETag}{part_number}"}
        elif args[0] == "complete_multipart_upload":
            return None

    mock_call_s3.side_effect = call_s3_side_effect

    mock_parent.return_value = None

    mock_body = os.urandom(mock_file_size)
    m = mock_open(read_data=mock_body)

    with mock.patch("builtins.open", m):
        asyncs3fs = AsyncS3FileSystem()
        await asyncs3fs._put_file(lpath=f"/{mock_file_name}", rpath=f"s3://{mock_bucket}/{mock_file_name}")

    mock_chunk_count = mock_file_size // DEFAULT_UPLOAD_CHUNK_SIZE
    if mock_file_size % DEFAULT_UPLOAD_CHUNK_SIZE > 0:
        mock_chunk_count += 1
    put_object_calls = []
    for i in range(mock_chunk_count):
        part_number = i + 1
        start_byte = i * DEFAULT_UPLOAD_CHUNK_SIZE
        end_byte = min(start_byte + DEFAULT_UPLOAD_CHUNK_SIZE, mock_file_size)
        body = mock_body[start_byte:end_byte]
        put_object_calls.append(
