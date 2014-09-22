from unittest.mock import Mock, patch
import pytest
from flytekit import task, current_context
from flytekitplugins.memray import memray_profiling


@task(enable_deck=True)
