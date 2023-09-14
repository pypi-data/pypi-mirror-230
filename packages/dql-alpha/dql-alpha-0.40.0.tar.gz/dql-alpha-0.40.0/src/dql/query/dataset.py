import os
import random
import string
import subprocess  # nosec B404
import sys
from abc import ABC, abstractmethod
from copy import copy
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
)

import sqlalchemy
from attrs import frozen
from dill import dumps  # nosec B403
from sqlalchemy.sql import func as f
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.expression import label

from dql.catalog import QUERY_SCRIPT_INVALID_LAST_STATEMENT_EXIT_CODE, get_catalog
from dql.data_storage.schema import DATASET_CORE_COLUMN_NAMES
from dql.data_storage.schema import DatasetRow as DatasetRowSchema
from dql.dataset import DatasetRow
from dql.dataset import Status as DatasetStatus

from .schema import C
from .udf import UDFClassWrapper, UDFFactory, UDFType

if TYPE_CHECKING:
    from sqlalchemy.sql.elements import ColumnElement
    from sqlalchemy.sql.schema import Table
    from sqlalchemy.sql.selectable import SelectBase

    from dql.catalog import Catalog
    from dql.query.udf import Generator


BATCH_SIZE = 1000


class QueryGeneratorFunc(Protocol):
    def __call__(self, *columns: "ColumnElement") -> "SelectBase":
        ...


@frozen
class QueryGenerator:
    func: QueryGeneratorFunc
    columns: Tuple["ColumnElement", ...]

    def exclude(self, column_names):
        return self.func(*[c for c in self.columns if c.name not in column_names])

    def select(self, column_names=None):
        if column_names is None:
            return self.func(*self.columns)
        return self.func(*[c for c in self.columns if c.name in column_names])


@frozen
class StepResult:
    query_generator: QueryGenerator
    temp_table_names: Tuple[str, ...]


def step_result(
    func: QueryGeneratorFunc,
    columns: Iterable["ColumnElement"],
    temp_table_names: Iterable[str] = (),
) -> "StepResult":
    return StepResult(
        query_generator=QueryGenerator(func=func, columns=tuple(columns)),
        temp_table_names=tuple(temp_table_names),
    )


class StartingStep(ABC):
    """An initial query processing step, referencing a data source."""

    @abstractmethod
    def apply(self) -> "StepResult":
        ...


@frozen
class Step(ABC):
    """A query processing step (filtering, mutation, etc.)"""

    @abstractmethod
    def apply(self, query_generator: "QueryGenerator") -> "StepResult":
        """Apply the processing step."""


@frozen
class QueryStep(StartingStep):
    table: "Table"

    def apply(self):
        """Return the query for the table the query refers to."""
        table = self.table

        def q(*columns):
            return sqlalchemy.select(*columns)

        return step_result(q, table.c)


@frozen
class IndexingStep(StartingStep):
    path: str
    catalog: "Catalog"
    kwargs: Dict[str, Any]

    def apply(self):
        """Return the query for the table the query refers to."""
        self.catalog.index([self.path], **self.kwargs)
        uri, path = self.parse_path()

        def q(*columns):
            col_names = [c.name for c in columns]
            return self.catalog.data_storage.nodes_dataset_query(
                column_names=col_names, path=path, recursive=True, uri=uri
            )

        nodes = self.catalog.data_storage.nodes_table(uri)
        dataset_columns = DatasetRowSchema.calculate_all_columns([nodes])

        return step_result(q, dataset_columns)

    def parse_path(self):
        client_config = self.kwargs.get("client_config") or {}
        client, path = self.catalog.parse_url(self.path, **client_config)
        return client.uri, path


def generator_then_call(generator, func: Callable):
    """
    Yield items from generator then execute a function and yield
    its result.
    """
    yield from generator
    yield func() or []


