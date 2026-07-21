from flytekit.types.file.file import FlyteFile


def test_filepath_equality():
    a = FlyteFile("/tmp")
    b = FlyteFile("/tmp")
    assert str(b) == "/tmp"
    assert a == b

