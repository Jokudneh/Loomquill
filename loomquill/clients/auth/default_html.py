from contextlib import suppress


def get_default_success_html(endpoint: str) -> str:
    from flytekit.configuration.plugin import get_plugin

    with suppress(AttributeError):
        success_html = get_plugin().get_auth_success_html(endpoint)
        if success_html is not None:
            return success_html

    return f"""
<html>
