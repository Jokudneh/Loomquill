import warnings
from typing import TYPE_CHECKING, List, Optional, Union

from flytekit import lazy_module
from flytekit.types.file import FlyteFile

if TYPE_CHECKING:
    import markdown
    import pandas as pd
    import PIL.Image
    import pygments
    import ydata_profiling
else:
    pd = lazy_module("pandas")
    markdown = lazy_module("markdown")
    PIL = lazy_module("PIL")
    ydata_profiling = lazy_module("ydata_profiling")
    pygments = lazy_module("pygments")


class SourceCodeRenderer:
    """
    Convert Python source code to HTML, and return HTML as a unicode string.
    """

    def __init__(self, title: str = "Source Code"):
        self._title = title
        msg = (
            "flytekitplugins.deck.SourceCodeRenderer is deprecated. Please use flytekit.deck.SourceCodeRenderer instead"
        )
        warnings.warn(msg, FutureWarning)

    def to_html(self, source_code: str) -> str:
        """
        Convert the provided Python source code into HTML format using Pygments library.

        This method applies a colorful style and replaces the color "#fff0f0" with "#ffffff" in CSS.

        Args:
            source_code (str): The Python source code to be converted.

        Returns:
            str: The resulting HTML as a string, including CSS and highlighted source code.
        """
        formatter = pygments.formatters.HtmlFormatter(style="colorful")
        css = formatter.get_style_defs(".highlight").replace("#fff0f0", "#ffffff")
        html = pygments.highlight(source_code, pygments.lexers.PythonLexer(), formatter)
        return f"<style>{css}</style>{html}"


class FrameProfilingRenderer:
    """
    Generate a ProfileReport based on a pandas DataFrame
    """

    def __init__(self, title: str = "Pandas Profiling Report"):
        self._title = title

    def to_html(self, df: "pd.DataFrame") -> str:
        assert isinstance(df, pd.DataFrame)
        profile = ydata_profiling.ProfileReport(df, title=self._title)
