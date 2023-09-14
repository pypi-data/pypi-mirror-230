import asyncio
import logging
import os
import os.path
import posixpath
import shutil
import subprocess  # nosec B404
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union
from uuid import uuid4

import yaml
from attrs import asdict
from fsspec.implementations.local import LocalFileSystem
from tqdm import tqdm

from dql.cache import DQLCache
from dql.client import Client
from dql.data_storage import AbstractDataStorage
from dql.data_storage.schema import DatasetRow as DatasetRowSchema
from dql.data_storage.schema import parse_columns
from dql.dataset import (
    DATASET_PREFIX,
    DatasetMeta,
    DatasetRecord,
    DatasetRow,
    DatasetStats,
)
from dql.dataset import Status as DatasetStatus
from dql.dataset import create_dataset_uri, parse_dataset_uri
from dql.error import (
    ClientError,
    DatasetNotFoundError,
    InconsistentSignalType,
    PendingIndexingError,
    QueryScriptCompileError,
    QueryScriptDatasetNotFound,
    QueryScriptRunError,
)
from dql.listing import Listing
from dql.node import DirType, Node
from dql.remote.studio import StudioClient
from dql.storage import Status, Storage
from dql.utils import (
    DQLDir,
    dql_paths_join,
    get_remote_config,
    import_object,
    parse_params_string,
    read_config,
)

from .datasource import DataSource
from .formats import IndexingFormat, apply_processors

if sys.version_info < (3, 9):
    from dql.vendored import ast
    from dql.vendored.ast import Attribute, Call, Expr, Import, Load, Name, alias
else:
    import ast
    from ast import Attribute, Call, Expr, Import, Load, Name, alias

logger = logging.getLogger("dql")

DEFAULT_DATASET_DIR = "dataset"
DATASET_FILE_SUFFIX = ".edql"

TTL_INT = 4 * 60 * 60
PYTHON_SCRIPT_WRAPPER_CODE = "__ds__"

INDEX_INTERNAL_ERROR_MESSAGE = "Internal error on indexing"
DATASET_INTERNAL_ERROR_MESSAGE = "Internal error on creating dataset"
# exit code we use if last statement in query script is not instance of DatasetQuery
QUERY_SCRIPT_INVALID_LAST_STATEMENT_EXIT_CODE = 10


@dataclass
class NodeGroup:
    """Class for a group of nodes from the same source"""

    listing: Listing
    sources: List[DataSource]

    # The source path within the bucket
    # (not including the bucket name or s3:// prefix)
    source_path: str = ""
    updated_checksums: Optional[Dict[int, str]] = None
    is_edql: bool = False
    dataset_name: Optional[str] = None
    dataset_version: Optional[int] = None

    @property
    def is_dataset(self) -> bool:
        return bool(self.dataset_name)


def check_output_dataset_file(
    output: str,
    force: bool = False,
    dataset_filename: Optional[str] = None,
    skip_check_output: bool = False,
    skip_check_edql: bool = False,
) -> str:
    """
    Checks the output directory and dataset filename for existence or if they
    should be force-overwritten.
    """
    if not skip_check_output:
        if os.path.exists(output):
            if force:
                shutil.rmtree(output)
            else:
                raise RuntimeError(f"Output directory already exists: {output}")

    dataset_file = (
        dataset_filename if dataset_filename else output + DATASET_FILE_SUFFIX
    )
    if not skip_check_edql:
        if os.path.exists(dataset_file):
            if force:
                os.remove(dataset_file)
            else:
                raise RuntimeError(
                    f"Output dataset file already exists: {dataset_file}"
                )
    return dataset_file


def parse_edql_file(filename: str) -> List[Dict[str, Any]]:
    with open(filename, encoding="utf-8") as f:
        contents = yaml.safe_load(f)

    if not isinstance(contents, list):
        contents = [contents]

    for entry in contents:
        if not isinstance(entry, dict):
            raise ValueError(
                "Failed parsing EDQL file, "
                "each data source entry must be a dictionary"
            )
        if "data-source" not in entry or "files" not in entry:
            raise ValueError(
                "Failed parsing EDQL file, "
                "each data source entry must contain the "
                '"data-source" and "files" keys'
            )

    return contents


def prepare_output_for_cp(
    node_groups: List[NodeGroup],
    output: str,
    force: bool = False,
    edql_only: bool = False,
    no_edql_file: bool = False,
) -> Tuple[bool, Optional[str]]:
    total_node_count = 0
    for node_group in node_groups:
        if not node_group.sources:
            raise FileNotFoundError(
                f"No such file or directory: {node_group.source_path}"
            )
        total_node_count += len(node_group.sources)

    always_copy_dir_contents = False
    copy_to_filename = None

    if edql_only:
        return always_copy_dir_contents, copy_to_filename

    if not os.path.isdir(output):
        if all(n.is_dataset for n in node_groups):
            os.mkdir(output)
        elif total_node_count == 1:
            first_source = node_groups[0].sources[0]
            if first_source.is_container():
                if os.path.exists(output):
                    if force:
                        os.remove(output)
                    else:
                        raise FileExistsError(f"Path already exists: {output}")
                always_copy_dir_contents = True
                os.mkdir(output)
            else:  # Is a File
                if os.path.exists(output):
                    if force:
                        os.remove(output)
                    else:
                        raise FileExistsError(f"Path already exists: {output}")
                copy_to_filename = output
        else:
            raise FileNotFoundError(f"Is not a directory: {output}")

    if copy_to_filename and not no_edql_file:
        raise RuntimeError("File to file cp not supported with .edql files!")

    return always_copy_dir_contents, copy_to_filename