@frozen
class Subtract(Step):
    """
    Calculates rows that are in a source query but are not in target query (diff)
    This can be used to do delta updates (calculate UDF only on newly added rows)
    Example:
        >>> ds = DatasetQuery(name="dogs_cats") # some older dataset with embeddings
        >>> ds_updated = (
                DatasetQuery("s3://ldb-public/remote/data-lakes/dogs-and-cats")
                .filter(C.size > 1000) # we can also filter out source query
                .subtract(ds)
                .add_signals(calc_embeddings) # calculae embeddings only on new rows
                .union(ds) # union with old dataset that's missing new rows
                .save("dogs_cats_updated")
            )
    """

    dq: "DatasetQuery"
    catalog: "Catalog"

    def clone(self):
        return self.__class__(self.dq, self.catalog)

    def apply(self, query_generator):
        source_query = query_generator.exclude(("id", "parent_id"))
        target_query = self.dq.apply_steps().select()

        # creating temp table that will hold subtract results
        temp_table_name = "subtract_" + _random_string(6)
        custom_columns = [
            sqlalchemy.Column(col.name, col.type)
            for col in source_query.columns
            if col.name not in DATASET_CORE_COLUMN_NAMES
        ]
        subtract_table = self.catalog.data_storage.create_dataset_rows_table(
            temp_table_name,
            custom_columns=custom_columns,
            if_not_exists=False,
        )
        # query that selects all rows from source query that are not in a target
        # query (added diff)
        subtract_q = self.catalog.data_storage.subtract_query(
            source_query, target_query
        )

        insert_q = subtract_table.insert().from_select(
            source_query.selected_columns, subtract_q
        )

        self.catalog.data_storage.execute(insert_q)

        def q(*columns):
            return sqlalchemy.select(*columns).select_from(subtract_table)

        return step_result(q, subtract_table.c, temp_table_names=[subtract_table.name])


@frozen
class UDFSignal(Step):
    """Add a custom column to the result set."""

    udf: UDFType
    catalog: "Catalog"
    processes: Union[bool, int] = False
    workers: Union[bool, int] = False
    min_task_size: Optional[int] = None

    def clone(self):
        return self.__class__(self.udf, self.catalog)

    def apply(self, query_generator):
        query = query_generator.select()
        tbl, cols = self.udf_results_table(query)
        signal_cols = {c.name: c for c in cols}
        # Construct a new query that will join the udf-generated partial table.
        subq = query.subquery()

        def q(*columns):
            cols1 = []
            cols2 = []
            for c in columns:
                cols.append(signal_cols.get(c.name, c))
                if c.name in signal_cols.keys():
                    cols2.append(c)
                else:
                    cols1.append(c)

            if cols2:
                return (
                    sqlalchemy.select(*cols1)
                    .select_from(subq)
                    .join(tbl, tbl.c.id == subq.c.id)
                    .add_columns(*cols2)
                )
            return sqlalchemy.select(*cols1).select_from(subq)

        return step_result(q, [*subq.c, *cols], temp_table_names=[tbl.name])

    def udf_results_table(self, query):
        """
        Create and populate a temporary UDF results table, this table
        will have an id column for joining to the original query and
        one or more columns for generated signals.
        """
        if isinstance(self.udf, UDFClassWrapper):
            udf = self.udf()
        else:
            udf = self.udf

        id_cols = [c for c in query.selected_columns if c.name == "id"]
        cols = [
            sqlalchemy.Column(col_name, col_type) for (col_name, col_type) in udf.output
        ]

        temp_table_name = "udf_" + _random_string(6)
        tbl = self.catalog.data_storage.create_udf_table(
            temp_table_name,
            id_cols[0].type,
            cols,
        )

        try:
            if self.workers:
                from dql.catalog.loader import get_distributed_class

                distributor = get_distributed_class(min_task_size=self.min_task_size)
                distributor(udf, self.catalog, tbl, query, self.workers, self.processes)
            elif self.processes:
                # Parallel processing (faster for more CPU-heavy UDFs)
                udf_info = {
                    "udf": udf,
                    "catalog_init": self.catalog.get_init_params(),
                    "data_storage_params": self.catalog.data_storage.clone_params(),
                    "table": tbl,
                    "query": query,
                    "processes": self.processes,
                }
                process_data = dumps(udf_info, recurse=True)
                # Run the UDFDispatcher in another process to avoid needing
                # if __name__ == '__main__': in user scripts
                # pylint: disable=W1510
                result = subprocess.run(  # nosec B603, B607
                    ["dql", "--internal-run-udf"],
                    input=process_data,
                )
                if result.returncode != 0:
                    raise RuntimeError("UDF Execution Failed!")
            else:
                # Otherwise process single-threaded (faster for smaller UDFs)
                execute = self.catalog.data_storage.execute
                selected_columns = [col.name for col in query.selected_columns]
                udf_inputs = (
                    DatasetRow.from_result_row(selected_columns, r)
                    for r in execute(query)
                )

                # Optionally instantiate the UDF instance if a class is provided.
                if isinstance(udf, UDFFactory):
                    udf = udf()
                udf_results = (udf(self.catalog, row) for row in udf_inputs)
                if hasattr(udf, "finalize"):
                    udf_results = generator_then_call(udf_results, udf.finalize)

                rows = []
                for udf_output in udf_results:
                    if not udf_output:
                        continue
                    rows.extend(udf_output)
                    if len(rows) > BATCH_SIZE:
                        update = tbl.insert().values(rows)
                        execute(update)
                        rows.clear()
                if rows:
                    update = tbl.insert().values(rows)
                    execute(update)
            return tbl, cols
        except Exception:
            # Close any open database connections if an error is encountered
            self.catalog.data_storage.close()
            raise


