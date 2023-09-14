import logging
import os
import posixpath
import re
import sqlite3
from datetime import datetime, timezone
from functools import wraps
from time import sleep
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

import sqlalchemy
from sqlalchemy import MetaData, Table, UniqueConstraint, select, update
from sqlalchemy.dialects import sqlite
from sqlalchemy.schema import Column as saColumn
from sqlalchemy.schema import CreateIndex, CreateTable, DropTable
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import bindparam, cast, true

import dql.sql.sqlite
from dql.data_storage.abstract import AbstractDataStorage
from dql.data_storage.schema import (
    DATASET_CORE_COLUMN_NAMES,
    DefaultSchema,
    SignalsTable,
)
from dql.dataset import DatasetRecord
from dql.dataset import Status as DatasetStatus
from dql.error import DQLError, InconsistentSignalType
from dql.sql.sqlite import create_user_defined_sql_functions
from dql.storage import Status as StorageStatus
from dql.storage import Storage
from dql.utils import DQLDir

if TYPE_CHECKING:
    from sqlalchemy.schema import SchemaItem
    from sqlalchemy.sql.elements import ColumnClause, CompilerElement, TextClause
    from sqlalchemy.types import TypeEngine

    from dql.data_storage import schema

logger = logging.getLogger("dql")

RETRY_START_SEC = 0.01
RETRY_MAX_TIMES = 10
RETRY_FACTOR = 2
# special string to wrap around dataset name in a user query script stdout, which
# is run in a Python subprocess, so that we can find it later on after script is
# done since there is no other way to return results from it
PYTHON_SCRIPT_WRAPPER_CODE = "__ds__"

Column = Union[str, "ColumnClause[Any]", "TextClause"]

dql.sql.sqlite.setup()

sqlite_dialect = sqlite.dialect(paramstyle="named")
quote_schema = sqlite_dialect.identifier_preparer.quote_schema
quote = sqlite_dialect.identifier_preparer.quote


def compile_statement(
    statement: "CompilerElement",
) -> Union[Tuple[str], Tuple[str, Dict[str, Any]]]:
    compile_kwargs = {}
    if not isinstance(statement, (CreateTable, DropTable, CreateIndex)):
        # render_postcompile is needed for in_ queries to work
        compile_kwargs = {"render_postcompile": True}
    compiled = statement.compile(dialect=sqlite_dialect, compile_kwargs=compile_kwargs)
    if compiled.params is None:
        return (compiled.string,)
    return compiled.string, compiled.params


def get_retry_sleep_sec(retry_count: int) -> int:
    return RETRY_START_SEC * (RETRY_FACTOR**retry_count)


def retry_sqlite_locks(func):  # pylint: disable=redefined-outer-name
    # This retries the database modification in case of concurrent access
    @wraps(func)
    def wrapper(*args, **kwargs):
        exc = None
        for retry_count in range(RETRY_MAX_TIMES):
            try:
                return func(*args, **kwargs)
            except sqlite3.OperationalError as operror:
                exc = operror
                sleep(get_retry_sleep_sec(retry_count))
        raise exc

    return wrapper


