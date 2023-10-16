from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from _qwak_proto.qwak.vectors.v1.filters_pb2 import (
    And as ProtoAnd,
    AtomicLiteral as ProtoAtomicLiteral,
    Equal as ProtoEqual,
    Filter as ProtoFilter,
    GreaterThan as ProtoGreaterThan,
    GreaterThanEqual as ProtoGreaterThanEqual,
    IsNotNull as ProtoIsNotNull,
    IsNull as ProtoIsNull,
    LessThan as ProtoLessThan,
    LessThanEqual as ProtoLessThanEqual,
    Like as ProtoLike,
    NotEqual as ProtoNotEqual,
    Or as ProtoOr,
)
from google.protobuf.json_format import MessageToDict, ParseDict
from qwak.vector_store.utils.filter_utils import transform


class Filter(ABC):
    def And(self, other):
        return And(self, other)

    def Or(self, other):
        return Or(self, other)

    @abstractmethod
    def to_proto(self):
        pass


@dataclass
class And(Filter):
    left: Filter
    right: Filter

    def to_proto(self):
        proto_filter = ProtoFilter()
        proto_filter_dict = MessageToDict(proto_filter)
        proto_and_dict = MessageToDict(
            ProtoAnd(left=self.left.to_proto(), right=self.right.to_proto())
        )
        proto_filter_dict["and"] = proto_and_dict
        return ParseDict(proto_filter_dict, proto_filter, ignore_unknown_fields=True)


@dataclass
class Or(Filter):
    left: Filter
    right: Filter

    def to_proto(self):
        proto_filter = ProtoFilter()
        proto_filter_dict = MessageToDict(proto_filter)
        proto_or_dict = MessageToDict(
            ProtoOr(left=self.left.to_proto(), right=self.right.to_proto())
        )
        proto_filter_dict["or"] = proto_or_dict
        return ParseDict(proto_filter_dict, proto_filter, ignore_unknown_fields=True)


@dataclass
class _UnaryFilter(Filter):
    property: str
    value: Any

    def to_proto(self):
        # Each UnaryFilter implements its own to_proto
        pass


class Equal(_UnaryFilter):
    def to_proto(self):
        atomic_literal: ProtoAtomicLiteral = transform(value=self.value)
        return ProtoFilter(eq=ProtoEqual(property=self.property, value=atomic_literal))


class NotEqual(_UnaryFilter):
    def to_proto(self):
        atomic_literal: ProtoAtomicLiteral = transform(value=self.value)
        return ProtoFilter(
            ne=ProtoNotEqual(property=self.property, value=atomic_literal)
        )


class LessThanEqual(_UnaryFilter):
    def to_proto(self):
        atomic_literal: ProtoAtomicLiteral = transform(value=self.value)
        return ProtoFilter(
            lte=ProtoLessThanEqual(property=self.property, value=atomic_literal)
        )


class LessThan(_UnaryFilter):
    def to_proto(self):
        atomic_literal: ProtoAtomicLiteral = transform(value=self.value)
        return ProtoFilter(
            lt=ProtoLessThan(property=self.property, value=atomic_literal)
        )


class GreaterThanEqual(_UnaryFilter):
    def to_proto(self):
        atomic_literal: ProtoAtomicLiteral = transform(value=self.value)
        return ProtoFilter(
            gte=ProtoGreaterThanEqual(property=self.property, value=atomic_literal)
        )


class GreaterThan(_UnaryFilter):
    def to_proto(self):
        atomic_literal: ProtoAtomicLiteral = transform(value=self.value)
        return ProtoFilter(
            gt=ProtoGreaterThan(property=self.property, value=atomic_literal)
        )


@dataclass
class Like(Filter):
    property: str
    pattern: str

    def to_proto(self):
        return ProtoFilter(like=ProtoLike(property=self.property, pattern=self.pattern))


@dataclass
class IsNull(Filter):
    property: str

    def to_proto(self):
        return ProtoFilter(is_null=ProtoIsNull(property=self.property))


@dataclass
class IsNotNull(Filter):
    property: str

    def to_proto(self):
        return ProtoFilter(is_not_null=ProtoIsNotNull(property=self.property))


@dataclass
class Property:
    name: str

    def gt(self, value: Any):
        return GreaterThan(self.name, value)

    def gte(self, value: Any):
        return GreaterThan(self.name, value)

    def lt(self, value: Any):
        return LessThan(self.name, value)

    def lte(self, value: Any):
        return LessThanEqual(self.name, value)

    def eq(self, value: Any):
        return Equal(self.name, value)

    def ne(self, value: Any):
        return NotEqual(self.name, value)

    def is_null(self):
        return IsNull(self.name)

    def is_not_null(self):
        return IsNotNull(self.name)

    def like(self, pattern: str):
        return Like(self.name, pattern)