@frozen
class RowGenerator(Step):
    """Extend dataset with new rows."""

    generator: "Generator"
    catalog: "Catalog"

    def clone(self):
        return self.__class__(self.generator, self.catalog)

    def apply(self, query_generator):
        query = query_generator.select()
        # Create a temporary table.
        temp_table_name = "generated_" + _random_string(6)
        selected_columns = [col.name for col in query.selected_columns]
        custom_columns: List["sqlalchemy.Column"] = [
            sqlalchemy.Column(col.name, col.type)
            for col in query.selected_columns
            if col.name not in DATASET_CORE_COLUMN_NAMES
        ]
        self.catalog.data_storage.create_dataset_rows_table(
            temp_table_name,
            custom_columns=custom_columns,
            if_not_exists=False,
        )
        tbl = self.catalog.data_storage.get_table(temp_table_name)

        execute = self.catalog.data_storage.execute

        results = (
            DatasetRow.from_result_row(selected_columns, r) for r in execute(query)
        )
        rows = []
        for row in results:
            for new_entry in self.generator(self.catalog, row):
                rows.append(new_entry)
                if len(rows) >= BATCH_SIZE:
                    execute(tbl.insert().values(rows))
                    rows.clear()
        if rows:
            execute(tbl.insert().values(rows))

        original_query = query.subquery()
        table_query = tbl.select().subquery()
        original_cols = [label(c.name, c) for c in original_query.columns]
        table_cols = [label(c.name, c) for c in table_query.columns]

        def q(*columns):
            names = {c.name for c in columns}
            cols1 = [c for c in original_cols if c.name in names]
            cols2 = [
                c for c in table_cols if c.name in names
            ]  # Columns for the generated table.
            q = sqlalchemy.union_all(
                sqlalchemy.select(*cols1).select_from(original_query),
                sqlalchemy.select(*cols2).select_from(table_query),
            )
            return q

        return step_result(q, [*original_cols], temp_table_names=[temp_table_name])


@frozen
class SQLClause(Step, ABC):
    def apply(self, query_generator):
        query = query_generator.select()
        new_query = self.apply_sql_clause(query)

        def q(*columns):
            return new_query.with_only_columns(*columns)

        return step_result(q, new_query.selected_columns)

    @abstractmethod
    def apply_sql_clause(self, query):
        pass


@frozen
class SQLSelect(SQLClause):
    args: Tuple["ColumnElement", ...]

    def apply_sql_clause(self, query):
        subquery = query.subquery()
        args = [subquery.c[c] if isinstance(c, str) else c for c in self.args]
        if not args:
            args = subquery.c
        return sqlalchemy.select(*args).select_from(subquery)


@frozen
class SQLSelectExcept(SQLClause):
    args: Tuple[str, ...]

    def apply_sql_clause(self, query):
        subquery = query.subquery()
        names = set(self.args)
        args = [c for c in subquery.c if c.name not in names]
        return sqlalchemy.select(*args).select_from(subquery)


@frozen
class SQLMutate(SQLClause):
    args: Tuple["ColumnElement", ...]

    def apply_sql_clause(self, query):
        subquery = query.subquery()
        return sqlalchemy.select(*subquery.c, *self.args).select_from(subquery)


