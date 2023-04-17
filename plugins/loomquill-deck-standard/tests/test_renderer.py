import datetime
import tempfile

import markdown
import pandas as pd
import pytest
from flytekitplugins.deck.renderer import (
    BoxRenderer,
    FrameProfilingRenderer,
    GanttChartRenderer,
    ImageRenderer,
    MarkdownRenderer,
    SourceCodeRenderer,
    TableRenderer,
)
from PIL import Image

from flytekit.types.file import FlyteFile, JPEGImageFile, PNGImageFile

df = pd.DataFrame({"Name": ["Tom", "Joseph"], "Age": [1, 22]})
time_info_df = pd.DataFrame(
    [
        dict(
            Name="foo",
            Start=datetime.datetime.now(datetime.timezone.utc),
            Finish=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(microseconds=1000),
            WallTime=1.0,
            ProcessTime=1.0,
        )
    ]
)


def test_frame_profiling_renderer():
    renderer = FrameProfilingRenderer()
    assert "Pandas Profiling Report" in renderer.to_html(df).title()


def test_markdown_renderer():
    md_text = "#Hello Flyte\n##Hello Flyte\n###Hello Flyte"

    with pytest.warns(FutureWarning):
        renderer = MarkdownRenderer()
    assert renderer.to_html(md_text) == markdown.markdown(md_text)

