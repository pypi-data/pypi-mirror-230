"""
SQL types.

This module provides SQL types to provide common features and interoperability
between different database backends which often have different typing systems.

See https://docs.sqlalchemy.org/en/20/core/custom_types.html#sqlalchemy.types.TypeDecorator.load_dialect_impl

For the corresponding python to db type conversion, it's often simpler and
more direct to use methods at the DBAPI rather than sqlalchemy. For example
for sqlite we can use `sqlite.register_converter`
( https://docs.python.org/3/library/sqlite3.html#sqlite3.register_converter )
"""  # noqa: E501

from types import MappingProxyType
from typing import Dict

from sqlalchemy import TypeDecorator, types

_registry: Dict[str, "TypeConverter"] = {}
registry = MappingProxyType(_registry)


def register_backend_types(dialect_name: str, type_cls):
    _registry[dialect_name] = type_cls


def converter(dialect) -> "TypeConverter":
    name = dialect.name
    try:
        return registry[name]
    except KeyError:
        raise ValueError(f"No type converter registered for dialect: {dialect.name!r}")


# pylint: disable=abstract-method


class SQLType(TypeDecorator):
    impl = types.TypeEngine
    cache_ok = True


class String(SQLType):
    impl = types.String

    def load_dialect_impl(self, dialect):
        return converter(dialect).string()


class Int(SQLType):
    impl = types.INTEGER

    def load_dialect_impl(self, dialect):
        return converter(dialect).int()


class Int32(Int):
    def load_dialect_impl(self, dialect):
        return converter(dialect).int32()


class Int64(Int):
    def load_dialect_impl(self, dialect):
        return converter(dialect).int64()


class Float(SQLType):
    impl = types.INTEGER

    def load_dialect_impl(self, dialect):
        return converter(dialect).float()


class Float32(Int):
    def load_dialect_impl(self, dialect):
        return converter(dialect).float32()


class Float64(Int):
    def load_dialect_impl(self, dialect):
        return converter(dialect).float64()


class Array(SQLType):
    impl = types.ARRAY

    def load_dialect_impl(self, dialect):
        return converter(dialect).array(self.item_type)


# pylint: enable=abstract-method


class TypeConverter:
    def string(self):
        return types.String()

    def int(self):
        return types.Integer()

    def int32(self):
        return self.int()

    def int64(self):
        return self.int()

    def float(self):
        return types.Float()

    def float32(self):
        self.float()

    def float64(self):
        self.float()

    def array(self, item_type):
        return types.ARRAY(item_type)


register_backend_types("default", TypeConverter())