@frozen
class SQLFilter(SQLClause):
    expressions: Tuple["ColumnElement", ...]

    def __and__(self, other):
        return self.__class__(self.expressions + other)

    def apply_sql_clause(self, query):
        # Makes sure there is no ambiguity with column names.
        # This adds a real table name in the left side of expression.
        # e.g size > :size => <table_name>.size > :size
        def _fix_binary_expression(exp):
            if isinstance(exp.left, C):
                exp.left = source_table.c[str(exp.left)]

        def _traverse_expressions(exp):
            if isinstance(exp, BinaryExpression):
                _fix_binary_expression(exp)
                return
            if hasattr(exp, "get_children"):
                for ch in exp.get_children():
                    _traverse_expressions(ch)

        source_table = query.get_final_froms()[0]
        for exp in self.expressions:
            _traverse_expressions(exp)

        return query.filter(*self.expressions)


@frozen
class SQLOrderBy(SQLClause):
    args: Tuple["ColumnElement", ...]

    def apply_sql_clause(self, query):
        return query.order_by(*self.args)


@frozen
class SQLLimit(SQLClause):
    n: int

    def apply_sql_clause(self, query):
        return query.limit(self.n)


@frozen
class SQLCount(SQLClause):
    def apply_sql_clause(self, query):
        return sqlalchemy.select(f.count(1)).select_from(query.subquery())


@frozen
class SQLUnion(Step):
    query1: "SQLQuery"
    query2: "SQLQuery"

    def apply(self, query_generator):
        q1 = self.query1.apply_steps().select().subquery()
        q2 = self.query2.apply_steps().select().subquery()
        columns1, columns2 = fill_columns(q1.columns, q2.columns)

        def q(*columns):
            names = {c.name for c in columns}
            col1 = [c for c in columns1 if c.name in names]
            col2 = [c for c in columns2 if c.name in names]
            return (
                sqlalchemy.select(*col1)
                .select_from(q1)
                .union_all(sqlalchemy.select(*col2).select_from(q2))
            )

        return step_result(q, columns1)


def fill_columns(
    *column_iterables: Iterable["ColumnElement"],
) -> List[List["ColumnElement"]]:
    column_dicts = [{c.name: c for c in columns} for columns in column_iterables]
    combined_columns = {n: c for col_dict in column_dicts for n, c in col_dict.items()}

    result: List[List["ColumnElement"]] = [[] for _ in column_dicts]
    for n in combined_columns:
        col = next(col_dict[n] for col_dict in column_dicts if n in col_dict)
        for col_dict, out in zip(column_dicts, result):
            if n in col_dict:
                out.append(col_dict[n])
            else:
                # Cast the NULL to ensure all columns are aware of their type
                # Label it to ensure it's aware of its name
                out.append(sqlalchemy.cast(sqlalchemy.null(), col.type).label(n))
    return result


SQLQueryT = TypeVar("SQLQueryT", bound="SQLQuery")


