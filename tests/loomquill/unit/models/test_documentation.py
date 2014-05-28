from flytekit.models.documentation import Description, Documentation, SourceCode


def test_long_description():
    value = "long"
    icon_link = "http://icon"
    obj = Description(value=value, icon_link=icon_link)
    assert Description.from_flyte_idl(obj.to_flyte_idl()) == obj