def collect_nodes_for_cp(
    node_groups: Iterable[NodeGroup],
    recursive: bool = False,
) -> Tuple[int, int]:
    total_size: int = 0
    total_files: int = 0

    # Collect all sources to process
    for node_group in node_groups:
        listing: Listing = node_group.listing
        valid_sources: List[DataSource] = []
        for dsrc in node_group.sources:
            if dsrc.is_single_object():
                total_size += dsrc.node.size
                total_files += 1
                valid_sources.append(dsrc)
            else:
                node = dsrc.node
                if not recursive:
                    print(f"{node.full_path} is a directory (not copied).")
                    continue
                add_size, add_files = listing.du(node, count_files=True)
                total_size += add_size
                total_files += add_files
                valid_sources.append(dsrc)

        node_group.sources = valid_sources

    return total_size, total_files


def download_node_groups(
    node_groups: Iterable[NodeGroup],
    bar_format: str,
    total_size: int,
    recursive: bool = False,
):
    download_progress_bar = tqdm(
        desc="Downloading files: ",
        unit="B",
        bar_format=bar_format,
        unit_scale=True,
        unit_divisor=1000,
        total=total_size,
    )

    # Download these nodes
    for node_group in node_groups:
        if not node_group.sources:
            continue
        listing: Listing = node_group.listing

        updated_checksums = listing.download_nodes(
            node_group.sources,
            total_size,
            recursive=recursive,
            shared_progress_bar=download_progress_bar,
        )
        node_group.updated_checksums = updated_checksums

    download_progress_bar.close()


def instantiate_node_groups(
    node_groups: Iterable[NodeGroup],
    output: str,
    bar_format: str,
    total_files: int,
    force: bool = False,
    recursive: bool = False,
    virtual_only: bool = False,
    always_copy_dir_contents: bool = False,
    copy_to_filename: Optional[str] = None,
) -> List[Dict[str, Any]]:
    instantiate_progress_bar = (
        None
        if virtual_only
        else tqdm(
            desc=f"Instantiating {output}: ",
            unit=" f",
            bar_format=bar_format,
            unit_scale=True,
            unit_divisor=1000,
            total=total_files,
        )
    )

    metafile_data = []

    # Instantiate these nodes
    for node_group in node_groups:
        if not node_group.sources:
            continue
        listing: Listing = node_group.listing
        source_path: str = node_group.source_path
        metafile_group = {
            "data-source": (
                listing.storage.to_dict(source_path)
                if not node_group.is_dataset
                else {"uri": listing.data_storage.uri}
            ),
            "files": [],
        }
        output_dir = output
        if copy_to_filename:
            output_dir = os.path.dirname(output)
            if not output_dir:
                output_dir = "."

        copy_dir_contents = always_copy_dir_contents or source_path.endswith("/")
        instantiated_nodes = listing.collect_nodes_to_instantiate(
            node_group.sources,
            copy_to_filename,
            recursive,
            copy_dir_contents,
            source_path,
            node_group.is_edql,
        )
        if node_group.updated_checksums:
            for n in instantiated_nodes:
                n.n.checksum = node_group.updated_checksums.get(n.n.id, n.n.checksum)

        if not virtual_only:
            listing.instantiate_nodes(
                instantiated_nodes,
                output_dir,
                total_files,
                force=force,
                shared_progress_bar=instantiate_progress_bar,
            )

        for node in instantiated_nodes:
            if not node.n.is_dir:
                metafile_group["files"].append(node.get_metafile_data())
        if metafile_group["files"]:
            metafile_data.append(metafile_group)

    if instantiate_progress_bar:
        instantiate_progress_bar.close()

    return metafile_data


def find_column_to_str(
    row: Tuple[Any, ...], field_lookup: Dict[str, int], src: DataSource, column: str
) -> str:
    if column == "du":
        return str(
            src.listing.du(
                {
                    f: row[field_lookup[f]]
                    for f in ["dir_type", "size", "parent", "name"]
                }
            )[0]
        )
    if column == "name":
        return row[field_lookup["name"]] or ""
    if column == "owner":
        return row[field_lookup["owner_name"]] or ""
    if column == "path":
        is_dir = row[field_lookup["dir_type"]] == DirType.DIR
        parent = row[field_lookup["parent"]]
        name = row[field_lookup["name"]]
        path = f"{parent}/{name}" if parent else name
        if is_dir and path:
            full_path = path + "/"
        else:
            full_path = path
        return src.get_node_full_path_from_path(full_path)
    if column == "size":
        return str(row[field_lookup["size"]])
    if column == "type":
        dt = row[field_lookup["dir_type"]]
        if dt == DirType.DIR:
            return "d"
        elif dt == DirType.FILE:
            return "f"
        elif dt == DirType.TAR_ARCHIVE:
            return "t"
        # Unknown - this only happens if a type was added elsewhere but not here
        return "u"
    return ""


