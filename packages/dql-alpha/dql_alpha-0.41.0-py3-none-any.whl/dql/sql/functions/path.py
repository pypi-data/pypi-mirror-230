"""
This module provides generic SQL functions for path logic.

These need to be implemented using dialect-specific compilation rules.
See https://docs.sqlalchemy.org/en/14/core/compiler.html
"""
from sqlalchemy.sql.functions import GenericFunction

from dql.sql.types import String
from dql.sql.utils import compiler_not_implemented


class parent(GenericFunction):
    """
    Returns the directory component of a posix-style path.
    """

    type = String()
    package = "path"
    name = "parent"
    inherit_cache = True


class name(GenericFunction):
    """
    Returns the final component of a posix-style path.
    """

    type = String()
    package = "path"
    name = "name"
    inherit_cache = True


compiler_not_implemented(parent)
compiler_not_implemented(name)
