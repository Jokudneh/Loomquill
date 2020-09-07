import sys

import pytest

from flytekit.deck.renderer import DEFAULT_MAX_COLS, DEFAULT_MAX_ROWS, ArrowRenderer, TopFrameRenderer


@pytest.mark.skipif("pyarrow" not in sys.modules, reason="Pyarrow is not installed.")
@pytest.mark.skipif("pandas" not in sys.modules, reason="Pandas is not installed.")
