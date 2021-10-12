from datetime import timedelta
from itertools import product

from flyteidl.core import tasks_pb2

from flytekit.extras.accelerators import A100, T4
from flytekit.models import interface, literals, security, task, types
from flytekit.models.core import identifier
from flytekit.models.core import types as _core_types

LIST_OF_SCALAR_LITERAL_TYPES = [
    types.LiteralType(simple=types.SimpleType.BINARY),
    types.LiteralType(simple=types.SimpleType.BOOLEAN),
    types.LiteralType(simple=types.SimpleType.DATETIME),
    types.LiteralType(simple=types.SimpleType.DURATION),
    types.LiteralType(simple=types.SimpleType.ERROR),
    types.LiteralType(simple=types.SimpleType.FLOAT),
    types.LiteralType(simple=types.SimpleType.INTEGER),
    types.LiteralType(simple=types.SimpleType.NONE),
    types.LiteralType(simple=types.SimpleType.STRING),
    types.LiteralType(
        schema=types.SchemaType(
            [
                types.SchemaType.SchemaColumn("a", types.SchemaType.SchemaColumn.SchemaColumnType.INTEGER),
                types.SchemaType.SchemaColumn("b", types.SchemaType.SchemaColumn.SchemaColumnType.BOOLEAN),
                types.SchemaType.SchemaColumn("c", types.SchemaType.SchemaColumn.SchemaColumnType.DATETIME),
                types.SchemaType.SchemaColumn("d", types.SchemaType.SchemaColumn.SchemaColumnType.DURATION),
                types.SchemaType.SchemaColumn("e", types.SchemaType.SchemaColumn.SchemaColumnType.FLOAT),
                types.SchemaType.SchemaColumn("f", types.SchemaType.SchemaColumn.SchemaColumnType.STRING),
            ]
        )
    ),
    types.LiteralType(
        blob=_core_types.BlobType(
            format="",
            dimensionality=_core_types.BlobType.BlobDimensionality.SINGLE,
        )
    ),
    types.LiteralType(
        blob=_core_types.BlobType(
            format="csv",
            dimensionality=_core_types.BlobType.BlobDimensionality.SINGLE,
        )
    ),
    types.LiteralType(
        blob=_core_types.BlobType(
            format="",
            dimensionality=_core_types.BlobType.BlobDimensionality.MULTIPART,
        )
    ),
    types.LiteralType(
        blob=_core_types.BlobType(
            format="csv",
            dimensionality=_core_types.BlobType.BlobDimensionality.MULTIPART,
        )
    ),
    types.LiteralType(
        union_type=types.UnionType(
            variants=[
                types.LiteralType(simple=types.SimpleType.STRING, structure=types.TypeStructure(tag="str")),
                types.LiteralType(simple=types.SimpleType.INTEGER, structure=types.TypeStructure(tag="int")),
            ]
        )
    ),
]


LIST_OF_COLLECTION_LITERAL_TYPES = [
    types.LiteralType(collection_type=literal_type) for literal_type in LIST_OF_SCALAR_LITERAL_TYPES
]

LIST_OF_NESTED_COLLECTION_LITERAL_TYPES = [
    types.LiteralType(collection_type=literal_type) for literal_type in LIST_OF_COLLECTION_LITERAL_TYPES
]

LIST_OF_ALL_LITERAL_TYPES = (
    LIST_OF_SCALAR_LITERAL_TYPES + LIST_OF_COLLECTION_LITERAL_TYPES + LIST_OF_NESTED_COLLECTION_LITERAL_TYPES
)

LIST_OF_INTERFACES = [
    interface.TypedInterface(
        {"a": interface.Variable(t, "description 1")},
        {"b": interface.Variable(t, "description 2")},
    )
    for t in LIST_OF_ALL_LITERAL_TYPES
]


LIST_OF_RESOURCE_ENTRIES = [
    task.Resources.ResourceEntry(task.Resources.ResourceName.CPU, "1"),
    task.Resources.ResourceEntry(task.Resources.ResourceName.GPU, "1"),
    task.Resources.ResourceEntry(task.Resources.ResourceName.MEMORY, "1G"),
    task.Resources.ResourceEntry(task.Resources.ResourceName.EPHEMERAL_STORAGE, "1G"),
