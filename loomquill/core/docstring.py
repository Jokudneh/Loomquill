from typing import Callable, Dict, Optional

from docstring_parser import parse


class Docstring(object):
    def __init__(self, docstring: Optional[str] = None, callable_: Optional[Callable] = None):
        if docstring is not None:
            self._parsed_docstring = parse(docstring)
