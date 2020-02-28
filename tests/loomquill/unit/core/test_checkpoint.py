import os
from pathlib import Path

import pytest

import flytekit
from flytekit.core.checkpointer import SyncCheckpoint
from flytekit.exceptions.user import FlyteDataNotFoundException


def test_sync_checkpoint_write(tmpdir):
    td_path = Path(tmpdir)
    cp = SyncCheckpoint(checkpoint_dest=tmpdir)
    assert cp.read() is None
    assert cp.restore() is None
    dst_path = td_path / SyncCheckpoint.TMP_DST_PATH
    assert not dst_path.exists()
    cp.write(b"bytes")
    assert dst_path.exists()


def test_sync_checkpoint_save_file(tmpdir):
    td_path = Path(tmpdir)
    cp = SyncCheckpoint(checkpoint_dest=tmpdir)
    dst_path = td_path / SyncCheckpoint.TMP_DST_PATH
    assert not dst_path.exists()
    inp = td_path / "test"
    with inp.open("wb") as f:
        f.write(b"blah")
    with inp.open("rb") as f:
        cp.save(f)
    assert dst_path.exists()

    with pytest.raises(ValueError):
        # Unsupported object
        cp.save(SyncCheckpoint)  # noqa


def test_sync_checkpoint_save_filepath(tmpdir):
    src_path = Path(os.path.join(tmpdir, "src"))
    src_path.mkdir(parents=True, exist_ok=True)
    chkpnt_path = Path(os.path.join(tmpdir, "dest"))
    chkpnt_path.mkdir()
    cp = SyncCheckpoint(checkpoint_dest=str(chkpnt_path))
    dst_path = chkpnt_path / "test"
    assert not dst_path.exists()
    inp = src_path / "test"
    with inp.open("wb") as f:
        f.write(b"blah")
    cp.save(inp)
    assert dst_path.exists()

