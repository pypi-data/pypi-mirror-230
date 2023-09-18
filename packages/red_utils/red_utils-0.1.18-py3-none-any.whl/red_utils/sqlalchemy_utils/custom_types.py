"""Define custom type classes for SQLAlchemy.

- [SQLAlchemy docs: Custom Types](https://docs.sqlalchemy.org/en/20/core/custom_types.html#custom-types)

How to use custom type overrides:

After defining a customer class (by inheriting from overriding sqlalchemy.types.TypeDecorator), use it in
a model, after declaring a __tablename__.

Example custom UUID class (https://docs.sqlalchemy.org/en/20/core/custom_types.html#backend-agnostic-guid-type):

class SomeModel(Base):
    __tablename__ = "someTable"
    
    ## Tell this model to convert uuid.UUID Python types to custom CompatibleUUID class
    type_annotation_map = {uuid.UUID: CompatibleUUID}
"""
from __future__ import annotations

from typing import Any
import uuid

from sqlalchemy import BINARY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import CHAR, TypeDecorator

class CompatibleUUID(TypeDecorator):
    """Define a custom UUID, overriding SQLAlchemy's UUId type.

    The main purpose of this class is to instruct SQLAlchemy to
    store UUIDs as a binary, instead of as a UUID type. This is
    useful for cross-database support, i.e. for SQLite which does
    not support the UUID type.

    https://docs.sqlalchemy.org/en/20/core/custom_types.html#backend-agnostic-guid-type

    Usage:

    When defining a table model, after declaring __tablename__, set the type_annotation_map, i.e.:

    class ExampleModel(Base):
        __tablename__ = "__sometable__"

        type_annotation_map = {uuid.UUID: CompatibleUUID}
    """

    impl = BINARY
    cache_ok = True

    def load_diaclect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                ## Return hexstring
                return "%.32x" % value.int

    def process_result_value(self, value: Any | None, dialect: Dialect) -> Any | None:
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value
