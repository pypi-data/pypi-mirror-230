from typing import Any, Dict

import pytest
from sqlalchemy import select
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import true

from dql.catalog import indexer_formats

from ..data import ENTRIES, INVALID_ENTRIES
from ..utils import DEFAULT_TREE, TARRED_TREE, insert_entries


def test_validate_paths(data_storage):
    src = "s3://bucket1"
    data_storage = data_storage.clone(uri=src)
    data_storage.init_db(src, True)
    insert_entries(data_storage, ENTRIES + INVALID_ENTRIES)

    def count_valid_nodes():
        n = data_storage.nodes
        query = select(func.count(n.c.valid)).where(  # pylint: disable=not-callable
            n.c.valid == true()
        )
        return next(data_storage.execute(query), (None,))[0]

    before_count = count_valid_nodes()
    data_storage.validate_paths()
    after_count = count_valid_nodes()

    assert before_count == 14
    assert after_count == 11


COMPLEX_TREE: Dict[str, Any] = {
    **TARRED_TREE,
    **DEFAULT_TREE,
    "nested": {"dir": {"path": {"abc.txt": "abc"}}},
}


@pytest.mark.parametrize("use_dataset", [False, True])
@pytest.mark.parametrize("tree", [COMPLEX_TREE], indirect=True)
def test_dir_expansion(cloud_test_catalog, use_dataset, version_aware, cloud_type):
    has_version = version_aware or cloud_type == "gcs"

    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.client_config = ctc.client_config
    catalog.index([ctc.src_uri], index_processors=indexer_formats["tar-files"])

    st = catalog.data_storage.clone(ctc.src_uri)
    if use_dataset:
        dataset = catalog.create_shadow_dataset("ds1", [ctc.src_uri], recursive=True)
        q = st.dataset_rows(dataset.id).dir_expansion()
    else:
        q = st.nodes.dir_expansion()
    columns = (
        "id",
        "vtype",
        "is_dir",
        "source",
        "parent",
        "name",
        "version",
        "location",
    )
    result = [dict(zip(columns, r)) for r in st.data_execute(q)]
    to_compare = [
        (r["parent"], r["name"], r["vtype"], r["is_dir"], r["version"] != "")
        for r in result
    ]

    assert all(r["source"] == ctc.src_uri for r in result)
    # Note, we have both a file and a directory entry for expanded tar files
    assert to_compare == [
        ("", "animals.tar", "", 0, has_version),
        ("", "animals.tar", "", 1, False),
        ("", "cats", "", 1, False),
        ("", "description", "", 0, has_version),
        ("", "dogs", "", 1, False),
        ("", "nested", "", 1, False),
        ("animals.tar", "cats", "", 1, False),
        ("animals.tar", "description", "tar", 0, False),
        ("animals.tar", "dogs", "", 1, False),
        ("animals.tar/cats", "cat1", "tar", 0, False),
        ("animals.tar/cats", "cat2", "tar", 0, False),
        ("animals.tar/dogs", "dog1", "tar", 0, False),
        ("animals.tar/dogs", "dog2", "tar", 0, False),
        ("animals.tar/dogs", "dog3", "tar", 0, False),
        ("animals.tar/dogs", "others", "", 1, False),
        ("animals.tar/dogs/others", "dog4", "tar", 0, False),
        ("cats", "cat1", "", 0, has_version),
        ("cats", "cat2", "", 0, has_version),
        ("dogs", "dog1", "", 0, has_version),
        ("dogs", "dog2", "", 0, has_version),
        ("dogs", "dog3", "", 0, has_version),
        ("dogs", "others", "", 1, False),
        ("dogs/others", "dog4", "", 0, has_version),
        ("nested", "dir", "", 1, False),
        ("nested/dir", "path", "", 1, False),
        ("nested/dir/path", "abc.txt", "", 0, has_version),
    ]
