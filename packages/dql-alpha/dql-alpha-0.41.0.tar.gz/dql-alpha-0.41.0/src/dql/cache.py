import hashlib
import os
import sys
from functools import partial
from typing import Optional

import attrs
from dvc_data.hashfile.build import _upload_file
from dvc_data.hashfile.db.local import LocalHashFileDB
from dvc_objects.fs.local import LocalFileSystem

if sys.version_info < (3, 9):
    md5 = hashlib.md5
else:
    md5 = partial(hashlib.md5, usedforsecurity=False)

BUFSIZE = 2**18


def file_digest(fileobj):
    """Calculate the digest of a file-like object."""
    buf = bytearray(BUFSIZE)  # Reusable buffer to reduce allocations.
    view = memoryview(buf)
    digestobj = md5()
    # From 3.11's hashlib.filedigest()
    while True:
        size = fileobj.readinto(buf)
        if size == 0:
            break  # EOF
        digestobj.update(view[:size])
    return digestobj.hexdigest()


@attrs.frozen
class UniqueId:
    storage: str
    parent: str
    name: str
    vtype: str
    location: Optional[str]

    @property
    def path(self) -> str:
        return f"{self.parent}/{self.name}" if self.parent else self.name


class DQLCache:
    def __init__(self, cache_dir: str, tmp_dir: str, data_storage):
        self.cache = LocalHashFileDB(
            LocalFileSystem(),
            cache_dir,
            tmp_dir=tmp_dir,
        )
        self.data_storage = data_storage

    def get_checksum(self, uid: UniqueId) -> Optional[str]:
        return self.data_storage.cache_get(uid)

    def get_path(self, uid: UniqueId) -> Optional[str]:
        if checksum := self.get_checksum(uid):
            return self.path_from_checksum(checksum)
        return None

    def set_checksum(self, uid: UniqueId, checksum: str) -> None:
        self.data_storage.cache_set(uid, checksum)

    def exists(self, checksum: str) -> bool:
        return self.cache.exists(checksum)

    def contains(self, uid: UniqueId) -> bool:
        if checksum := self.get_checksum(uid):
            return self.cache.exists(checksum)
        return False

    def path_from_checksum(self, checksum: str) -> str:
        assert checksum
        return self.cache.oid_to_path(checksum)

    def download(self, uid: UniqueId, fs, callback=None) -> str:
        _, obj = _upload_file(
            f"{uid.storage}/{uid.path}", fs, self.cache, self.cache, callback=callback
        )
        checksum = obj.hash_info.value
        assert checksum is not None
        return checksum

    def store_data(self, contents: bytes, callback=None) -> str:
        checksum = md5(contents).hexdigest()
        dst = self.path_from_checksum(checksum)
        if not os.path.exists(dst):
            # Create the file only if it's not already in cache
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, mode="wb") as f:
                f.write(contents)
        if callback:
            callback.relative_update(len(contents))
        return checksum

    def clear(self):
        """
        Completely clear the cache.
        """
        self.data_storage.cache_clear()
        self.cache.clear()
