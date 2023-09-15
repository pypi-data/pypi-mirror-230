import asyncio
import json
import logging
import multiprocessing
import os
import posixpath
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime, timezone
from shutil import copy2
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Type,
)

from botocore.exceptions import ClientError
from fsspec.asyn import get_loop
from reflink import reflink
from reflink.error import ReflinkImpossibleError
from tqdm import tqdm

from dql.cache import DQLCache, UniqueId
from dql.client.fileslice import FileSlice
from dql.error import ClientError as DQLClientError
from dql.nodes_fetcher import NodesFetcher
from dql.nodes_thread_pool import NodeChunk

if TYPE_CHECKING:
    from fsspec.spec import AbstractFileSystem

    from dql.data_storage import AbstractDataStorage
    from dql.node import Node

logger = logging.getLogger("dql")

FETCH_WORKERS = 100
DELIMITER = "/"  # Path delimiter.
TIME_ZERO = datetime.fromtimestamp(0, tz=timezone.utc)


class Bucket(NamedTuple):
    name: str
    uri: str
    created: Optional[datetime]


class Client(ABC):
    MAX_THREADS = multiprocessing.cpu_count()
    FS_CLASS: ClassVar[Type["AbstractFileSystem"]]
    PREFIX: ClassVar[str]
    protocol: ClassVar[str]

    def __init__(self, name: str, fs: "AbstractFileSystem", cache: DQLCache) -> None:
        self.name = name
        self.fs = fs
        self.cache = cache

    @staticmethod
    def get_implementation(url: str) -> Type["Client"]:
        from .azure import AzureClient
        from .gcs import GCSClient
        from .local import FileClient
        from .s3 import ClientS3

        if url.lower().startswith(ClientS3.PREFIX):
            return ClientS3
        elif url.lower().startswith(GCSClient.PREFIX):
            return GCSClient
        elif url.lower().startswith(AzureClient.PREFIX):
            return AzureClient
        elif url.lower().startswith(FileClient.PREFIX):
            return FileClient
        raise RuntimeError(f"Unsupported data source format '{url}'")

    @staticmethod
    def parse_url(
        source: str,
        data_storage: "AbstractDataStorage",
        cache: DQLCache,
        **kwargs,
    ) -> Tuple["Client", str]:
        cls = Client.get_implementation(source)
        storage_url, rel_path = cls.split_url(source, data_storage)
        client = cls.from_url(storage_url, data_storage, cache, kwargs)
        return client, rel_path

    @classmethod
    def create_fs(cls, **kwargs) -> "AbstractFileSystem":
        kwargs.setdefault("version_aware", True)
        fs = cls.FS_CLASS(**kwargs)
        fs.invalidate_cache()
        return fs

    @classmethod
    def from_url(  # pylint:disable=unused-argument
        cls,
        url: str,
        data_storage: "AbstractDataStorage",
        cache: DQLCache,
        kwargs: Dict[str, Any],
    ) -> "Client":
        return cls(url, cls.create_fs(**kwargs), cache)

    @classmethod
    def ls_buckets(cls, **kwargs) -> Iterator[Bucket]:
        for entry in cls.create_fs(**kwargs).ls(cls.PREFIX, detail=True):
            name = entry["name"].rstrip("/")
            yield Bucket(
                name=name,
                uri=f"{cls.PREFIX}{name}",
                created=entry.get("CreationDate"),
            )

    @classmethod
    def is_root_url(cls, url) -> bool:
        return url == cls.PREFIX

    @property
    def uri(self) -> str:
        return f"{self.PREFIX}{self.name}"

    @classmethod
    def split_url(  # pylint:disable=unused-argument
        cls, url: str, data_storage: "AbstractDataStorage"
    ) -> Tuple[str, str]:
        fill_path = url[len(cls.PREFIX) :]
        path_split = fill_path.split("/", 1)
        bucket = path_split[0]
        path = path_split[1] if len(path_split) > 1 else ""
        return bucket, path

    @abstractmethod
    def url(self, path: str, expires: int = 3600) -> str:
        ...

    async def fetch(self, listing, start_prefix="", partial_id=0, results=None):
        data_storage = listing.data_storage.clone()
        if start_prefix:
            start_prefix = start_prefix.rstrip("/")
            start_id = await listing.insert_dir(
                None,
                posixpath.basename(start_prefix),
                TIME_ZERO,
                posixpath.dirname(start_prefix),
                partial_id,
                data_storage=data_storage,
            )
        else:
            start_id = await listing.insert_root(data_storage=data_storage)

        progress_bar = tqdm(desc=f"Listing {self.uri}", unit=" objects")
        total_ignore_count = 0
        total_count = 0
        loop = get_loop()

        queue = asyncio.Queue()
        queue.put_nowait((start_id, start_prefix))

        async def worker(queue, data_storage):
            nonlocal total_ignore_count, total_count
            while True:
                dir_id, prefix = await queue.get()
                try:
                    subdirs, ignore_count, found_count = await self._fetch_dir(
                        dir_id,
                        prefix,
                        progress_bar,
                        listing,
                        data_storage,
                        partial_id,
                    )
                    total_ignore_count += ignore_count
                    total_count += found_count
                    for subdir in subdirs:
                        queue.put_nowait(subdir)
                finally:
                    queue.task_done()

        try:
            workers = []
            for _ in range(FETCH_WORKERS):
                workers.append(loop.create_task(worker(queue, data_storage)))

            # Wait for all fetch tasks to complete
            await queue.join()
            # Stop the workers
            for worker in workers:
                worker.cancel()
            await asyncio.gather(*workers)
        except ClientError as exc:
            raise DQLClientError(
                exc.response.get("Error", {}).get("Message") or exc,
                exc.response.get("Error", {}).get("Code"),
            ) from exc
        finally:
            data_storage.inserts_done()
            # This ensures the progress bar is closed before any exceptions are raised
            progress_bar.close()
            if total_ignore_count:
                logger.warning(
                    "File names that collide with directory names will be ignored. "
                    f"Number found: {total_ignore_count}"
                )
            if isinstance(results, dict):
                results["total_ignore_count"] = total_ignore_count
                results["total_count"] = total_count

    async def _fetch_dir(self, dir_id, prefix, pbar, listing, data_storage, partial_id):
        path = f"{self.name}/{prefix}"
        infos = await self.ls_dir(path)
        files = []
        subdirs = set()
        subdir_names = set()
        ignore_count = 0
        for info in infos:
            full_path = info["name"]
            subprefix = self.rel_path(full_path)
            if info["type"] == "directory":
                name = full_path.split(DELIMITER)[-1]
                new_dir_id = await listing.insert_dir(
                    dir_id,
                    name,
                    TIME_ZERO,
                    prefix,
                    partial_id,
                    data_storage=data_storage,
                )
                subdirs.add((new_dir_id, subprefix))
                subdir_names.add(name)
            else:
                files.append(self._dict_from_info(info, dir_id, prefix, partial_id))
        for f in files:
            if not f["name"] or f["name"] in subdir_names:
                # Set files that conflict with directories as not valid
                # Files without a name are of a prefix like "dir/" where the name
                # ends up being empty after the split on "/"
                # And the conflicting files have prefixes like "dir" where there is
                # also an "dir" directory, for example "dir/file1" as well.
                f["valid"] = False
                ignore_count += 1
        if files:
            await data_storage.insert_entries(files)
            await data_storage.update_last_inserted_at()
        found_count = len(subdirs) + len(files)
        pbar.update(found_count)
        return subdirs, ignore_count, found_count

    async def ls_dir(self, path):
        # pylint:disable-next=protected-access
        return await self.fs._ls(path, detail=True, versions=True)

    def rel_path(self, path):
        return self.fs.split_path(path)[1]

    def get_full_path(self, rel_path: str) -> str:
        return f"{self.PREFIX}{self.name}/{rel_path}"

    @abstractmethod
    def _dict_from_info(self, v, parent_id, parent, partial_id):
        ...

    def fetch_nodes(
        self,
        file_path,
        nodes,
        total_size=None,
        cls=NodesFetcher,
        pb_descr="Download",
        shared_progress_bar=None,
    ) -> List["Node"]:
        fetcher = cls(self, self.MAX_THREADS, self.cache)

        chunk_gen = NodeChunk(self.cache, self.uri, nodes)
        target_name = self.visual_file_name(file_path)
        pb_descr = f"{pb_descr} {target_name}"
        return fetcher.run(chunk_gen, pb_descr, total_size, shared_progress_bar)

    def iter_object_chunks(self, bucket, path, version=None):
        with self.fs.open(f"{bucket}/{path}", version_id=version) as f:
            chunk = f.read()
            while chunk:
                yield chunk
                chunk = f.read()

    @staticmethod
    def visual_file_name(file_path):
        target_name = file_path.rstrip("/").split("/")[-1]
        max_len = 25
        if len(target_name) > max_len:
            target_name = "..." + target_name[max_len - 3 :]
        return target_name

    def instantiate_object(
        self,
        uid: UniqueId,
        dst: str,
        progress_bar: tqdm,
        force: bool = False,
    ) -> None:
        if os.path.exists(dst):
            if force:
                os.remove(dst)
            else:
                progress_bar.close()
                raise FileExistsError(f"Path {dst} already exists")
        self.do_instantiate_object(uid, dst)

    def do_instantiate_object(self, uid: "UniqueId", dst: str) -> None:
        src = self.cache.get_path(uid)
        assert src is not None
        try:
            reflink(src, dst)
        except (NotImplementedError, ReflinkImpossibleError):
            # Default to copy if reflinks are not supported
            copy2(src, dst)

    @contextmanager
    def open_object(self, uid: UniqueId, use_cache: bool = True):
        """Open a file, including files in tar archives."""
        if uid.vtype == "tar":
            assert uid.location is not None
            loc_stack = json.loads(uid.location)
            if len(loc_stack) > 1:
                raise NotImplementedError("Nested v-objects are not supported yet.")
            obj_location = loc_stack[0]
            tar_path = posixpath.split(obj_location["parent"])
            offset = obj_location["offset"]
            size = obj_location["size"]
            parent_uid = UniqueId(uid.storage, *tar_path, vtype="", location=None)
            with self.open_object(parent_uid, use_cache=True) as f:
                yield FileSlice(f, offset, size, posixpath.basename(uid.path))
        else:
            if use_cache and (checksum := self.cache.get_checksum(uid)):
                cache_path = self.cache.path_from_checksum(checksum)
                with open(cache_path, mode="rb") as f:
                    yield f
            else:
                with self.open(uid.path) as f:
                    yield f

    def open(self, path: str, mode="rb") -> Any:
        return self.fs.open(self.get_full_path(path), mode=mode)

    def download(self, uid: UniqueId, *, callback=None):
        if checksum := self.cache.get_checksum(uid):
            # Already in cache, so there's nothing to do.
            return checksum
        checksum = self.put_in_cache(uid, callback=callback)
        self.cache.set_checksum(uid, checksum)
        return checksum

    def put_in_cache(self, uid: UniqueId, *, callback=None) -> str:
        if uid.vtype == "tar":
            return self._download_from_tar(uid.location, callback=callback)
        return self.cache.download(uid, self.fs, callback=callback)

    def _download_from_tar(self, location, *, callback=None):
        assert location is not None
        loc_stack = json.loads(location)
        if len(loc_stack) > 1:
            raise NotImplementedError("Nested v-objects are not supported yet.")
        location = loc_stack[0]
        offset = location["offset"]
        tar_path = location["parent"]
        size = location["size"]
        with self.open(tar_path) as f:
            f.seek(offset)
            contents = f.read(size)
        return self.cache.store_data(contents, callback=callback)