class SQLiteDataStorage(AbstractDataStorage):
    """
    SQLite data storage uses SQLite3 for storing indexed data locally.
    This is currently used for the local cli.
    """

    def __init__(self, db_file: Optional[str] = None, uri: str = ""):
        self.schema: "DefaultSchema" = DefaultSchema()
        super().__init__(uri)
        self.db_file = db_file if db_file else DQLDir.find().db
        detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        self.listing_table_pattern = re.compile(
            f"^{self.LISTING_TABLE_NAME_PREFIX}[a-z0-9]+$"
        )

        try:
            if self.db_file == ":memory:":
                # Enable multithreaded usage of the same in-memory db
                self.db = sqlite3.connect(
                    "file::memory:?cache=shared", uri=True, detect_types=detect_types
                )
            else:
                self.db = sqlite3.connect(self.db_file, detect_types=detect_types)
            create_user_defined_sql_functions(self.db)
            self.engine = sqlalchemy.create_engine(
                "sqlite+pysqlite:///", creator=lambda: self.db, future=True
            )

            self.db.isolation_level = None  # Use autocommit mode
            self.db.execute("PRAGMA foreign_keys = ON")
            self.db.execute("PRAGMA cache_size = -102400")  # 100 MiB
            # Enable Write-Ahead Log Journaling
            self.db.execute("PRAGMA journal_mode = WAL")
            self.db.execute("PRAGMA synchronous = NORMAL")
            self.db.execute("PRAGMA case_sensitive_like = ON")
            if os.environ.get("DEBUG_SHOW_SQL_QUERIES"):
                self.db.set_trace_callback(print)

            self._init_storage_table()
            self._init_datasets_tables()
            self.init_cache_table()

            self._reflect_tables(
                filter_tables=lambda t, _: bool(self.listing_table_pattern.match(t))
            )
        except RuntimeError:
            raise DQLError("Can't connect to SQLite DB")

    @staticmethod
    def buckets_constraints() -> List["SchemaItem"]:
        return [
            UniqueConstraint("uri"),
        ]

    @staticmethod
    def datasets_constraints() -> List["SchemaItem"]:
        return [
            UniqueConstraint("name"),
        ]

    @staticmethod
    def buckets_columns() -> List["SchemaItem"]:
        columns = super(SQLiteDataStorage, SQLiteDataStorage).buckets_columns()
        return columns + SQLiteDataStorage.buckets_constraints()

    @staticmethod
    def datasets_columns() -> List["SchemaItem"]:
        columns = super(SQLiteDataStorage, SQLiteDataStorage).datasets_columns()
        return columns + SQLiteDataStorage.datasets_constraints()

    def _reflect_tables(self, filter_tables=None):
        """
        Since some tables are prone to schema extension, meaning we can add
        additional columns to it, we should reflect changes in metadata
        to have the latest columns when dealing with those tables.
        If filter function is defined, it's used to filter out tables to reflect,
        otherwise all tables are reflected
        """
        self.metadata.reflect(
            bind=self.engine,
            extend_existing=True,
            only=filter_tables,
        )

    def _init_storage_table(self):
        """Initialize only tables related to storage, e.g s3"""
        self.execute(CreateTable(self.storages, if_not_exists=True))

    def _init_datasets_tables(self) -> None:
        self.execute(CreateTable(self.datasets, if_not_exists=True))
        self.execute(CreateTable(self.datasets_versions, if_not_exists=True))

    def init_db(self, prefix: str = "", is_new: bool = True):
        assert self.listing_table_name, "Missing listing_table_name"
        table = self.nodes.table
        partials_table = self.partials
        ig = self.id_generator
        if not prefix or is_new:
            self.execute(DropTable(table, if_exists=True))
            self.execute(DropTable(partials_table, if_exists=True))
            # Do not drop ID Generator, as this is shared across all buckets
        self.execute(CreateTable(table, if_not_exists=True))
        self.execute(CreateTable(partials_table, if_not_exists=True))
        self.execute(CreateTable(ig, if_not_exists=True))
        if not prefix or is_new:
            # If there is no prefix (indexing the whole bucket) or this is a new
            # bucket entry, then reset the id_generator for this bucket by deleting
            # any existing used last_id entries, and reinsert the zero last_id
            # as the start, as that indicates no ids have been used yet.
            partials_uri = f"partials:{self.uri}"
            self.execute(
                self.id_generator_delete().where(
                    (ig.c.uri == self.uri) | (ig.c.uri == partials_uri)
                )
            )
            self.execute(self.id_generator.insert().values(uri=self.uri, last_id=0))
            self.execute(self.id_generator.insert().values(uri=partials_uri, last_id=0))

    def clone(self, uri: Optional[str] = None) -> "SQLiteDataStorage":
        uri = uri or self.uri
        return SQLiteDataStorage(db_file=self.db_file, uri=uri)

    def clone_params(self) -> Tuple[Type[AbstractDataStorage], List, Dict[str, Any]]:
        """
        Returns the class, args, and kwargs needed to instantiate a cloned copy of this
        SQLiteDataStorage implementation, for use in separate processes or machines.
        """
        return (SQLiteDataStorage, [], {"db_file": self.db_file, "uri": self.uri})

    def close(self) -> None:
        """Closes any active database connections"""
        self.db.close()

    @retry_sqlite_locks
    def execute(
        self,
        query,
        cursor: Optional[sqlite3.Cursor] = None,
        conn=None,
    ) -> sqlite3.Cursor:
        if cursor:
            result = cursor.execute(*compile_statement(query))
        else:
            result = self.db.execute(*compile_statement(query))
        if isinstance(query, CreateTable) and query.element.indexes:
            for index in query.element.indexes:
                self.execute(CreateIndex(index, if_not_exists=True), cursor=cursor)
        return result

    @retry_sqlite_locks
    def executemany(
        self, query, params, cursor: Optional[sqlite3.Cursor] = None
    ) -> sqlite3.Cursor:
        if cursor:
            return cursor.executemany(compile_statement(query)[0], params)
        return self.db.executemany(compile_statement(query)[0], params)

    def _get_next_ids(self, uri: str, count: int) -> range:
        with self.db:
            # Transactions ensure no concurrency conflicts
            self.db.execute("BEGIN")
            ig = self.id_generator
            self.execute(
                self.id_generator_update()
                .where(ig.c.uri == uri)
                .values(last_id=ig.c.last_id + count)
            )
            # TODO: RETURNING might be a better option,
            # but is only supported on SQLite 3.35.0 or newer
            last_id = self.execute(
                self.id_generator_select(ig.c.last_id).where(ig.c.uri == uri)
            ).fetchone()[0]

        return range(last_id - count + 1, last_id + 1)

    def create_dataset_rows_table(
        self,
        name: str,
        custom_columns: Sequence["sqlalchemy.Column"] = (),
        if_not_exists: bool = True,
    ) -> Table:
        table = self.schema.dataset_row_cls.new_table(
            name, custom_columns=custom_columns, metadata=self.metadata
        )
        q = CreateTable(table, if_not_exists=if_not_exists)
        self.execute(q)
        return table

    def _get_dataset_row_values(
        self,
        name: str,
        columns: Optional[Sequence[str]] = None,
        limit: Optional[int] = 20,
        version: Optional[int] = None,
        source: Optional[str] = None,
    ) -> Iterator[Dict[str, Any]]:
        dataset = self.get_dataset(name)

        dr = self.dataset_rows(dataset.id, version)
        select_columns = []
        if columns:
            select_columns = [getattr(dr.c, c) for c in columns]
        query = dr.select(*select_columns)
        if source:
            query = query.where(dr.c.source == source)
        if limit:
            query = query.limit(limit)

        cur = self.db.cursor()
        cur.row_factory = sqlite3.Row  # type: ignore[assignment]

        rows = self.execute(query, cursor=cur)
        for row in rows:
            yield dict(row)

    def get_dataset_sources(self, name: str, version: Optional[int]) -> List[str]:
        dataset = self.get_dataset(name)
        dr = self.dataset_rows(dataset.id, version)

        query = dr.select(dr.c.source).distinct()
        cur = self.db.cursor()
        cur.row_factory = sqlite3.Row  # type: ignore[assignment]

        return [dict(row)["source"] for row in self.execute(query, cursor=cur)]

    def create_shadow_dataset(
        self,
        name: str,
        sources: List[str] = None,
        query_script: str = "",
        create_rows: Optional[bool] = True,
        custom_columns: Sequence["sqlalchemy.Column"] = (),
    ) -> DatasetRecord:
        """Creates new shadow dataset if it doesn't exist yet"""
        with self.db:
            self.db.execute("begin")

            d = self.datasets
            self.execute(
                sqlite.insert(d)
                .values(
                    name=name,
                    shadow=True,
                    status=DatasetStatus.CREATED,
                    created_at=datetime.now(timezone.utc),
                    error_message="",
                    error_stack="",
                    script_output="",
                    sources="\n".join(sources) if sources else "",
                    query_script=query_script,
                )
                .on_conflict_do_nothing(index_elements=["name"])
            )
            dataset = self.get_dataset(name)
            assert dataset.shadow

            # Reassign custom columns to the new table.
            custom_cols = [
                saColumn(c.name, c.type, nullable=c.nullable) for c in custom_columns
            ]
            if create_rows:
                table_name = self.dataset_table_name(dataset.id)
                self.create_dataset_rows_table(table_name, custom_cols)
                dataset = self.update_dataset_status(dataset, DatasetStatus.PENDING)

            return dataset  # type: ignore[return-value]

    def insert_into_shadow_dataset(
        self, name: str, uri: str, path: str, recursive=False
    ) -> None:
        dataset = self.get_dataset(name)
        assert dataset.shadow

        dst = self.dataset_rows(dataset.id)  # Destination (dataset table).
        src = self.nodes_table(uri)  # Source (nodes table).

        src_cols = {c.name for c in src.c}
        # Not including id
        dst_cols = {c.name for c in dst.c if c.name != "id"}
        cols = src_cols.intersection(dst_cols)
        cols.add("source")
        transfer_fields = list(cols)
        select_query = self.nodes_dataset_query(
            transfer_fields, path=path, recursive=recursive, uri=uri
        )

        insert_query = dst.insert().from_select(transfer_fields, select_query)
        self.execute(insert_query)

    def _rename_table(self, old_name: str, new_name: str):
        comp_old_name = quote_schema(old_name)
        comp_new_name = quote_schema(new_name)
        self.db.execute(f"ALTER TABLE {comp_old_name} RENAME TO {comp_new_name}")

    def create_dataset_version(
        self,
        name: str,
        version: int,
        sources="",
        query_script="",
        create_rows_table=True,
    ) -> DatasetRecord:
        with self.db:
            self.db.execute("begin")

            dataset = self.get_dataset(name)

            dv = self.datasets_versions
            self.execute(
                sqlite.insert(dv)
                .values(
                    dataset_id=dataset.id,
                    version=version,
                    created_at=datetime.now(timezone.utc),
                    sources=sources,
                    query_script=query_script,
                )
                .on_conflict_do_nothing(index_elements=["dataset_id", "version"])
            )

            if create_rows_table:
                table_name = self.dataset_table_name(dataset.id, version)
                self.create_dataset_rows_table(table_name)

            return dataset

    def merge_dataset_rows(
        self,
        src: DatasetRecord,
        dst: DatasetRecord,
        src_version: Optional[int] = None,
        dst_version: Optional[int] = None,
    ) -> None:
        dst_empty = False

        if not self.has_table(self.dataset_table_name(src.id, src_version)):
            # source table doesn't exist, nothing to do
            return

        if not self.has_table(self.dataset_table_name(dst.id, dst_version)):
            # destination table doesn't exist, create it
            self.create_dataset_rows_table(self.dataset_table_name(dst.id))
            dst_empty = True

        src_dr = self.dataset_rows(src.id, src_version).table
        dst_dr = self.dataset_rows(dst.id, dst_version).table
        dst_dr_latest = self.dataset_rows(dst.id, dst.latest_version).table

        # Not including id
        merge_fields = [c for c in DATASET_CORE_COLUMN_NAMES if c != "id"]

        select_src = select(*(getattr(src_dr.c, f) for f in merge_fields))
        select_dst_latest = select(*(getattr(dst_dr_latest.c, f) for f in merge_fields))

        union_query = sqlalchemy.union(select_src, select_dst_latest)

        if dst_empty:
            # we don't need union, but just select from source to destination
            insert_query = sqlite.insert(dst_dr).from_select(merge_fields, select_src)
        else:
            insert_query = (
                sqlite.insert(dst_dr)
                .from_select(merge_fields, union_query)
                .prefix_with("OR IGNORE")
            )

        self.execute(insert_query)

    def copy_shadow_dataset_rows(self, src: DatasetRecord, dst: DatasetRecord) -> None:
        assert src.shadow
        assert dst.shadow

        if not self.has_table(self.dataset_table_name(src.id)):
            # source table doesn't exist, nothing to do
            return

        src_dr = self.dataset_rows(src.id).table

        if not self.has_table(self.dataset_table_name(dst.id)):
            # Destination table doesn't exist, create it
            custom_columns = [
                c
                for c in src_dr.c
                if c.name not in [c.name for c in DATASET_CORE_COLUMN_NAMES]
            ]
            self.create_dataset_rows_table(
                self.dataset_table_name(dst.id), custom_columns=custom_columns
            )

        dst_dr = self.dataset_rows(dst.id).table

        # Not including id
        src_fields = [c.name for c in src_dr.c if c.name != "id"]
        select_src = select(*(getattr(src_dr.c, f) for f in src_fields))
        insert_query = sqlite.insert(dst_dr).from_select(src_fields, select_src)

        self.execute(insert_query)

    def remove_shadow_dataset(self, dataset: DatasetRecord, drop_rows=True) -> None:
        with self.db:
            self.db.execute("begin")
            d = self.datasets
            self.execute(self.datasets_delete().where(d.c.id == dataset.id))
            if drop_rows:
                table_name = self.dataset_table_name(dataset.id)
                self.execute(DropTable(Table(table_name, MetaData())))

    async def insert_entry(self, entry: Dict[str, Any]) -> int:
        return (
            self.execute(
                self.nodes.insert().values(self._prepare_node(entry))
            ).lastrowid
            or 0
        )

    async def insert_entries(self, entries: Iterable[Dict[str, Any]]) -> None:
        self.executemany(
            self.nodes.insert().values({f: bindparam(f) for f in self.node_fields[1:]}),
            map(self._prepare_node, entries),
        )

    def insert_dataset_rows(
        self, name: str, rows: Optional[Iterable[Dict[str, Any]]]
    ) -> None:
        def _prepare_row(row):
            if "id" in row:
                del row["id"]  # id will be implicitly created by SQLite
            row["parent_id"] = None  # parent_id is deprecated and not used any more
            return row

        if not rows:
            return

        dataset = self.get_dataset(name)
        assert dataset.shadow

        dst = self.dataset_rows(dataset.id)
        self.executemany(
            dst.insert().values(
                {f: bindparam(f) for f in [c.name for c in dst.c if c.name != "id"]}
            ),
            map(_prepare_row, rows),
        )

    def create_storage_if_not_registered(
        self, uri: str, symlinks: bool = False
    ) -> None:
        s = self.storages
        self.execute(
            sqlite.insert(s)
            .values(
                uri=uri,
                status=StorageStatus.CREATED,
                symlinks=symlinks,
                error_message="",
                error_stack="",
            )
            .on_conflict_do_nothing()
        )

    def find_stale_storages(self):
        """
        Finds all pending storages for which the last inserted node has happened
        before STALE_HOURS_LIMIT hours, and marks it as STALE
        """
        with self.db:
            self.db.execute("begin")
            s = self.storages
            pending_storages = map(
                Storage._make,
                self.execute(
                    self.storages_select().where(s.c.status == StorageStatus.PENDING)
                ),
            )
            for storage in pending_storages:
                if storage.is_stale:
                    print(f"Marking storage {storage.uri} as stale")
                    self._mark_storage_stale(storage.id)

    def register_storage_for_indexing(
        self,
        uri: str,
        force_update: bool = True,
        prefix: str = "",
    ) -> Tuple[Storage, bool, bool, bool]:
        """
        Prepares storage for indexing operation.
        This method should be called before index operation is started
        It returns:
            - storage, prepared for indexing
            - boolean saying if indexing is needed
            - boolean saying if indexing is currently pending (running)
            - boolean saying if the storage is newly registered
        """
        # This ensures that all calls to the DB are in a single transaction
        # and commit is automatically called once this function returns
        with self.db:
            self.db.execute("begin")

            # Create storage if it doesn't exist
            self.create_storage_if_not_registered(uri)
            storage = self.get_storage(uri)

            if storage.status == StorageStatus.PENDING:
                return storage, False, True, False

            elif storage.is_expired or storage.status == StorageStatus.STALE:
                storage = self.mark_storage_pending(storage)
                return storage, True, False, False

            elif storage.status == StorageStatus.COMPLETE and not force_update:
                return storage, False, False, False

            elif (
                storage.status == StorageStatus.PARTIAL and prefix and not force_update
            ):
                if self._check_partial_index_valid(prefix):
                    return storage, False, False, False
                self._delete_partial_index(prefix)
                return storage, True, False, False

            else:
                is_new = storage.status == StorageStatus.CREATED
                storage = self.mark_storage_pending(storage)
                return storage, True, False, is_new

    def mark_storage_indexed(
        self,
        uri: str,
        status: int,
        ttl: int,
        end_time: Optional[datetime] = None,
        prefix: str = "",
        partial_id: int = 0,
        error_message: str = "",
        error_stack: str = "",
    ) -> None:
        if status == StorageStatus.PARTIAL and not prefix:
            raise AssertionError("Partial indexing requires a prefix")

        if end_time is None:
            end_time = datetime.now(timezone.utc)
        expires = Storage.get_expiration_time(end_time, ttl)

        with self.db:
            self.db.execute("BEGIN")

            s = self.storages
            self.execute(
                self.storages_update()
                .where(s.c.uri == uri)
                .values(  # type: ignore [attr-defined]
                    timestamp=end_time,
                    expires=expires,
                    status=status,
                    last_inserted_at=end_time,
                    error_message=error_message,
                    error_stack=error_stack,
                )
            )

            if not self.listing_table_name:
                # This only occurs in tests
                return

            p = self.partials
            if status in {StorageStatus.COMPLETE, StorageStatus.FAILED}:
                # Delete remaining partial index paths
                # has_table cannot be used here, or this operation/transaction will fail
                if self.table_exists(self.partials.name):
                    # Only delete if this table exists
                    self.execute(self.partials_delete())
            elif status == StorageStatus.PARTIAL:
                dirprefix = posixpath.join(prefix, "")
                self.execute(
                    sqlite.insert(p)
                    .values(
                        path_str=dirprefix,
                        timestamp=end_time,
                        expires=expires,
                        partial_id=partial_id,
                    )
                    .on_conflict_do_update(
                        index_elements=["path_str"],
                        set_={"timestamp": end_time, "expires": expires},
                    )
                )

    def validate_paths(self) -> int:
        """Find and mark any invalid paths."""
        t1 = self.nodes.table
        t2 = t1.alias("t2")
        t3 = t1.alias("t3")

        q1 = update(t1).values(valid=False).where(t1.c.name == "", t1.c.parent != "")
        row_count = self.execute(q1).rowcount

        id_query = (
            select(t2.c.id)  # type: ignore[attr-defined]
            .select_from(t2)
            .join(
                t3,
                (t2.c.parent == t3.c.parent)
                & (t2.c.name == t3.c.name)
                & (t2.c.id != t3.c.id),
            )
            .where(
                t2.c.valid == true(),
                t2.c.dir_type == 0,
            )
        )
        q2 = (
            update(t1)
            .values(valid=False)
            .where(t1.c.id.in_(id_query))  # type: ignore[attr-defined]
        )
        row_count += self.execute(q2).rowcount

        if row_count:
            logger.warning(
                "File names that collide with directory names will be ignored. "
                f"Number found: {row_count}"
            )
        return row_count

    def instr(self, source, target) -> sqlalchemy.Boolean:
        return cast(func.instr(source, target), sqlalchemy.Boolean)

    def table_exists(self, name: str) -> bool:
        """
        Checks the sqlite_master table to check if the requested table exists
        """
        results = list(
            self.execute(
                select(sqlalchemy.text("name"))
                .select_from(sqlalchemy.text("sqlite_master"))
                .where(sqlalchemy.column("name") == name)
            )
        )
        if results and results[0] == name:
            return True
        return False

    def get_table(self, name: str) -> sqlalchemy.Table:
        # load table with latest schema to metadata
        self._reflect_tables(filter_tables=lambda t, _: t == name)
        return self.metadata.tables[name]

    def return_ds_hook(self, name: str) -> None:
        print(f"{PYTHON_SCRIPT_WRAPPER_CODE}{name}{PYTHON_SCRIPT_WRAPPER_CODE}")

    def add_column(self, table: Table, col_name: str, col_type: "TypeEngine"):
        """Adds a column to a table"""
        # trying to find the same column in a table
        table_col = table.c.get(col_name, None)
        if table_col is not None and table_col.type.python_type != col_type.python_type:
            raise InconsistentSignalType(
                f"Column {col_name} already exists with a type:"
                f" {table_col.type.python_type}"
                f", but trying to create it with different type: {col_type.python_type}"
            )
        if table_col is not None:
            # column with the same name and type already exist, nothing to do
            return

        table_name = quote_schema(table.name)
        col_name_comp = quote(col_name)
        col_type_comp = col_type.compile(dialect=sqlite_dialect)
        q = f"ALTER TABLE {table_name} ADD COLUMN {col_name_comp} {col_type_comp}"
        self.db.execute(q)

        # reload the table to self.metadata so the table object
        # self.metadata.tables[table.name] includes the new column
        self._reflect_tables(filter_tables=lambda t, _: t == table.name)

    def dataset_column_types(
        self, name: str, version=None, custom=False
    ) -> List[Dict[str, str]]:
        dataset = self.get_dataset(name)
        dr = self.dataset_rows(dataset.id, version)
        columns = dr.custom_columns if custom else dr.columns
        return [{"name": c.name, "type": c.type.python_type.__name__} for c in columns]

    #
    # Signals
    #

    def create_signals_table(self) -> SignalsTable:
        """
        Create an empty signals table for storing signals entries.
        """
        tbl_name = self._table_name(self.uri, self.SIGNALS_TABLE_PREFIX)
        tbl = SignalsTable(tbl_name, [], self.metadata)
        q = CreateTable(tbl.table)
        self.execute(q)
        return tbl

    def extend_index_with_signals(self, index: "schema.Table", signals: SignalsTable):
        """
        Extend a nodes table with a signals table.
        This will result in the original index table being replaced
        with a table that is a join between the signals table and the
        index table (joining on the id column).
        """

        with self.db:
            # Create temporary table.
            join_tbl_name = "tmp_" + index.name

            signal_columns = [c for c in signals.table.c if c.name != "id"]

            join_tbl = self.schema.node_cls.new_table(
                join_tbl_name,
                [self.schema.node_cls.copy_signal_column(c) for c in signal_columns],
                self.metadata,
            )
            try:
                self.execute(CreateTable(join_tbl))

                # Query joining original index table and signals table.
                index_cols = {c.name for c in index.table.c}
                duplicate_signal_cols = {
                    c.name
                    for c in signals.table.c
                    if c.name in index_cols and c.name != "id"
                }
                select_cols = [
                    # columns from index table
                    *[c for c in index.table.c if c.name not in duplicate_signal_cols],
                    # coalesce columns already in index table
                    *[
                        func.coalesce(*cc).label(cc[0].name)
                        for cc in zip(
                            [index.table.c[col] for col in duplicate_signal_cols],
                            [signals.table.c[col] for col in duplicate_signal_cols],
                        )
                    ],
                    # columns from signals table
                    *[c for c in signal_columns if c.name not in duplicate_signal_cols],
                ]
                q = sqlalchemy.select(*select_cols).select_from(
                    index.table.outerjoin(
                        signals.table, index.c.id == signals.table.c.id
                    )
                )

                cols = [c.name for c in select_cols]

                # Write results of query to the new index table.
                self.execute(sqlalchemy.insert(join_tbl).from_select(cols, q))
                # Replace original table with extended one.
                self.execute(DropTable(index.table))
                self._rename_table(join_tbl_name, index.name)
            finally:
                self.execute(DropTable(join_tbl, if_exists=True))