class SQLQuery:
    def __init__(
        self,
        starting_step: StartingStep,
        steps: Optional[Iterable["Step"]] = None,
        catalog: Optional["Catalog"] = None,
        client_config=None,
    ):  # pylint: disable=super-init-not-called
        self.steps: List["Step"] = list(steps) if steps is not None else []
        self.starting_step: StartingStep = starting_step
        self.catalog = catalog or get_catalog(client_config=client_config)
        self._chunk_index: Optional[int] = None
        self._chunk_total: Optional[int] = None
        self.temp_table_names: List[str] = []

    def __iter__(self):
        return iter(self.results())

    def __or__(self, other):
        return self.union(other)

    def apply_steps(self):
        """
        Apply the steps in the query and return the resulting
        sqlalchemy.SelectBase.
        """
        query = self.clone()

        index = os.getenv("DQL_QUERY_CHUNK_INDEX", self._chunk_index)
        total = os.getenv("DQL_QUERY_CHUNK_TOTAL", self._chunk_total)

        if None not in (index, total):
            index, total = int(index), int(total)  # os.getenv returns str

            if not (0 <= index < total):
                raise ValueError("chunk index must be between 0 and total")

            # Prepend the chunk filter to the step chain.
            query = query.filter(C.random % total == index)
            query.steps = query.steps[-1:] + query.steps[:-1]

        result = query.starting_step.apply()
        self.temp_table_names.extend(result.temp_table_names)
        for step in query.steps:
            result = step.apply(
                result.query_generator
            )  # a chain of steps linked by results
            self.temp_table_names.extend(result.temp_table_names)
        return result.query_generator

    def results(self, row_factory=None, **kwargs):
        try:
            query = self.apply_steps()
            execute = self.catalog.data_storage.data_execute

            query = query.select()
            if row_factory:
                selected_columns = [col.name for col in query.selected_columns]
                result = [
                    row_factory(selected_columns, r) for r in execute(query, **kwargs)
                ]
            else:
                result = list(execute(query, **kwargs))
        finally:
            self.catalog.data_storage.cleanup_temp_tables(self.temp_table_names)
        return result

    def clone(self: SQLQueryT) -> SQLQueryT:
        obj = copy(self)
        obj.steps = obj.steps.copy()
        return obj

    def select(self, *args, **kwargs):
        """
        Select the given columns or expressions using a subquery.

        If used with no arguments, this simply creates a subquery and
        select all columns from it.

        Note that the `save` function expects default dataset columns to
        be present. This function is meant to be followed by a call to
        `results` if used to exclude any default columns.

        Example:
            >>> ds.select(C.name, C.size * 10).results()
            >>> ds.select(C.name, size10x=C.size * 10).order_by(C.size10x).results()
        """
        named_args = [v.label(k) for k, v in kwargs.items()]
        query = self.clone()
        query.steps.append(SQLSelect((*args, *named_args)))
        return query

    def select_except(self, *args):
        """
        Exclude certain columns from this query using a subquery.

        Note that the `save` function expects default dataset columns to
        be present. This function is meant to be followed by a call to
        `results` if used to exclude any default columns.

        Example:
            >>> (
            ...     ds.mutate(size10x=C.size * 10)
            ...     .order_by(C.size10x)
            ...     .select_exclude(C.size10x)
            ...     .results()
            ... )
        """

        if not args:
            raise TypeError("select_except expected at least 1 argument, got 0")
        args = [c if isinstance(c, str) else c.name for c in args]
        query = self.clone()
        query.steps.append(SQLSelectExcept(args))
        return query

    def select_default(self):
        """
        Select only the default dataset columns using a subquery.

        This assumes that none of the default dataset columns have
        already been excluded from this query. This is useful if you've
        added columns with `mutate` or `select` calls for filtering but
        only want the default columns in the final output.

        Example:
            >>> (
            ...     ds.mutate(size10x=C.size * 10)
            ...     .order_by(C.size10x)
            ...     .select_default()
            ...     .results()
            ... )
        """
        query = self.clone()
        query.steps.append(SQLSelect((*DATASET_CORE_COLUMN_NAMES,)))
        return query

    def mutate(self, *args, **kwargs):
        """
        Add new columns to this query.

        This function selects all existing columns from this query and
        adds in the new columns specified.

        Example:
            >>> ds.mutate(size10x=C.size * 10).order_by(C.size10x).results()
        """
        args = [v.label(k) for k, v in dict(args, **kwargs).items()]
        query = self.clone()
        query.steps.append(SQLMutate((*args,)))
        return query

    def filter(self, *args):
        query = self.clone()
        steps = query.steps
        if steps and isinstance(steps[-1], SQLFilter):
            steps[-1] = steps[-1] & args
        else:
            steps.append(SQLFilter(args))
        return query

    def order_by(self, *args):
        query = self.clone()
        query.steps.append(SQLOrderBy(args))
        return query

    def limit(self, n: int):
        query = self.clone()
        query.steps.append(SQLLimit(n))
        return query

    def count(self):
        query = self.clone()
        query.steps.append(SQLCount())
        return query.results()[0][0]

    def union(self, dataset_query):
        left = self.clone()
        right = dataset_query.clone()
        new_query = self.clone()
        new_query.steps = [SQLUnion(left, right)]
        return new_query

    def chunk(self, index: int, total: int):
        """Split a query into smaller chunks for e.g. parallelization.
        Example:
            >>> query = DatasetQuery(...)
            >>> chunk_1 = query._chunk(0, 2)
            >>> chunk_2 = query._chunk(1, 2)
        Note:
            Bear in mind that `index` is 0-indexed but `total` isn't.
            Use 0/3, 1/3 and 2/3, not 1/3, 2/3 and 3/3.
        """
        query = self.clone()
        query._chunk_index, query._chunk_total = index, total
        return query


