"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.message
import google.protobuf.timestamp_pb2
import sys

if sys.version_info >= (3, 8):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class DoubleVector(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ELEMENT_FIELD_NUMBER: builtins.int
    @property
    def element(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.float]: ...
    def __init__(
        self,
        *,
        element: collections.abc.Iterable[builtins.float] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["element", b"element"]) -> None: ...

global___DoubleVector = DoubleVector

class Property(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    NAME_FIELD_NUMBER: builtins.int
    STRING_VAL_FIELD_NUMBER: builtins.int
    INT_VAL_FIELD_NUMBER: builtins.int
    BOOL_VAL_FIELD_NUMBER: builtins.int
    DOUBLE_VAL_FIELD_NUMBER: builtins.int
    TIMESTAMP_VAL_FIELD_NUMBER: builtins.int
    IS_EMPTY_FIELD_NUMBER: builtins.int
    name: builtins.str
    string_val: builtins.str
    int_val: builtins.int
    """we treat all ints as 64 - no int/long distinction"""
    bool_val: builtins.bool
    double_val: builtins.float
    """not distinguishing double vs float"""
    @property
    def timestamp_val(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    is_empty: builtins.bool
    def __init__(
        self,
        *,
        name: builtins.str = ...,
        string_val: builtins.str = ...,
        int_val: builtins.int = ...,
        bool_val: builtins.bool = ...,
        double_val: builtins.float = ...,
        timestamp_val: google.protobuf.timestamp_pb2.Timestamp | None = ...,
        is_empty: builtins.bool = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["bool_val", b"bool_val", "double_val", b"double_val", "int_val", b"int_val", "string_val", b"string_val", "timestamp_val", b"timestamp_val", "value_type", b"value_type"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["bool_val", b"bool_val", "double_val", b"double_val", "int_val", b"int_val", "is_empty", b"is_empty", "name", b"name", "string_val", b"string_val", "timestamp_val", b"timestamp_val", "value_type", b"value_type"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["value_type", b"value_type"]) -> typing_extensions.Literal["string_val", "int_val", "bool_val", "double_val", "timestamp_val"] | None: ...

global___Property = Property

class SearchResult(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    VECTOR_FIELD_NUMBER: builtins.int
    PROPERTIES_FIELD_NUMBER: builtins.int
    DISTANCE_FIELD_NUMBER: builtins.int
    id: builtins.str
    @property
    def vector(self) -> global___DoubleVector: ...
    @property
    def properties(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___Property]: ...
    distance: builtins.float
    def __init__(
        self,
        *,
        id: builtins.str = ...,
        vector: global___DoubleVector | None = ...,
        properties: collections.abc.Iterable[global___Property] | None = ...,
        distance: builtins.float = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["vector", b"vector"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["distance", b"distance", "id", b"id", "properties", b"properties", "vector", b"vector"]) -> None: ...

global___SearchResult = SearchResult

class StoredVector(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    VECTOR_FIELD_NUMBER: builtins.int
    PROPERTY_FIELD_NUMBER: builtins.int
    id: builtins.str
    @property
    def vector(self) -> global___DoubleVector: ...
    @property
    def property(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___Property]: ...
    def __init__(
        self,
        *,
        id: builtins.str = ...,
        vector: global___DoubleVector | None = ...,
        property: collections.abc.Iterable[global___Property] | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["vector", b"vector"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["id", b"id", "property", b"property", "vector", b"vector"]) -> None: ...

global___StoredVector = StoredVector