class Catalog:
    def __init__(
        self,
        data_storage: AbstractDataStorage,
        cache_dir=None,
        tmp_dir=None,
        client_config=None,
    ):
        dql_dir = DQLDir(cache=cache_dir, tmp=tmp_dir)
        self.data_storage = data_storage
        self.cache = DQLCache(dql_dir.cache, dql_dir.tmp, data_storage)
        self.client_config = client_config
        self._init_params = {
            "cache_dir": cache_dir,
            "tmp_dir": tmp_dir,
        }

    def get_init_params(self) -> Dict[str, Any]:
        return {
            **self._init_params,
            "client_config": self.client_config,
        }

    def compile_query_script(self, script: str) -> str:
        code_ast = ast.parse(script)
        if code_ast.body:
            last_expr = code_ast.body[-1]
            if isinstance(last_expr, Expr):
                new_expressions = [
                    Import(names=[alias(name="dql.query.dataset", asname=None)]),
                    Expr(
                        value=Call(
                            func=Attribute(
                                value=Attribute(
                                    value=Attribute(
                                        value=Name(id="dql", ctx=Load()),
                                        attr="query",
                                        ctx=Load(),
                                    ),
                                    attr="dataset",
                                    ctx=Load(),
                                ),
                                attr="return_ds",
                                ctx=Load(),
                            ),
                            args=[last_expr],
                            keywords=[],
                        )
                    ),
                ]
                code_ast.body[-1:] = new_expressions
            else:
                raise Exception("Last line in a script was not an expression")

        return ast.unparse(code_ast)

    def add_storage(self, source: str, symlinks: bool = False) -> None:
        # pylint:disable-next=protected-access
        path = LocalFileSystem._strip_protocol(source)
        if not os.path.isdir(path):
            raise RuntimeError(f"{path} is not a directory")
        uri = Path(path).resolve().as_uri()
        print(f"Registering storage {uri}")
        self.data_storage.create_storage_if_not_registered(uri, symlinks)

    def parse_url(self, uri: str, **config: Any) -> Tuple[Client, str]:
        config = config or self.client_config or {}
        return Client.parse_url(uri, self.data_storage, self.cache, **config)

    def enlist_source(
        self,
        source: str,
        ttl: int,
        force_update=False,
        skip_indexing=False,
        client_config=None,
        index_processors: Optional[List[IndexingFormat]] = None,
    ) -> Tuple[Listing, str]:
        if force_update and skip_indexing:
            raise ValueError(
                "Both force_update and skip_indexing flags"
                " cannot be True at the same time"
            )

        client_config = client_config or self.client_config or {}
        client, path = self.parse_url(source, **client_config)
        prefix = posixpath.dirname(path)
        source_data_storage = self.data_storage.clone(uri=client.uri)

        if skip_indexing:
            source_data_storage.create_storage_if_not_registered(client.uri)
            storage = source_data_storage.get_storage(client.uri)
            return (
                Listing(storage, source_data_storage, client),
                path,
            )

        (
            storage,
            need_index,
            in_progress,
            is_new,
        ) = source_data_storage.register_storage_for_indexing(
            client.uri, force_update, prefix
        )
        if in_progress:
            raise PendingIndexingError(f"Pending indexing operation: uri={storage.uri}")

        lst = Listing(storage, source_data_storage, client)

        if not need_index:
            logger.debug(  # type: ignore[unreachable]
                f"Using cached listing {storage.uri}."
                + f" Valid till: {storage.expires_to_local}"
            )
            # Listing has to have correct version of data storage
            # initialized with correct Storage
            return lst, path

        try:
            source_data_storage.init_db(prefix, is_new)
            partial_id = source_data_storage.get_next_partial_id(prefix)
            lst.fetch(prefix, partial_id)

            # Apply index processing before marking storage as indexed.
            if index_processors:
                asyncio.run(apply_processors(lst, path, index_processors))

                # We need to validate paths to eliminate duplicate entries
                # after applying index_processor, which may create
                # subobjects, so we're always working with valid entries
                source_data_storage.validate_paths()

            source_data_storage.mark_storage_indexed(
                storage.uri,
                Status.PARTIAL if prefix else Status.COMPLETE,
                ttl,
                prefix=prefix,
                partial_id=partial_id,
            )
        except InconsistentSignalType as e:
            # handle all custom errors here which messages we want to show
            # directly to the user (user mistake generated error)
            source_data_storage.mark_storage_indexed(
                storage.uri,
                Status.FAILED,
                ttl,
                prefix=prefix,
                error_message=str(e),
                error_stack=traceback.format_exc(),
            )
            raise
        except ClientError as e:
            # for handling cloud errors
            error_message = INDEX_INTERNAL_ERROR_MESSAGE
            if e.error_code in ["InvalidAccessKeyId", "SignatureDoesNotMatch"]:
                error_message = "Invalid cloud credentials"

            source_data_storage.mark_storage_indexed(
                storage.uri,
                Status.FAILED,
                ttl,
                prefix=prefix,
                error_message=error_message,
                error_stack=traceback.format_exc(),
            )
            raise
        except:  # noqa: E722,B001
            source_data_storage.mark_storage_indexed(
                storage.uri,
                Status.FAILED,
                ttl,
                prefix=prefix,
                error_message=INDEX_INTERNAL_ERROR_MESSAGE,
                error_stack=traceback.format_exc(),
            )
            raise

        lst.storage = storage

        return lst, path

    def enlist_sources(
        self,
        sources: List[str],
        ttl: int,
        update: bool,
        skip_indexing=False,
        client_config=None,
        index_processors: Optional[List[IndexingFormat]] = None,
        only_index=False,
    ) -> Optional[List["DataSource"]]:
        enlisted_sources = []
        for src in sources:  # Opt: parallel
            listing, file_path = self.enlist_source(
                src,
                ttl,
                update,
                skip_indexing=skip_indexing,
                client_config=client_config or self.client_config,
                index_processors=index_processors,
            )
            enlisted_sources.append((listing, file_path))

        if only_index:
            # sometimes we don't really need listing result (e.g on indexing process)
            # so this is to improve performance
            return None

        dsrc_all = []
        for listing, file_path in enlisted_sources:
            nodes = listing.expand_path(file_path)
            dir_only = file_path.endswith("/")
            for node in nodes:
                dsrc_all.append(DataSource(listing, node, dir_only))

        return dsrc_all

    def enlist_sources_grouped(
        self,
        sources: List[str],
        ttl: int,
        update: bool,
        no_glob: bool = False,
        client_config=None,
    ) -> List[NodeGroup]:
        def _ds_row_to_node(dr: DatasetRow) -> Node:
            d = asdict(dr)  # type: ignore [arg-type]
            del d["source"]
            del d["custom"]
            return Node(**d)

        enlisted_sources: List[Tuple[bool, bool, Any]] = []
        client_config = client_config or self.client_config or {}
        for src in sources:  # Opt: parallel
            if src.endswith(DATASET_FILE_SUFFIX) and os.path.isfile(src):
                # TODO: Also allow using EDQL files from cloud locations?
                edql_data = parse_edql_file(src)
                indexed_sources = []
                for ds in edql_data:
                    listing, source_path = self.enlist_source(
                        ds["data-source"]["uri"],
                        ttl,
                        update,
                        client_config=client_config,
                    )
                    paths = dql_paths_join(
                        source_path, (f["name"] for f in ds["files"])
                    )
                    indexed_sources.append((listing, source_path, paths))
                enlisted_sources.append((True, False, indexed_sources))
            elif src.startswith("ds://"):
                ds_name, ds_version = parse_dataset_uri(src)
                dataset_sources = self.data_storage.get_dataset_sources(
                    ds_name, ds_version
                )
                indexed_sources = []
                for source in dataset_sources:
                    client, _ = self.parse_url(source, **client_config)
                    listing = Listing(
                        None,  # type: ignore [arg-type]
                        self.data_storage.clone(uri=client.uri),
                        client,
                    )
                    rows = self.data_storage.get_dataset_rows(
                        ds_name, version=ds_version, limit=None, source=source
                    )
                    indexed_sources.append(
                        (
                            listing,
                            source,
                            rows,
                            ds_name,
                            ds_version,
                        )  # type: ignore [arg-type]
                    )

                enlisted_sources.append((False, True, indexed_sources))
            else:
                listing, source_path = self.enlist_source(
                    src, ttl, update, client_config=client_config
                )
                enlisted_sources.append((False, False, (listing, source_path)))

        node_groups = []
        dsrc: List[DataSource] = []
        for is_dql, is_dataset, payload in enlisted_sources:  # Opt: parallel
            if is_dataset:
                for (
                    listing,
                    source_path,
                    dataset_rows,
                    dataset_name,
                    dataset_version,
                ) in payload:
                    nodes = [_ds_row_to_node(row) for row in dataset_rows]
                    dsrc = [DataSource(listing, node) for node in nodes]
                    node_groups.append(
                        NodeGroup(
                            listing,
                            dsrc,
                            source_path,
                            dataset_name=dataset_name,
                            dataset_version=dataset_version,
                        )
                    )
            elif is_dql:
                for listing, source_path, paths in payload:
                    dsrc = [DataSource(listing, listing.resolve_path(p)) for p in paths]
                    node_groups.append(
                        NodeGroup(listing, dsrc, source_path, is_edql=True)
                    )
            else:
                listing, source_path = payload
                as_container = source_path.endswith("/")
                if no_glob:
                    dsrc = [
                        DataSource(
                            listing, listing.resolve_path(source_path), as_container
                        )
                    ]
                else:
                    dsrc = [
                        DataSource(listing, n, as_container)
                        for n in listing.expand_path(source_path)
                    ]
                node_groups.append(NodeGroup(listing, dsrc, source_path))

        return node_groups

    def _get_nodes(self, sources: Iterable[str], client_config):
        "Gets list of nodes based on sources"
        nodes = []
        for source in sources:
            client, _ = self.parse_url(source, **client_config)
            nodes.append(self.data_storage.nodes_table(client.uri))

        return nodes

    def create_shadow_dataset(
        self,
        name: str,
        sources: List[str],
        query_script: str = "",
        client_config=None,
        recursive=False,
        populate=True,
    ) -> DatasetRecord:
        """
        Creates shadow dataset in DB if it doesn't exist and updates it with
        entries from sources.
        Example of sources:
            s3://bucket_name/dir1/dir2/*
            s3://bucket_name/*
            s3://bucket_name/image_*
        """
        error_message = ""
        error_stack = ""
        client_config = client_config or self.client_config or {}

        # get custom columns based on sources
        custom_columns = DatasetRowSchema.calculate_custom_columns(
            self._get_nodes(sources, client_config)
        )
        dataset = self.data_storage.create_shadow_dataset(
            name,
            sources=sources,
            query_script=query_script,
            create_rows=populate,
            custom_columns=custom_columns,
        )
        assert dataset
        if not populate:
            # returning empty dataset without dataset rows table and data inside
            return dataset

        final_status = DatasetStatus.FAILED
        try:
            for source in sources:
                client, path = self.parse_url(source, **client_config)
                self.data_storage.insert_into_shadow_dataset(
                    name, client.uri, path, recursive=recursive
                )
            final_status = DatasetStatus.COMPLETE
        except Exception:
            error_message = DATASET_INTERNAL_ERROR_MESSAGE
            error_stack = traceback.format_exc()
            raise
        finally:
            self.data_storage.update_dataset_status(
                dataset,
                final_status,
                error_message=error_message,
                error_stack=error_stack,
            )

        return dataset

    def register_shadow_dataset(
        self,
        shadow_name: str,
        registered_name: Optional[str] = None,
        version: Optional[int] = None,
        description: Optional[str] = None,
        labels: Optional[List[str]] = None,
        validate_version: Optional[bool] = True,
    ):
        """
        Method for registering shadow dataset as a new dataset with version 1, or
        as a new version of existing registered dataset
        """
        version = version or 1

        # getting shadow dataset
        shadow_dataset = self.data_storage.get_dataset(shadow_name)

        if not shadow_dataset.shadow:
            raise ValueError(f"Dataset {shadow_name} must be shadow")

        try:
            registered_dataset = (
                self.data_storage.get_dataset(registered_name)
                if registered_name
                else None
            )
        except DatasetNotFoundError:
            registered_dataset = None

        if registered_dataset:
            # if registered dataset already exists, we are creating new version
            # of it out of shadow dataset
            version = version or registered_dataset.next_version
            if validate_version and not registered_dataset.is_valid_next_version(
                version
            ):
                raise ValueError(
                    f"Version {version} must be higher than the current latest one"
                )

            self.data_storage.create_dataset_version(
                registered_dataset.name,
                version,
                sources=shadow_dataset.sources,
                query_script=shadow_dataset.query_script,
                create_rows_table=False,
            )
            # to avoid re-creating rows table, we are just taking shadow one and
            # renaming it for a new version of registered one
            self.data_storage.rename_dataset_table(
                shadow_dataset.name,
                registered_dataset.name,
                old_version=None,
                new_version=version,
            )
            # finally, we are removing shadow dataset from datasets table
            self.data_storage.remove_shadow_dataset(shadow_dataset, drop_rows=False)
            return

        # if registered dataset doesn't exist we are modifying shadow dataset
        # to become registered one
        update_data = {
            "shadow": False,
            "description": description,
            "labels": labels,
            "sources": "",
            "query_script": "",
        }

        if registered_name:
            update_data["name"] = registered_name

        self.data_storage.update_dataset(shadow_name, **update_data)
        self.data_storage.create_dataset_version(
            registered_name or shadow_name,
            version,
            sources=shadow_dataset.sources,
            query_script=shadow_dataset.query_script,
            create_rows_table=False,
        )
        self.data_storage.rename_dataset_table(
            registered_name or shadow_name,
            registered_name or shadow_name,
            old_version=None,
            new_version=version,
        )

    def get_dataset(self, name: str) -> DatasetRecord:
        return self.data_storage.get_dataset(name)

    def ls_datasets(self, shadow_only=None) -> Iterator[DatasetRecord]:
        yield from self.data_storage.list_datasets(shadow_only=shadow_only)

    def ls_dataset_rows(
        self, name: str, limit=None, version=None, custom_columns=False
    ) -> Iterator[DatasetRow]:
        dataset = self.data_storage.get_dataset(name)
        if not dataset.shadow and not version:
            raise ValueError(
                f"Missing dataset version from input for registered dataset {name}"
            )

        yield from self.data_storage.get_dataset_rows(
            name, limit=limit, version=version, custom_columns=custom_columns
        )

    def signed_url(self, source: str, path: str, client_config=None) -> str:
        client_config = client_config or {}
        client, _ = self.parse_url(source, **client_config)
        return client.url(path)

    def dataset_row(
        self,
        name: str,
        row_id: int,
        dataset_version: Optional[int] = None,
    ) -> Optional[DatasetRow]:
        return self.data_storage.get_dataset_row(
            name, row_id, dataset_version=dataset_version
        )

    def dataset_stats(self, name: str, version: Optional[int] = None) -> DatasetStats:
        dataset = self.data_storage.get_dataset(name)
        if dataset.registered and not version:
            raise ValueError(f"Missing dataset version for registered dataset {name}")
        return DatasetStats(
            num_objects=self.data_storage.dataset_rows_count(name, version),
            size=self.data_storage.dataset_rows_size(name, version),
        )

    def dataset_meta(self, name: str, version: Optional[int] = None) -> DatasetMeta:
        dataset = self.data_storage.get_dataset(name)
        if dataset.registered and not version:
            raise ValueError(f"Missing dataset version for registered dataset {name}")

        return DatasetMeta(
            custom_column_types=self.data_storage.dataset_column_types(
                name, version=version, custom=True
            ),
        )

    def remove_dataset(
        self,
        name: str,
        version: Optional[int] = None,
        force: Optional[bool] = False,
    ):
        dataset = self.data_storage.get_dataset(name)
        if dataset.registered and not version and not force:
            raise ValueError(
                f"Missing dataset version from input for registered dataset {name}"
            )
        if version and not dataset.has_version(version):
            raise RuntimeError(f"Dataset {name} doesn't have version {version}")

        if dataset.registered and version:
            # removing one version of registered dataset
            self.data_storage.remove_dataset_version(dataset, version)

        elif dataset.registered and force:
            for version in dataset.versions.copy():  # type: ignore [assignment, union-attr] # noqa: E501
                self.data_storage.remove_dataset_version(
                    dataset, version.version  # type: ignore [union-attr]
                )
        else:
            self.data_storage.remove_shadow_dataset(dataset)

    def edit_dataset(
        self,
        name: str,
        new_name: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ):
        update_data = {}
        if new_name:
            update_data["name"] = new_name
        if description is not None:
            update_data["description"] = description
        if labels is not None:
            update_data["labels"] = labels  # type: ignore[assignment]

        self.data_storage.update_dataset(name, **update_data)

    def merge_datasets(
        self,
        src_name: str,
        dst_name: str,
        src_version: Optional[int] = None,
        dst_version: Optional[int] = None,
    ) -> DatasetRecord:
        """
        Merges records from source to destination dataset.
        If destination dataset is shadow, it will copy all the records from source
        dataset to shadow one
        If destination dataset is registered, it will create a new version
        of dataset with records merged from old version and the source
        """

        src = self.data_storage.get_dataset(src_name)
        dst = self.data_storage.get_dataset(dst_name)

        # validation
        if src.shadow and src_version:
            raise ValueError(
                f"Source dataset {src_name} is shadow, cannot use it with versions"
            )
        if not src.shadow and not src_version:
            raise ValueError(f"Source dataset {src_name} is registered, need a version")
        if dst.shadow and dst_version:
            raise ValueError(
                f"Dataset {dst_name} is shadow, cannot use it with versions"
            )

        if dst_version and not dst.is_valid_next_version(dst_version):
            raise ValueError(
                f"Version {dst_version} must be higher than the current latest one"
            )

        if dst.shadow:
            self.data_storage.merge_dataset_rows(
                src,
                dst,
                src_version,
                dst_version=None,
            )
        else:
            dst_version = dst_version or dst.next_version
            dst = self.data_storage.create_dataset_version(dst_name, dst_version)
            self.data_storage.merge_dataset_rows(
                src,
                dst,
                src_version,
                dst_version,
            )

        return dst

    def copy_shadow_dataset(self, src_name: str, dst_name: str) -> DatasetRecord:
        """
        Copy records from source shadow dataset to destination shadow dataset.
        """
        src = self.data_storage.get_dataset(src_name)
        dst = self.data_storage.get_dataset(dst_name)

        # validation
        if not src.shadow:
            raise ValueError(f"Source dataset {src_name} is not shadow")
        if not dst.shadow:
            raise ValueError(f"Dataset {dst_name} is not shadow")

        self.data_storage.copy_shadow_dataset_rows(src, dst)

        return dst

    def open_object(self, row: DatasetRow, use_cache: bool = True, **config: Any):
        config = config or self.client_config or {}
        client, _ = self.parse_url(row.source, **config)
        return client.open_object(row.as_uid(), use_cache=use_cache)

    def ls(
        self,
        sources: List[str],
        fields: Iterable[str],
        ttl=TTL_INT,
        update=False,
        skip_indexing=False,
        *,
        client_config=None,
    ) -> Iterator[Tuple[DataSource, Iterable[tuple]]]:
        data_sources = self.enlist_sources(
            sources,
            ttl,
            update,
            skip_indexing=skip_indexing,
            client_config=client_config or self.client_config,
        )

        for source in data_sources:  # type: ignore [union-attr]
            yield source, source.ls(fields)

    def ls_storage_uris(self) -> Iterator[str]:
        yield from self.data_storage.get_all_storage_uris()

    def get_storage(self, uri: str) -> Storage:
        return self.data_storage.get_storage(uri)

    def ls_storages(self) -> List[Storage]:
        return self.data_storage.list_storages()

    def pull_dataset(  # noqa: C901
        self,
        dataset_uri: str,
        output: str = None,
        no_cp: bool = False,
        force: bool = False,
        edql: bool = False,
        edql_file: Optional[str] = None,
        *,
        client_config=None,
    ) -> None:
        # TODO add progress bar https://github.com/iterative/dql/issues/750
        # TODO copy correct remote dates https://github.com/iterative/dql/issues/new
        # TODO compare dataset stats on remote vs local pull to assert it's ok
        def _instantiate_dataset():
            if no_cp:
                return
            self.cp(
                [dataset_uri],
                output,
                force=force,
                no_edql_file=not edql,
                edql_file=edql_file,
                client_config=client_config,
            )
            print(f"Dataset {dataset_uri} instantiated locally to {output}")

        def _print_remote_error(error_message: str):
            print(f"Error from server: {error_message}")

        if not output and not no_cp:
            raise ValueError("Please provide output directory for instantiation")

        client_config = client_config or self.client_config or {}
        remote_config = get_remote_config(read_config(DQLDir.find().root), remote="")

        studio_client = StudioClient(
            remote_config["url"], remote_config["username"], remote_config["token"]
        )

        try:
            remote_dataset_name, version = parse_dataset_uri(dataset_uri)
        except Exception as e:  # pylint: disable=W0703
            print("Error when parsing dataset uri:", e)
            return

        dataset = None
        try:
            dataset = self.get_dataset(remote_dataset_name)
            if dataset.shadow:
                print(
                    "Shadow local dataset already exists with name "
                    f"{remote_dataset_name}"
                )
                return
        except DatasetNotFoundError:
            pass

        # TODO maybe convert dataset_info into DatasetRecord - we would need to
        # add DatasetMeta to DatasetVersion as optional field as well
        info_response = studio_client.dataset_info(remote_dataset_name)
        if not info_response.ok:
            _print_remote_error(info_response.message)
            return
        dataset_info = info_response.data

        # if version is not specified in uri, take the latest one
        if not version:
            version = max(
                int(v["version"])
                for v in dataset_info["versions"]  # type: ignore [index]
            )
            print(f"Version not specified, pulling the latest one (v{version})")
            # updating dataset uri with latest version
            dataset_uri = create_dataset_uri(remote_dataset_name, version)

        if dataset and dataset.has_version(version):
            print(f"Local copy of dataset {dataset_uri} already present")
            _instantiate_dataset()
            return

        version_info = next(
            (
                v
                for v in dataset_info["versions"]  # type: ignore [index]
                if v["version"] == version
            ),
            None,
        )
        if not version_info:
            print(
                f"Dataset {remote_dataset_name} doesn't have version {version}"
                " on server"
            )
            return

        stats_response = studio_client.dataset_stats(remote_dataset_name, version)
        if not stats_response.ok:
            _print_remote_error(stats_response.message)
            return
        dataset_stats = stats_response.data

        dataset_save_progress_bar = tqdm(
            desc=f"Saving dataset {dataset_uri} locally: ",
            unit=" rows",
            unit_scale=True,
            unit_divisor=1000,
            total=dataset_stats.num_objects,  # type: ignore [union-attr]
        )

        # temp shadow dataset name not to conflict to possibly already existing
        # registered one with the same name - if some other version of it
        # has been pulled from remote before
        shadow_dataset_name = f"shadow_ds_{uuid4().hex}"

        shadow_dataset = self.data_storage.create_shadow_dataset(
            shadow_dataset_name,
            sources=version_info["sources"].split(),
            query_script=version_info["query_script"],
            create_rows=True,
            custom_columns=parse_columns(version_info["meta"]["custom_column_types"]),
        )

        for rows_response in studio_client.dataset_rows(remote_dataset_name, version):
            if not rows_response.ok:
                _print_remote_error(rows_response.message)
                self.remove_dataset(shadow_dataset.name)  # cleaning up
                return
            dataset_save_progress_bar.update(
                len(rows_response.data)  # type: ignore [arg-type]
            )
            self.data_storage.insert_dataset_rows(
                shadow_dataset.name, rows_response.data
            )

        shadow_dataset = self.data_storage.update_dataset_status(
            shadow_dataset,
            DatasetStatus.COMPLETE,
            error_message=dataset_info["error_message"],  # type: ignore [index]
            error_stack=dataset_info["error_stack"],  # type: ignore [index]
            script_output=dataset_info["script_output"],  # type: ignore [index]
        )

        self.register_shadow_dataset(
            shadow_dataset.name,
            registered_name=remote_dataset_name,
            version=version,
            description=dataset_info["description"],  # type: ignore [index]
            labels=dataset_info["labels"],  # type: ignore [index]
            validate_version=False,
        )
        dataset_save_progress_bar.close()
        print(f"Dataset {dataset_uri} saved locally")

        _instantiate_dataset()

    def clone(
        self,
        sources: List[str],
        output: str,
        force: bool = False,
        update: bool = False,
        recursive: bool = False,
        no_glob: bool = False,
        no_cp: bool = False,
        edql: bool = False,
        edql_file: Optional[str] = None,
        ttl: int = TTL_INT,
        *,
        client_config=None,
    ) -> None:
        """
        This command takes cloud path(s) and duplicates files and folders in
        them into the dataset folder.
        It also adds those files to a shadow dataset in database, which is
        created if doesn't exist yet
        Optionally, it creates a .edql file
        """
        if not no_cp or edql:
            self.cp(
                sources,
                output,
                force=force,
                update=update,
                recursive=recursive,
                no_glob=no_glob,
                edql_only=no_cp,
                no_edql_file=not edql,
                edql_file=edql_file,
                ttl=ttl,
                client_config=client_config,
            )
        else:
            # since we don't call cp command, which does listing implicitly,
            # it needs to be done here
            self.enlist_sources(
                sources,
                ttl,
                update,
                client_config=client_config or self.client_config,
            )

        self.create_shadow_dataset(
            output, sources, client_config=client_config, recursive=recursive
        )

    def apply_udf(
        self,
        udf_location: str,
        source: str,
        target_name: str,
        processes: Union[bool, int] = False,
        params: Optional[str] = None,
    ):
        from dql.query import DatasetQuery

        if source.startswith(DATASET_PREFIX):
            ds = DatasetQuery(name=source[len(DATASET_PREFIX) :], catalog=self)
        else:
            ds = DatasetQuery(path=source, catalog=self)
        udf = import_object(udf_location)
        if params:
            args, kwargs = parse_params_string(params)
            udf = udf(*args, **kwargs)
        ds.add_signals(udf, processes=processes).save(target_name)

    def query(  # noqa: C901
        self,
        query_script: str,
        envs: Optional[Dict[str, str]] = None,
        dataset: Optional[DatasetRecord] = None,
        python_executable: Optional[str] = None,
    ) -> DatasetRecord:
        """
        Method to run custom user Python script to run a query and, as result,
        creates new shadow dataset from the results of a query
        Constraints on query script:
            1. dql.query.DatasetQuery should be used in order to create query
            for a dataset
            2. There should not be any .save() call on DatasetQuery since the idea
            is to create only one shadow dataset as the outcome of the script
            3. Last statement must be an instance of DatasetQuery - this is needed
            so that we can wrap that instance and call .save() on it

        Example of query script:
            from dql.query import DatasetQuery, C
            DatasetQuery('s3://ldb-public/remote/datasets/mnist-tiny/').filter(
                C.size > 1000
            )
        """
        if dataset:
            # save query script regardless of query run outcome
            self.data_storage.update_dataset(dataset.name, query_script=query_script)
        try:
            query_script_compiled = self.compile_query_script(query_script)
        except Exception as e:
            err = f"Query script failed to compile, reason: {e}"
            if dataset:
                self.data_storage.update_dataset_status(
                    dataset,
                    DatasetStatus.FAILED,
                    error_message=err,
                    error_stack=traceback.format_exc(),
                )
            raise QueryScriptCompileError(err)

        if not python_executable:
            python_executable = sys.executable
        script_output = ""  # stdout + stderr from user script itself

        try:
            # pylint: disable=W1510
            result = subprocess.run(  # nosec B603
                [python_executable, "-c", query_script_compiled],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # merging stderr to stdout
                env=envs or {},
            )

            if result.returncode:
                if result.stdout:
                    script_output = result.stdout.decode("utf-8")
                if result.returncode == QUERY_SCRIPT_INVALID_LAST_STATEMENT_EXIT_CODE:
                    raise QueryScriptRunError(
                        "Last line in a script was not an instance of DatasetQuery"
                    )
                else:
                    raise QueryScriptRunError(
                        f"Query script exited with error code {result.returncode}"
                    )
                raise QueryScriptRunError(err)

            # finding returning dataset name from script
            returned_dataset = None
            if result.stdout:
                for line in result.stdout.decode("utf-8").splitlines():
                    if len(line.split(PYTHON_SCRIPT_WRAPPER_CODE)) == 3:
                        returned_dataset_name = line.split(PYTHON_SCRIPT_WRAPPER_CODE)[
                            1
                        ]
                        returned_dataset = self.get_dataset(returned_dataset_name)
                    else:
                        # collecting script output as well to save it to the database
                        # later on for debugging
                        script_output += line + "\n"

            if not returned_dataset:
                raise QueryScriptDatasetNotFound(
                    "No dataset found after running Query script"
                )

            if dataset:
                dataset = self.merge_datasets(returned_dataset.name, dataset.name)
                self.remove_dataset(returned_dataset.name)
                self.data_storage.update_dataset_status(
                    dataset, DatasetStatus.COMPLETE, script_output=script_output
                )
                return dataset
            else:
                self.data_storage.update_dataset(
                    returned_dataset_name,
                    sources="",
                    query_script=query_script,
                )
                return self.get_dataset(returned_dataset_name)
        except QueryScriptRunError as e:
            if dataset:
                self.data_storage.update_dataset_status(
                    dataset,
                    DatasetStatus.FAILED,
                    error_message=str(e),
                    error_stack=traceback.format_exc(),
                    script_output=script_output,
                )
            raise
        except (Exception, QueryScriptDatasetNotFound):
            if dataset:
                self.data_storage.update_dataset_status(
                    dataset,
                    DatasetStatus.FAILED,
                    error_message=DATASET_INTERNAL_ERROR_MESSAGE,
                    error_stack=traceback.format_exc(),
                    script_output=script_output,
                )
            raise

    def cp(
        self,
        sources: List[str],
        output: str,
        force: bool = False,
        update: bool = False,
        recursive: bool = False,
        edql_file: Optional[str] = None,
        edql_only: bool = False,
        no_edql_file: bool = False,
        no_glob: bool = False,
        ttl: int = TTL_INT,
        *,
        client_config=None,
    ) -> List[Dict[str, Any]]:
        """
        This function copies files from cloud sources to local destination directory
        If cloud source is not indexed, or has expired index, it runs indexing
        It also creates .edql file by default, if not specified differently
        """
        client_config = client_config or self.client_config or {}
        node_groups = self.enlist_sources_grouped(
            sources,
            ttl,
            update,
            no_glob,
            client_config=client_config,
        )

        always_copy_dir_contents, copy_to_filename = prepare_output_for_cp(
            node_groups, output, force, edql_only, no_edql_file
        )

        dataset_file = check_output_dataset_file(
            output, force, edql_file, True, no_edql_file
        )

        total_size, total_files = collect_nodes_for_cp(node_groups, recursive)

        if total_files == 0:
            # Nothing selected to cp
            return []

        desc_max_len = max(len(output) + 16, 19)
        bar_format = (
            "{desc:<"
            f"{desc_max_len}"
            "}{percentage:3.0f}%|{bar}| {n_fmt:>5}/{total_fmt:<5} "
            "[{elapsed}<{remaining}, {rate_fmt:>8}]"
        )

        if not edql_only:
            download_node_groups(node_groups, bar_format, total_size, recursive)

        metafile_data = instantiate_node_groups(
            node_groups,
            output,
            bar_format,
            total_files,
            force,
            recursive,
            edql_only,
            always_copy_dir_contents,
            copy_to_filename,
        )

        if not metafile_data or no_edql_file:
            # Don't write the metafile if nothing was copied (or skipped)
            return metafile_data

        print(f"Creating '{dataset_file}'")
        with open(dataset_file, "w", encoding="utf-8") as fd:
            yaml.dump(metafile_data, fd, sort_keys=False)

        return metafile_data

    def du(
        self,
        sources,
        depth=0,
        ttl=TTL_INT,
        update=False,
        *,
        client_config=None,
    ) -> Iterable[Tuple[str, float]]:
        sources = self.enlist_sources(
            sources,
            ttl,
            update,
            client_config=client_config or self.client_config,
        )

        def du_dirs(src, node, subdepth):
            if subdepth > 0:
                subdirs = src.listing.data_storage.get_nodes_by_parent_id(
                    node.id, type="dir"
                )
                for sd in subdirs:
                    yield from du_dirs(src, sd, subdepth - 1)
            yield (
                src.get_node_full_path(node),
                src.listing.du(node)[0],
            )

        for src in sources:
            yield from du_dirs(src, src.node, depth)

    def find(
        self,
        sources,
        ttl=TTL_INT,
        update=False,
        names=None,
        inames=None,
        paths=None,
        ipaths=None,
        size=None,
        typ=None,
        columns=None,
        *,
        client_config=None,
    ) -> Iterator[str]:
        sources = self.enlist_sources(
            sources,
            ttl,
            update,
            client_config=client_config or self.client_config,
        )
        if not columns:
            columns = ["path"]
        field_set = set()
        for column in columns:
            if column == "du":
                field_set.add("dir_type")
                field_set.add("size")
                field_set.add("parent")
                field_set.add("name")
            elif column == "name":
                field_set.add("name")
            elif column == "owner":
                field_set.add("owner_name")
            elif column == "path":
                field_set.add("dir_type")
                field_set.add("parent")
                field_set.add("name")
            elif column == "size":
                field_set.add("size")
            elif column == "type":
                field_set.add("dir_type")
        fields = list(field_set)
        field_lookup = {f: i for i, f in enumerate(fields)}
        for src in sources:
            results = src.listing.find(
                src.node, fields, names, inames, paths, ipaths, size, typ
            )
            for row in results:
                yield "\t".join(
                    find_column_to_str(row, field_lookup, src, column)
                    for column in columns
                )

    def index(
        self,
        sources,
        ttl=TTL_INT,
        update=False,
        *,
        client_config=None,
        index_processors: Optional[Union[List[IndexingFormat], IndexingFormat]] = None,
    ) -> None:
        root_sources = [
            src for src in sources if Client.get_implementation(src).is_root_url(src)
        ]
        non_root_sources = [
            src
            for src in sources
            if not Client.get_implementation(src).is_root_url(src)
        ]

        client_config = client_config or self.client_config or {}

        # for root sources (e.g s3://) we are just getting all buckets and
        # saving them as storages, without further indexing in each bucket
        for source in root_sources:
            for bucket in Client.get_implementation(source).ls_buckets(**client_config):
                client, _ = self.parse_url(bucket.uri, **client_config)
                print(f"Registering storage {client.uri}")
                self.data_storage.create_storage_if_not_registered(client.uri)

        if index_processors and not isinstance(index_processors, list):
            processors = [index_processors]
        else:
            processors = index_processors  # type: ignore
        sources = self.enlist_sources(
            non_root_sources,
            ttl,
            update,
            client_config=client_config,
            index_processors=processors,
            only_index=True,
        )

    def find_stale_storages(self) -> None:
        self.data_storage.find_stale_storages()
