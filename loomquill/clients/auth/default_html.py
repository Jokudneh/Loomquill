from contextlib import suppress


def get_default_success_html(endpoint: str) -> str:
    from flytekit.configuration.plugin import get_plugin

    with suppress(AttributeError):
