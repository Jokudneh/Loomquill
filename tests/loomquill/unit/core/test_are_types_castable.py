from flytekit.core.type_engine import _are_types_castable
from flytekit.models.annotation import TypeAnnotation
from flytekit.models.core.types import EnumType
from flytekit.models.types import LiteralType, SimpleType, StructuredDatasetType, TypeStructure, UnionType

str_type = LiteralType(simple=SimpleType.STRING)
int_type = LiteralType(simple=SimpleType.INTEGER)
none_type = LiteralType(simple=SimpleType.NONE)
bool_type = LiteralType(simple=SimpleType.BOOLEAN)

str_or_int = LiteralType(union_type=UnionType([str_type, int_type]))
int_or_str = LiteralType(union_type=UnionType([int_type, str_type]))
str_or_int_or_bool = LiteralType(union_type=UnionType([str_type, int_type, bool_type]))
optional_str = LiteralType(union_type=UnionType([str_type, none_type]))


def test_simple():
    assert _are_types_castable(str_type, str_type)
    assert not _are_types_castable(str_type, int_type)
    assert not _are_types_castable(int_type, str_type)


def test_metadata():
    a = LiteralType(simple=SimpleType.STRING, metadata={"test": 456})
    assert _are_types_castable(
        a,
        LiteralType(simple=SimpleType.STRING, metadata={"test": 123}),
    )
    # must not clobber metadata
    assert a.metadata == {"test": 456}


def test_annotation():
    a = LiteralType(simple=SimpleType.STRING, annotation=TypeAnnotation(annotations={"test": 456}))
    assert _are_types_castable(
        a,
        LiteralType(simple=SimpleType.STRING, annotation=TypeAnnotation(annotations={"test": 123})),
    )
    # must not clobber annotation
    assert a.annotation.annotations == {"test": 456}


def test_structure():
    a = LiteralType(simple=SimpleType.STRING, structure=TypeStructure(tag="a"))
    assert _are_types_castable(
        a,
