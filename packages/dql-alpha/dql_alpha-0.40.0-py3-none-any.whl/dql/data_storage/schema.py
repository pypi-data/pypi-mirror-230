import itertools
from typing import (
    TYPE_CHECKING,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
)

import sqlalchemy as sa
from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Integer,
    MetaData,
    Text,
)
from sqlalchemy.sql import func as f
from sqlalchemy.sql.expression import null, true

from dql.node import DirType, DirTypeGroup
from dql.sql.functions import path

if TYPE_CHECKING:
    from sqlalchemy import Engine
    from sqlalchemy.sql.base import Executable
    from sqlalchemy.sql.selectable import Select


def parse_columns(columns: Iterable[Dict[str, str]]) -> List[Column]:
    """
    Function that outputs a list of sqlalchemy Column objects out of a list
    of column names and stringified python types.
    Example input:
    [
        {"name": "a_punsafe", "type": "float"},
        {"name": "a_hash", "type": "int"}
    ]
    """
    type_map = {
        "float": sa.Float,
        "int": sa.Integer,
        "str": sa.String,
        "list": sa.JSON,
        "bool": sa.Boolean,
    }

    return [Column(column["name"], type_map[column["type"]]) for column in columns]


def dedup_columns(columns: Iterable[Column]) -> List[Column]:
    """
    Removes duplicate columns from a list of columns.
    If column with the same name and different type is found, exception is
    raised
    """
    c_set: Dict[str, Column] = {}
    for c in columns:
        if ec := c_set.get(c.name, None):
            if str(ec.type) != str(c.type):
                raise ValueError(
                    f"conflicting types for column {c.name}:"
                    f"{str(c.type)} and {str(ec.type)}"
                )
            continue
        c_set[c.name] = c

    return list(c_set.values())


class Table:
    def __init__(self, name: str, metadata: Optional["MetaData"] = None):
        self.metadata: "MetaData" = metadata if metadata is not None else MetaData()
        self.name: str = name

    @property
    def columns(self) -> List[Column]:
        return self.table.columns

    @property
    def c(self):
        return self.columns

    @classmethod
    def default_columns(cls) -> List[Column]:
        return []

    @property
    def custom_columns(self):
        """List of custom columns added to the table."""
        default_cols = [c.name for c in self.default_columns()]
        return [c for c in self.columns if c.name not in default_cols]

    @property
    def table(self) -> "sa.Table":
        return self.get_table()

    def get_table(self) -> "sa.Table":
        table = self.metadata.tables.get(self.name)
        if table is None:
            table = sa.Table(
                self.name,
                self.metadata,
                *self.default_columns(),
            )
        return table

    def apply_conditions(self, query: "Executable") -> "Executable":
        """
        Apply any conditions that belong on all selecting queries.

        This could be used to filter tables that use access control.
        """
        return query

    def select(self, *columns):
        if not columns:
            query = self.table.select()
        else:
            query = sa.select(*columns).select_from(self.table)
        return self.apply_conditions(query)

    def insert(self):
        return self.table.insert()

    def update(self):
        return self.apply_conditions(self.table.update())

    def delete(self):
        return self.apply_conditions(self.table.delete())


class DirExpansion:
    @staticmethod
    def base_select(q):
        return sa.select(
            q.c.id,
            q.c.vtype,
            (q.c.dir_type == DirType.DIR).label("is_dir"),
            q.c.source,
            q.c.parent,
            q.c.name,
            q.c.version,
            q.c.location,
        )

    @staticmethod
    def apply_group_by(q):
        return (
            sa.select(
                f.min(q.c.id).label("id"),
                q.c.vtype,
                q.c.is_dir,
                q.c.source,
                q.c.parent,
                q.c.name,
                q.c.version,
                f.max(q.c.location).label("location"),
            )
            .select_from(q)
            .group_by(
                q.c.source, q.c.parent, q.c.name, q.c.vtype, q.c.is_dir, q.c.version
            )
            .order_by(
                q.c.source, q.c.parent, q.c.name, q.c.vtype, q.c.is_dir, q.c.version
            )
        )

    @classmethod
    def query(cls, q):
        q = cls.base_select(q).cte(recursive=True)
        parent_parent = path.parent(q.c.parent)
        parent_name = path.name(q.c.parent)
        q = q.union_all(
            sa.select(
                sa.literal(-1).label("id"),
                sa.literal("").label("vtype"),
                true().label("is_dir"),
                q.c.source,
                parent_parent.label("parent"),
                parent_name.label("name"),
                sa.literal("").label("version"),
                null().label("location"),
            ).where((parent_name != "") | (parent_parent != ""))
        )
        return cls.apply_group_by(q)


