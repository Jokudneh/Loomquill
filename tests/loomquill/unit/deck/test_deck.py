import datetime
import sys

import pytest
from markdown_it import MarkdownIt
from mock import mock, patch

import flytekit
from flytekit import Deck, FlyteContextManager, task

from flytekit.deck import DeckField, MarkdownRenderer, SourceCodeRenderer, TopFrameRenderer
from flytekit.deck.deck import _output_deck
from flytekit.deck.renderer import PythonDependencyRenderer


@pytest.mark.skipif("pandas" not in sys.modules, reason="Pandas is not installed.")
def test_deck():
    import pandas as pd

    df = pd.DataFrame({"Name": ["Tom", "Joseph"], "Age": [1, 22]})
    ctx = FlyteContextManager.current_context()
    ctx.user_space_params._decks = [ctx.user_space_params.default_deck]
    renderer = TopFrameRenderer()
    deck_name = "test"
    deck = Deck(deck_name)
    deck.append(renderer.to_html(df))
    assert deck.name == deck_name
    assert deck.html is not None
    assert len(ctx.user_space_params.decks) == 2

    _output_deck("test_task", ctx.user_space_params)


def test_timeline_deck():
    time_info = dict(
        Name="foo",
        Start=datetime.datetime.now(datetime.timezone.utc),
        Finish=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(microseconds=1000),
        WallTime=1.0,
        ProcessTime=1.0,
    )
    ctx = FlyteContextManager.current_context()
    ctx.user_space_params._decks = []
    ctx.user_space_params._timeline_deck = None
    timeline_deck = ctx.user_space_params.timeline_deck
    timeline_deck.append_time_info(time_info)
    assert timeline_deck.name == "Timeline"
    assert len(timeline_deck.time_info) == 1
    assert timeline_deck.time_info[0] == time_info
    assert len(ctx.user_space_params.decks) == 0

