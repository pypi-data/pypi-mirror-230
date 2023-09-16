import logging
import sqlite3
from datetime import MAXYEAR, MINYEAR, datetime, timezone
from types import MappingProxyType
from typing import Callable, Dict

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.elements import literal
from sqlalchemy.sql.functions import func

from dql.sql.functions import array
from dql.sql.functions import path as sql_path
from dql.sql.sqlite.types import SQLiteTypeConverter, register_type_converters
from dql.sql.types import register_backend_types

logger = logging.getLogger("dql")

_registered_function_creators: Dict[str, Callable[[sqlite3.Connection], None]] = {}
registered_function_creators = MappingProxyType(_registered_function_creators)

_compiler_hooks: Dict[str, Callable] = {}

slash = literal("/")
empty_str = literal("")


def setup():
    # sqlite 3.31.1 is the earliest version tested in CI
    if sqlite3.sqlite_version_info < (3, 31, 1):
        logger.warning(
            "Possible sqlite incompatibility. The earliest tested version of "
            f"sqlite is 3.31.1 but you have {sqlite3.sqlite_version}"
        )

    # We want to show tracebacks for user-defined functions
    sqlite3.enable_callback_tracebacks(True)
    sqlite3.register_adapter(datetime, adapt_datetime)
    sqlite3.register_converter("datetime", convert_datetime)

    register_type_converters()
    register_backend_types("sqlite", SQLiteTypeConverter())

    compiles(sql_path.parent, "sqlite")(compile_path_parent)
    compiles(sql_path.name, "sqlite")(compile_path_name)
    compiles(array.cosine_distance, "sqlite")(compile_cosine_distance)
    compiles(array.euclidean_distance, "sqlite")(compile_euclidean_distance)
    register_user_defined_sql_functions()


def run_compiler_hook(name):
    try:
        hook = _compiler_hooks[name]
    except KeyError:
        return
    hook()


def create_user_defined_sql_functions(connection):
    for function_creator in registered_function_creators.values():
        function_creator(connection)


def missing_vector_function(name, exc):
    def unavailable_func(*args):
        raise ImportError(
            f"Missing dependencies for SQL vector function, {name}\n"
            "To install run:\n\n"
            "  pip install 'dql-alpha[vector]'\n"
        ) from exc

    return unavailable_func


def register_user_defined_sql_functions() -> None:
    # Register optional functions if we have the necessary dependencies
    # and otherwise register functions that will raise an exception with
    # installation instructions
    try:
        from .vector import cosine_distance, euclidean_distance
    except ImportError as exc:
        # We want to throw an exception when trying to compile these
        # functions and also if the functions are called using raw SQL.
        cosine_distance = missing_vector_function("cosine_distance", exc)
        euclidean_distance = missing_vector_function("euclidean_distance", exc)
        _compiler_hooks["cosine_distance"] = cosine_distance
        _compiler_hooks["euclidean_distance"] = euclidean_distance

    def create_vector_functions(conn):
        conn.create_function("cosine_distance", 2, cosine_distance, deterministic=True)
        conn.create_function(
            "euclidean_distance", 2, euclidean_distance, deterministic=True
        )

    _registered_function_creators["vector_functions"] = create_vector_functions


def adapt_datetime(val: datetime) -> str:
    if not (val.tzinfo is timezone.utc or val.tzname() == "UTC"):
        try:
            val = val.astimezone(timezone.utc)
        except (OverflowError, ValueError, OSError):
            if val.year == MAXYEAR:
                val = datetime.max
            elif val.year == MINYEAR:
                val = datetime.min
            else:
                raise
    return val.replace(tzinfo=None).isoformat(" ")


def convert_datetime(val: bytes) -> datetime:
    return datetime.fromisoformat(val.decode()).replace(tzinfo=timezone.utc)


def path_parent(path):
    return func.rtrim(func.rtrim(path, func.replace(path, slash, empty_str)), slash)


def path_name(path):
    return func.ltrim(func.substr(path, func.length(path_parent(path)) + 1), slash)


def compile_path_parent(element, compiler, **kwargs):
    return compiler.process(path_parent(*element.clauses.clauses), **kwargs)


def compile_path_name(element, compiler, **kwargs):
    return compiler.process(path_name(*element.clauses.clauses), **kwargs)


def compile_cosine_distance(element, compiler, **kwargs):
    run_compiler_hook("cosine_distance")
    return "cosine_distance(%s)" % compiler.process(element.clauses, **kwargs)


def compile_euclidean_distance(element, compiler, **kwargs):
    run_compiler_hook("euclidean_distance")
    return "euclidean_distance(%s)" % compiler.process(element.clauses, **kwargs)
