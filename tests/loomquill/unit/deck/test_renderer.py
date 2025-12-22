import sys

import pytest

from flytekit.deck.renderer import DEFAULT_MAX_COLS, DEFAULT_MAX_ROWS, ArrowRenderer, TopFrameRenderer


@pytest.mark.skipif("pyarrow" not in sys.modules, reason="Pyarrow is not installed.")
@pytest.mark.skipif("pandas" not in sys.modules, reason="Pandas is not installed.")
@pytest.mark.parametrize(
    "rows, cols, max_rows, expected_max_rows, max_cols, expected_max_cols",
    [
        (1, 1, None, DEFAULT_MAX_ROWS, None, DEFAULT_MAX_COLS),
        (10, 1, None, DEFAULT_MAX_ROWS, None, DEFAULT_MAX_COLS),
        (1, 10, None, DEFAULT_MAX_ROWS, None, DEFAULT_MAX_COLS),
        (DEFAULT_MAX_ROWS + 1, 10, None, DEFAULT_MAX_ROWS, None, DEFAULT_MAX_COLS),
