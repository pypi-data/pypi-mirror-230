from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import WRAPPER_ASSIGNMENTS
from inspect import isclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from dql.catalog import Catalog

from .schema import Column, LocalFilename, Object

if TYPE_CHECKING:
    from dql.dataset import DatasetRow

ColumnType = Any

UDFParamSpec = Union[Column, Object, LocalFilename]

# Specification for the output of a UDF, a sequence of tuples containing
# the column name and the type.
UDFOutputSpec = Sequence[Tuple[str, ColumnType]]


class BatchingStrategy(ABC):
    """BatchingStrategy provides means of batching UDF executions."""

    def __init__(self, signal_names):
        self.signal_names = signal_names

    @abstractmethod
    def __call__(
        self, func: Callable, params: Tuple[int, Sequence[Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """Apply the provided parameters to the UDF."""

    @abstractmethod
    def finalize(self, func: Callable) -> Optional[List[Dict[str, Any]]]:
        """Execute the UDF with any parameter sets stored."""

    def _process_results(
        self, row_ids: List[int], results: Sequence[Sequence[Any]]
    ) -> List[Dict[str, Any]]:
        """Create a list of dictionaries representing UDF results."""
        r = []
        for row_id, result in zip(row_ids, results):
            signals = {
                signal_name: signal_value
                for (signal_name, signal_value) in zip(self.signal_names, result)
            }
            r.append(dict(id=row_id, **signals))
        return r


class NoBatching(BatchingStrategy):
    """
    NoBatching implements the default batching strategy, which is not to
    batch UDF calls.
    """

    def __call__(
        self, func: Callable, params: Tuple[int, Sequence[Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        (row_id, udf_params) = params
        return self._process_results([row_id], [func(*udf_params)])

    def finalize(self, func: Callable) -> Optional[List[Dict[str, Any]]]:
        return None


class Batch(BatchingStrategy):
    """
    Batch implements UDF call batching, where each execution of a UDF
    is passed a sequence of multiple parameter sets.
    """

    def __init__(self, count: int, signal_names: List[str]):
        super().__init__(signal_names)
        self.count = count
        self.batch: List[Sequence[Any]] = []

    def __call__(
        self, func: Callable, params: Tuple[int, Sequence[Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        self.batch.append(params)
        if len(self.batch) >= self.count:
            batch, self.batch = self.batch[: self.count], self.batch[self.count :]
            row_ids, params = tuple(zip(*batch))
            results = func(params)
            return self._process_results(row_ids, results)
        return None

    def finalize(self, func: Callable) -> Optional[List[Dict[str, Any]]]:
        if self.batch:
            row_ids, params = tuple(zip(*self.batch))
            self.batch.clear()
            results = func(params)
            return self._process_results(row_ids, results)
        return None


@dataclass
class UDFProperties:
    """Container for basic UDF properties."""

    output: UDFOutputSpec
    parameters: Sequence[UDFParamSpec]
    batch: int = 1

    def get_batching(self) -> BatchingStrategy:
        signal_names = [signal_name for (signal_name, _) in self.output]
        if self.batch == 1:
            return NoBatching(signal_names)
        elif self.batch > 1:
            return Batch(self.batch, signal_names)
        else:
            raise ValueError(f"invalid batch size {self.batch}")


def udf(
    output: UDFOutputSpec,
    parameters: Sequence[UDFParamSpec],
    method: Optional[str] = None,  # only used for class-based UDFs
    batch: int = 1,
):
    """
    Decorate a function or a class to be used as a UDF.

    The decorator expects both the outputs and inputs of the UDF to be specified.
    The outputs are defined as a collection of tuples containing the signal name
    and type.
    Parameters are defined as a list of column objects (e.g. C.name).
    Optionally, UDFs can be run on batches of rows to improve performance, this
    is determined by the 'batch' parameter. When operating on batches of inputs,
    the UDF function will be called with a single argument - a list
    of tuples containing inputs (e.g. ((input1_a, input1_b), (input2_a, input2b))).
    """
    properties = UDFProperties(output, parameters, batch)

    def decorator(udf_base: Union[Callable, Type]):
        if isclass(udf_base):
            return UDFClassWrapper(udf_base, properties, method=method)
        elif callable(udf_base):
            return UDFWrapper(udf_base, properties)

    return decorator


class UDFBase:
    """A base class for implementing stateful UDFs."""

    def __init__(
        self,
        func: Callable,
        properties: UDFProperties,
    ):
        self.func = func
        self.properties = properties
        self.batching = properties.get_batching()
        self.output = properties.output

    def __call__(
        self, catalog: "Catalog", row: "DatasetRow"
    ) -> Optional[List[Dict[str, Any]]]:
        params = []
        for p in self.properties.parameters:
            if isinstance(p, Column):
                params.append(row[p.name])
            elif isinstance(p, Object):
                client, _ = catalog.parse_url(row.source)
                uid = row.as_uid()
                if p.cache:
                    client.download(uid)
                with client.open_object(uid, use_cache=p.cache) as f:
                    obj: Any = p.reader(f)
                params.append(obj)
            elif isinstance(p, LocalFilename):
                client, _ = catalog.parse_url(row.source)
                uid = row.as_uid()
                client.download(uid)
                local_path = client.cache.get_path(uid)
                params.append(local_path)
            else:
                raise ValueError("unknown udf parameter")
        signals = self.batching(self.func, (row.id, params))
        return signals

    def finalize(self) -> Optional[List[Dict[str, Any]]]:
        """
        Execute the UDF with any parameter sets still held by
        the batching strategy.
        """
        return self.batching.finalize(self.func)


class UDFClassWrapper:
    """
    A wrapper for class-based (stateful) UDFs.
    """

    def __init__(
        self,
        udf_class: Type,
        properties: UDFProperties,
        method: Optional[str] = None,
    ):
        self.udf_class = udf_class
        self.udf_method = method
        self.properties = properties

    def __call__(self, *args, **kwargs):
        return UDFFactory(
            self.udf_class,
            args,
            kwargs,
            self.properties,
            self.udf_method,
        )


class UDFWrapper(UDFBase):
    """A wrapper class for function UDFs to be used in custom signal generation."""

    def __init__(
        self,
        func: Callable,
        properties: UDFProperties,
    ):
        super().__init__(func, properties)
        # This emulates the behavior of functools.wraps for a class decorator
        for attr in WRAPPER_ASSIGNMENTS:
            if hasattr(func, attr):
                setattr(self, attr, getattr(func, attr))

    # This emulates the behavior of functools.wraps for a class decorator
    def __repr__(self):
        return repr(self.func)


class UDFFactory:
    """
    A wrapper for late instantiation of UDF classes, primarily for use in parallelized
    execution.
    """

    def __init__(
        self,
        udf_class: Type,
        args,
        kwargs,
        properties: UDFProperties,
        method: Optional[str] = None,
    ):
        self.udf_class = udf_class
        self.udf_method = method
        self.args = args
        self.kwargs = kwargs
        self.properties = properties
        self.output = properties.output

    def __call__(self):
        udf_func = self.udf_class(*self.args, **self.kwargs)
        if self.udf_method:
            udf_func = getattr(udf_func, self.udf_method)

        return UDFWrapper(udf_func, self.properties)


def generator(*parameters: Union[UDFParamSpec, Type["Catalog"]]):
    def decorator(func: Callable):
        return Generator(func, *parameters)

    return decorator


class Generator:
    """A wrapper class for UDFs used to generate new dataset rows."""

    def __init__(
        self, func: Callable, *parameters: Union[UDFParamSpec, Type["Catalog"]]
    ):
        self.func = func
        self.parameters = parameters

    def __call__(self, catalog: "Catalog", row: "DatasetRow"):
        params = []
        for p in self.parameters:
            if isinstance(p, Column):
                params.append(row[p.name])
            elif isinstance(p, Object):
                with catalog.open_object(row) as f:
                    obj: Any = p.reader(f)
                params.append(obj)
            elif p is Catalog:
                params.append(catalog)
            else:
                raise ValueError("unknown udf parameter")
        yield from self.func(row, *params)


# UDFs can be callables or classes that instantiate into callables
UDFType = Union[Callable[["Catalog", "DatasetRow"], Any], UDFFactory, UDFClassWrapper]
