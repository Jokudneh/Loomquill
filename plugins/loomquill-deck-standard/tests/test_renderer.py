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
