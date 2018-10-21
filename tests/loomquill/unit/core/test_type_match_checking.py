from flytekit.models.core.types import BlobType, EnumType
from flytekit.models.types import LiteralType, StructuredDatasetType, UnionType, SimpleType
from flytekit.core.type_match_checking import literal_types_match


def test_exact_match():
    lt = LiteralType(simple=SimpleType.STRING)
    assert literal_types_match(lt, lt) is True

    lt2 = LiteralType(simple=SimpleType.FLOAT)
    assert literal_types_match(lt, lt2) is False


def test_collection_type_match():
    lt1 = LiteralType(collection_type=LiteralType(SimpleType.STRING))
    lt2 = LiteralType(collection_type=LiteralType(SimpleType.STRING))
    assert literal_types_match(lt1, lt2) is True


def test_collection_type_mismatch():
    lt1 = LiteralType(collection_type=LiteralType(SimpleType.STRING))
    lt2 = LiteralType(collection_type=LiteralType(SimpleType.INTEGER))
    assert literal_types_match(lt1, lt2) is False


