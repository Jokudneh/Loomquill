import typing

from flytekit.core.docstring import Docstring


def test_get_variable_descriptions():
    # sphinx style
    def z(a: int, b: str) -> typing.Tuple[int, str]:
        """
        function z

        longer description here

        :param a: foo
        :param b: bar
        :return: ramen
        """
        ...

    docstring = Docstring(callable_=z)
    input_descriptions = docstring.input_descriptions
    output_descriptions = docstring.output_descriptions
    assert input_descriptions["a"] == "foo"
    assert input_descriptions["b"] == "bar"
    assert len(output_descriptions) == 1
    assert next(iter(output_descriptions.items()))[1] == "ramen"
    assert docstring.short_description == "function z"
    assert docstring.long_description == "longer description here"

