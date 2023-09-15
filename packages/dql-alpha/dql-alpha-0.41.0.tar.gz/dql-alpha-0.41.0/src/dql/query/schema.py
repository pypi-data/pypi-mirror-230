from typing import Callable, Optional

from sqlalchemy.sql.elements import ColumnClause
from sqlalchemy.sql.visitors import TraversibleType


class ColumnMeta(TraversibleType):
    def __getattr__(cls, name: str):  # noqa: B902
        return cls(name)  # pylint: disable=no-value-for-parameter


class Object:
    """
    Object is used as a placeholder parameter to indicate the actual stored object
    being passed as a parameter to the UDF.
    """

    def __init__(self, reader: Callable, cache: bool = False):
        """
        Initialize the object and specify the reader to be
        used for loading the object into memory.
        """
        self.reader = reader
        self.cache = cache


class LocalFilename:
    """
    Placeholder parameter representing the local path to a cached copy of the object.
    """


class Column(ColumnClause, metaclass=ColumnMeta):  # pylint: disable=abstract-method
    inherit_cache: Optional[bool] = True

    def __init__(self, text, type_=None, is_literal=False, _selectable=None):
        self.name = text
        super().__init__(
            text, type_=type_, is_literal=is_literal, _selectable=_selectable
        )

    def glob(self, glob_str):
        return self.op("GLOB")(glob_str)


C = Column
