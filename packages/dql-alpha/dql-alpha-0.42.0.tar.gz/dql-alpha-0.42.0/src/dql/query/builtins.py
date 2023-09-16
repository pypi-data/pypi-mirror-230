import hashlib
import json
import sys
import tarfile
from datetime import datetime, timezone
from functools import partial
from random import getrandbits
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from dql.catalog import Catalog
from dql.data_storage.abstract import RANDOM_BITS
from dql.node import DirType
from dql.sql.types import String

from .udf import generator

if TYPE_CHECKING:
    from dql.dataset import DatasetRow


if sys.version_info < (3, 9):
    md5 = hashlib.md5
else:
    md5 = partial(hashlib.md5, usedforsecurity=False)

__all__ = ["index_tar", "checksum"]


def tarmember_from_info(info, parent):
    location = json.dumps(
        [
            {
                "offset": info.offset_data,
                "size": info.size,
                "type": "tar",
                "parent": parent.path,
            },
        ]
    )
    full_path = f"{parent.path}/{info.name}"
    parent_dir, name = full_path.rsplit("/", 1)
    return {
        "vtype": "tar",
        "dir_type": DirType.FILE,
        "parent_id": parent.id,
        "parent": parent_dir,
        "name": name,
        "checksum": "",
        "etag": "",
        "version": "",
        "is_latest": parent.is_latest,
        "last_modified": datetime.fromtimestamp(info.mtime, timezone.utc),
        "size": info.size,
        "owner_name": info.uname,
        "owner_id": str(info.uid),
        "anno": None,
        "source": parent.source,
        "random": getrandbits(RANDOM_BITS),
        "location": location,
    }


@generator(Catalog)
def index_tar(row, catalog):
    with catalog.open_object(row) as f:
        with tarfile.open(fileobj=f, mode="r:") as archive:
            for info in archive:
                if info.isdir():
                    continue
                yield tarmember_from_info(info, parent=row)


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


class ChecksumFunc:
    """Calculate checksums for objects reference by dataset rows."""

    output = (("checksum", String),)

    def __init__(self):
        pass

    def __call__(
        self, catalog: "Catalog", row: "DatasetRow"
    ) -> Optional[List[Dict[str, Any]]]:
        with catalog.open_object(row) as f:
            return [{"id": row.id, "checksum": file_digest(f)}]


checksum = ChecksumFunc()