class DatasetQuery(SQLQuery):
    def __init__(
        self,
        path: str = "",
        name: str = "",
        version: Optional[int] = None,
        catalog=None,
        client_config=None,
    ):
        if catalog is None:
            catalog = get_catalog(client_config=client_config)

        data_storage = catalog.data_storage
        starting_step: StartingStep
        if path:
            starting_step = IndexingStep(
                path, catalog, {"client_config": client_config}
            )
        elif name:
            ds = data_storage.get_dataset(name)
            version = version or ds.latest_version
            ds_table = catalog.data_storage.get_table(
                data_storage.dataset_table_name(dataset_id=ds.id, version=version)
            )
            starting_step = QueryStep(ds_table)
        else:
            raise ValueError("must provide path or name")

        super().__init__(
            starting_step=starting_step, catalog=catalog, client_config=client_config
        )

    def add_signals(
        self,
        udf: UDFType,
        processes: Union[bool, int] = False,
        workers: Union[bool, int] = False,
        min_task_size: Optional[int] = None,
    ):
        """
        Adds one or more signals based on the results from the provided UDF.

        Processes can optionally be specified as >= 1 for parallel processing with a
        specific number of processes, or set to True for the default of
        the number of CPUs (cores) on the current machine.

        For distributed processing with the appropriate distributed module installed,
        workers can optionally be specified as >= 1 for a specific number of workers,
        or set to True for the default of all nodes in the cluster.
        As well, a custom minimum task size (min_task_size) can be provided to send
        at least that minimum number of rows to each distributed worker, mostly useful
        if there are a very large number of small tasks to process.
        """
        query = self.clone()
        query.steps.append(
            UDFSignal(
                udf,
                self.catalog,
                processes=processes,
                workers=workers,
                min_task_size=min_task_size,
            )
        )
        return query

    def started_from_index(self) -> bool:
        return isinstance(self.starting_step, IndexingStep)

    def subtract(self, dq: "DatasetQuery"):
        query = self.clone()
        # taking source_uri if indexing step, since it's needed for calculating
        # tables diff
        query.steps.append(Subtract(dq, self.catalog))
        return query

    def generate(self, generator: "Generator"):
        query = self.clone()
        steps = query.steps
        steps.append(RowGenerator(generator, self.catalog))
        return query

    def save(self, name: str, **kwargs):
        """Save the query as a shadow dataset."""
        try:
            query = self.apply_steps()

            # Save to a temporary table first.
            temp_table_name = f"tmp_{name}_" + _random_string(6)
            custom_columns: List["sqlalchemy.Column"] = [
                sqlalchemy.Column(col.name, col.type)
                for col in query.columns
                if col.name not in DATASET_CORE_COLUMN_NAMES
            ]
            temp_table = self.catalog.data_storage.create_dataset_rows_table(
                temp_table_name,
                custom_columns=custom_columns,
                if_not_exists=False,
            )
            # Exclude the id column and let the db create it to avoid unique
            # constraint violations, and parent_id is not used in datasets.
            cols = [
                col.name for col in temp_table.c if col.name not in ("id", "parent_id")
            ]

            self.catalog.data_storage.execute(
                sqlalchemy.insert(temp_table).from_select(
                    cols, query.exclude(("id", "parent_id"))
                ),
                **kwargs,
            )

            # Create a shadow dataset.
            self.catalog.data_storage.create_shadow_dataset(name, create_rows=False)
            dataset = self.catalog.data_storage.get_dataset(name)
            if dataset is None:
                raise RuntimeError(f"No dataset found with {name=}")
            # pylint: disable=protected-access
            table_name = self.catalog.data_storage.dataset_table_name(dataset.id)

            self.catalog.data_storage._rename_table(temp_table_name, table_name)
            self.catalog.data_storage.update_dataset_status(
                dataset, DatasetStatus.COMPLETE
            )
        finally:
            self.catalog.data_storage.cleanup_temp_tables(self.temp_table_names)


def return_ds(dataset_query: DatasetQuery) -> DatasetQuery:
    """
    Wrapper function that wraps the last statement of user query script for creating
    shadow dataset (user sees it as query results in the UI).
    Last statement MUST be instance of DatasetQuery, otherwise script exits with
    error code 10
    """

    if not isinstance(dataset_query, DatasetQuery):
        sys.exit(QUERY_SCRIPT_INVALID_LAST_STATEMENT_EXIT_CODE)

    if isinstance(dataset_query, DatasetQuery):
        ds_id = _random_string(6)
        ds_name = f"ds_return_{ds_id}"
        dataset_query.catalog.data_storage.return_ds_hook(ds_name)
        dataset_query.save(ds_name)
    return dataset_query


def _random_string(length: int) -> str:
    return "".join(
        random.choice(string.ascii_letters + string.digits)  # nosec B311
        for i in range(length)
    )
