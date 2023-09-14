import asyncio
import io
import math
import os
import tarfile
from string import printable
from tarfile import DIRTYPE, TarInfo
from typing import Any, Dict, List

import pytest

from dql.node import get_path


def insert_entries(data_storage, entries):
    """
    Takes a list of entries and inserts them synchronously.

    This assumes that, for every entry in entries, all of its parent
    directories also have an entry.
    """
    entries_by_parent = [(e["parent"], e) for e in entries]
    entries_by_parent.sort(key=lambda e: (len(e[0]), not e[1]["is_dir"]))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        dir_ids = {"": asyncio.run(data_storage.insert_root())}
        for parent, entry in entries_by_parent:
            entry = {
                **entry,
                "parent_id": dir_ids[parent],
                "partial_id": 0,
            }
            node_id = loop.run_until_complete(data_storage.insert_entry(entry))
            if entry["is_dir"]:
                dir_ids[get_path(parent, entry["name"])] = node_id
    finally:
        asyncio.set_event_loop(None)
        loop.close()
        data_storage.inserts_done()


DEFAULT_TREE: Dict[str, Any] = {
    "description": "Cats and Dogs",
    "cats": {
        "cat1": "meow",
        "cat2": "mrow",
    },
    "dogs": {
        "dog1": "woof",
        "dog2": "arf",
        "dog3": "bark",
        "others": {"dog4": "ruff"},
    },
}


def instantiate_tree(path, tree):
    for key, value in tree.items():
        if isinstance(value, str):
            (path / key).write_text(value)
        elif isinstance(value, bytes):
            (path / key).write_bytes(value)
        elif isinstance(value, dict):
            (path / key).mkdir()
            instantiate_tree(path / key, value)
        else:
            raise TypeError(f"{value=}")


def tree_from_path(path, binary=False):
    tree = {}
    for child in path.iterdir():
        if child.is_dir():
            tree[child.name] = tree_from_path(child, binary)
        else:
            if binary:
                tree[child.name] = child.read_bytes()
            else:
                tree[child.name] = child.read_text()
    return tree


def uppercase_scheme(uri: str) -> str:
    """
    Makes scheme (or protocol) of an url uppercased
    e.g s3://bucket_name -> S3://bucket_name
    """
    return f'{uri.split(":")[0].upper()}:{":".join(uri.split(":")[1:])}'


def make_tar(tree) -> bytes:
    with io.BytesIO() as tmp:
        with tarfile.open(fileobj=tmp, mode="w") as archive:
            write_tar(tree, archive)
        return tmp.getvalue()


def write_tar(tree, archive, curr_dir=""):
    for key, value in tree.items():
        name = f"{curr_dir}/{key}" if curr_dir else key
        if isinstance(value, str):
            value = value.encode("utf-8")
        if isinstance(value, bytes):
            info = TarInfo(name)
            info.size = len(value)
            f = io.BytesIO(value)
            archive.addfile(info, f)
        elif isinstance(value, dict):
            info = TarInfo(name)
            info.type = DIRTYPE
            archive.addfile(info, io.BytesIO())
            write_tar(value, archive, name)


TARRED_TREE: Dict[str, Any] = {"animals.tar": make_tar(DEFAULT_TREE)}


def skip_if_not_sqlite():
    if os.environ.get("DQL_DB_ADAPTER"):
        pytest.skip("This test is not supported on other data storages")


WEBFORMAT_TREE: Dict[str, Any] = {
    "f1.raw": "raw data",
    "f1.json": '{"similarity": 0.001, "md5": "deadbeef"}',
    "f2.raw": "raw data",
    "f2.json": '{"similarity": 0.005, "md5": "foobar"}',
}


def text_embedding(text: str) -> List[float]:
    """
    Compute a simple text embedding based on character counts.

    These aren't the most meaningful, but will produce a 100-element
    vector of floats between 0 and 1 where texts with similar
    character counts will have similar embeddings. Useful for writing
    unit tests without loading a heavy ML model.
    """
    emb = {c: 0.01 for c in printable}
    for c in text:
        try:
            emb[c] += 1.0
        except KeyError:
            pass
    # sqeeze values between 0 and 1 with an adjusted sigmoid function
    return [2.0 / (1.0 + math.e ** (-x)) - 1.0 for x in emb.values()]


def adjusted_float_diff(a: float, b: float, tol: float = 1e-8):
    """
    Compute how far beyond `tol` the difference between `a` and `b` is.
    Useful for verifying that two floats are close to each other.

    Example:
        >>> adjusted_float_diff(1.2, 1.29, 0.1)
        0.0
        >>> adjusted_float_diff(0.2, 0.8, 0.25)
        0.3500000000000001
    """
    return max(0.0, abs(a - b) - tol)
