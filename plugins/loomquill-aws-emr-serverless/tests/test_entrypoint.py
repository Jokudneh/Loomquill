"""
Unit tests for the EMR Serverless Pythonic-mode entrypoint script.

These tests exercise the entrypoint module on two levels:

* **Pure unit tests** of the helper functions (``_parse_fast_execute_args``,
  ``_build_resolver_command``, ``_exit_with_code``) by importing them
  directly.  These are fast, deterministic, and require no subprocess.
* **Subprocess tests** that run ``python -m`` on the actual file the
  connector uploads to S3, verifying the wire-level CLI behaviour EMR
  will see.

The shape of these tests mirrors how Databricks's ``flytetools``
maintains test coverage for ``flytekitplugins/databricks/entrypoint.py``.
"""

import hashlib
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from flytekitplugins.awsemrserverless import _entrypoint


ENTRYPOINT_PATH: Path = Path(_entrypoint.__file__).resolve()


# ---------------------------------------------------------------------------
# Module-level invariants
# ---------------------------------------------------------------------------


class TestEntrypointModuleInvariants:
    """Sanity checks on the entrypoint module itself."""

    def test_entrypoint_file_exists(self):
        assert ENTRYPOINT_PATH.is_file(), (
            f"_entrypoint.py must exist at {ENTRYPOINT_PATH}; the connector uploads this file to S3 and EMR runs it."
        )

    def test_entrypoint_is_valid_python(self):
        source = ENTRYPOINT_PATH.read_text()
        compile(source, str(ENTRYPOINT_PATH), "exec")

    def test_entrypoint_has_main(self):
        assert callable(_entrypoint.main)

    def test_entrypoint_minimal_runtime_imports(self):
        """The entrypoint runs inside the EMR worker; its module-level
        imports must be available there.  ``flytekit`` is the only
        non-stdlib module we should import (specifically
        ``download_distribution``)."""
        source = ENTRYPOINT_PATH.read_text()
        assert "from flytekit.tools.fast_registration import download_distribution" in source
        assert "import boto3" not in source, (
            "_entrypoint.py must not import boto3 -- it runs in the EMR "
            "worker which may not have boto3 installed at the version "
            "the connector uses."
        )


# ---------------------------------------------------------------------------
# _parse_fast_execute_args
# ---------------------------------------------------------------------------


class TestParseFastExecuteArgs:
    """The parser splits a ``pyflyte-fast-execute ...`` argv into its parts."""

    def test_full_argv(self):
        args = [
