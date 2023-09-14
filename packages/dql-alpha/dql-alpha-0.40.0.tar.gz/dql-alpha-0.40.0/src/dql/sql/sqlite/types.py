import json
import sqlite3

from sqlalchemy import types

from dql.sql.types import TypeConverter


class Array(types.UserDefinedType):
    cache_ok = True

    def __init__(self, item_type):  # pylint: disable=super-init-not-called
        self.item_type = item_type

    @property
    def python_type(self):
        return list

    def get_col_spec(self, **kwargs):  # pylint: disable=unused-argument
        return "ARRAY"


def adapt_array(arr):
    return json.dumps(arr)


def convert_array(arr):
    return json.loads(arr)


def register_type_converters():
    sqlite3.register_adapter(list, adapt_array)
    sqlite3.register_converter("ARRAY", convert_array)


class SQLiteTypeConverter(TypeConverter):
    def array(self, item_type):
        return Array(item_type)