class BaseDatasetRow(Table):
    dataset_dir_expansion = DirExpansion.query

    @classmethod
    def default_columns(cls) -> List[Column]:
        return [
            Column("id", Integer, primary_key=True),
            Column("vtype", Text, nullable=False, index=True),
            Column("dir_type", Integer, index=True),
            Column("parent_id", Integer, index=True),
            Column("parent", Text, index=True),
            Column("name", Text, nullable=False, index=True),
            Column("checksum", Text),
            Column("etag", Text),
            Column("version", Text),
            Column("is_latest", Boolean),
            Column("last_modified", DateTime(timezone=True)),
            Column("size", BigInteger, nullable=False, index=True),
            Column("owner_name", Text),
            Column("owner_id", Text),
            Column("anno", JSON),
            Column("random", BigInteger, nullable=False),
            Column("location", JSON),
        ]

    @staticmethod
    def copy_signal_column(column: Column):
        """
        Copy a sqlalchemy Column object intended for use as a signal column.

        This does not copy all attributes as certain attributes such as
        table are too context-dependent and the purpose of this function is
        adding a signal column from one table to another table.

        We can't use Column.copy() as it only works in certain contexts.
        See https://github.com/sqlalchemy/sqlalchemy/issues/5953
        """
        return Column(
            column.name,
            column.type,
            primary_key=column.primary_key,
            index=column.index,
            nullable=column.nullable,
            default=column.default,
            server_default=column.server_default,
            unique=column.unique,
        )

    @classmethod
    def new_table(
        cls,
        name: str,
        custom_columns: Sequence["Column"] = (),
        metadata: Optional["MetaData"] = None,
    ):
        # copy columns, since re-using the same objects from another table
        # may raise an error
        custom_columns = [cls.copy_signal_column(c) for c in custom_columns]
        if metadata is None:
            metadata = MetaData()
        return sa.Table(
            name,
            metadata,
            *cls.default_columns(),
            *custom_columns,
        )

    def dir_expansion(self):
        return self.dataset_dir_expansion(self)


class Node(BaseDatasetRow):
    def __init__(self, name: str, source: str, metadata: Optional["MetaData"] = None):
        super().__init__(name, metadata=metadata)
        self.source = source

    @classmethod
    def default_columns(cls) -> List[Column]:
        return [
            *super().default_columns(),
            Column("partial_id", Integer),
            Column("valid", Boolean, default=True, nullable=False),
        ]

    def dataset_query(
        self,
        *column_names: str,
    ) -> "Select":
        if not column_names:
            column_names = DATASET_CORE_COLUMN_NAMES
        column_objects = [
            sa.literal(self.source).label("source") if c == "source" else self.c[c]
            for c in column_names
        ]
        # include all object types - file, tar archive, tar file (subobject)
        return self.select(*column_objects).where(
            self.c.dir_type.in_(DirTypeGroup.FILE)
            & (self.c.valid == true())
            & (self.c.is_latest == true())
        )

    def dir_expansion(self):
        return self.dataset_dir_expansion(self.dataset_query().subquery())


class DatasetRow(BaseDatasetRow):
    def __init__(
        self, name: str, engine: "Engine", metadata: Optional["MetaData"] = None
    ):
        self.engine = engine
        super().__init__(name, metadata)

    def get_table(self) -> "sa.Table":
        table = self.metadata.tables.get(self.name)
        if table is None:
            return sa.Table(
                self.name,
                self.metadata,
                extend_existing=True,
                autoload_with=self.engine,
            )
        return table

    @classmethod
    def default_columns(cls) -> List[Column]:
        return [
            *super().default_columns(),
            Column("source", Text, nullable=False),
        ]

    @classmethod
    def calculate_custom_columns(cls, nodes: Iterable[Node]) -> List[Column]:
        """
        Function that returns union of custom columns from all the nodes on
        which dataset is based.
        """
        return dedup_columns(list(itertools.chain(*[n.custom_columns for n in nodes])))

    @classmethod
    def calculate_all_columns(cls, nodes: Iterable[Node]) -> List[Column]:
        """
        Function that returns all dataset columns that need to be created based
        on list of nodes which are sources for a dataset.
        It will always have default set of columns and additionally it will
        add union of custom columns from all the nodes
        """
        return cls.default_columns() + list(cls.calculate_custom_columns(nodes))


DATASET_CORE_COLUMN_NAMES = tuple([col.name for col in DatasetRow.default_columns()])

NodeT = TypeVar("NodeT", bound=Node)
DatasetRowT = TypeVar("DatasetRowT", bound=DatasetRow)


class Schema(Generic[NodeT, DatasetRowT]):
    node_cls: Type[NodeT]
    dataset_row_cls: Type[DatasetRowT]


class DefaultSchema(Schema[Node, DatasetRow]):
    def __init__(self):
        self.node_cls = Node
        self.dataset_row_cls = DatasetRow


class SignalsTable(Table):
    """A table for storing signals and annotations."""

    def __init__(
        self, name: str, cols: List[Column], metadata: Optional["MetaData"] = None
    ):
        self.cols = cols
        super().__init__(name, metadata=metadata)

    def get_table(self) -> "sa.Table":
        table = self.metadata.tables.get(self.name)
        if table is None:
            return sa.Table(
                self.name,
                self.metadata,
                Column("id", Integer, primary_key=True),
                *self.cols,
            )
        return table
