import enum
import os
import typing
from html import escape
from string import Template
from typing import Optional

from flytekit.core.context_manager import ExecutionParameters, ExecutionState, FlyteContext, FlyteContextManager
from flytekit.loggers import logger
from flytekit.tools.interactive import ipython_check

OUTPUT_DIR_JUPYTER_PREFIX = "jupyter"
DECK_FILE_NAME = "deck.html"


class DeckField(str, enum.Enum):
    """
    DeckField is used to specify the fields that will be rendered in the deck.
    """

    INPUT = "Input"
    OUTPUT = "Output"
    SOURCE_CODE = "Source Code"
    TIMELINE = "Timeline"
    DEPENDENCIES = "Dependencies"


class Deck:
    """
    Deck enable users to get customizable and default visibility into their tasks.

    Deck contains a list of renderers (FrameRenderer, MarkdownRenderer) that can
    generate a html file. For example, FrameRenderer can render a DataFrame as an HTML table,
    MarkdownRenderer can convert Markdown string to HTML

    Flyte context saves a list of deck objects, and we use renderers in those decks to render
    the data and create an HTML file when those tasks are executed

    Each task has a least three decks (input, output, default). Input/output decks are
    used to render tasks' input/output data, and the default deck is used to render line plots,
    scatter plots or Markdown text. In addition, users can create new decks to render
    their data with custom renderers.

    ```python
    iris_df = px.data.iris()

    @task()
    def t1() -> str:
        md_text = '#Hello Flyte##Hello Flyte###Hello Flyte'
        m = MarkdownRenderer()
        s = BoxRenderer("sepal_length")
        deck = flytekit.Deck("demo", s.to_html(iris_df))
        deck.append(m.to_html(md_text))
        default_deck = flytekit.current_context().default_deck
        default_deck.append(m.to_html(md_text))
        return md_text


    # Use Annotated to override default renderer
    @task()
    def t2() -> Annotated[pd.DataFrame, TopFrameRenderer(10)]:
        return iris_df
    ```
    """
