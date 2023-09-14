import io
import json
from random import getrandbits
from textwrap import dedent

import pytest
import sqlalchemy
from sqlalchemy import tuple_

from dql.catalog import indexer_formats
from dql.data_storage.abstract import RANDOM_BITS
from dql.data_storage.schema import DATASET_CORE_COLUMN_NAMES
from dql.dataset import Status as DatasetStatus
from dql.loader import DataView
from dql.query import C, DatasetQuery, LocalFilename, Object, generator, udf
from dql.query.builtins import checksum, index_tar
from dql.sql.functions.array import cosine_distance, euclidean_distance
from dql.sql.types import Array, Float32, Int, String

from ..utils import DEFAULT_TREE, TARRED_TREE, adjusted_float_diff, text_embedding


@pytest.mark.parametrize("from_path", [True, False])
@pytest.mark.parametrize("save", [True, False])
@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_filter(cloud_test_catalog, save, from_path):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    # ensure we can select a subset of a bucket properly
    path = f"{cloud_test_catalog.src_uri}/cats"
    if from_path:
        ds = DatasetQuery(path=path, catalog=catalog, client_config=conf)
    else:
        sources = [path]
        globs = [s.rstrip("/") + "/*" for s in sources]
        catalog.index(sources, client_config=conf)
        catalog.create_shadow_dataset(
            "animals", globs, client_config=conf, recursive=True
        )
        ds = DatasetQuery(name="animals", catalog=catalog)
    q = ds.filter(C.size < 13).filter(C.parent.glob("cats*") | (C.size < 4))
    if save:
        ds_name = "animals_cats"
        q.save(ds_name)
        q = DatasetQuery(name=ds_name, catalog=catalog)
        dataset_record = catalog.get_dataset(ds_name)
        assert dataset_record.status == DatasetStatus.COMPLETE
    result = q.results()
    count = q.count()
    assert len(result) == 2
    assert count == 2


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_select(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    path = cloud_test_catalog.src_uri
    ds = DatasetQuery(path=path, catalog=catalog, client_config=conf)
    q = (
        ds.order_by(C.size.desc(), C.name)
        .limit(6)
        .select(C.name, size10x=C.size * 10, size100x=C.size * 100)
    )
    result = q.results()
    assert result == [
        ("description", 130, 1300),
        ("cat1", 40, 400),
        ("cat2", 40, 400),
        ("dog1", 40, 400),
        ("dog3", 40, 400),
        ("dog4", 40, 400),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_select_missing_column(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    path = cloud_test_catalog.src_uri
    ds = DatasetQuery(path=path, catalog=catalog, client_config=conf)
    ds1 = ds.select(C.missing_column_name)
    ds2 = ds.select("missing_column_name")
    # The exception type varies by database backend
    exc1 = pytest.raises(Exception, ds1.results)
    assert "missing_column_name" in str(exc1.value)
    exc2 = pytest.raises(KeyError, ds2.results)
    assert "missing_column_name" in str(exc2.value)


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_select_except(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    path = cloud_test_catalog.src_uri
    ds = DatasetQuery(path=path, catalog=catalog, client_config=conf)
    q = (
        ds.order_by(C.size.desc(), C.name)
        .limit(6)
        .select(C.parent, "name", C.size, size10x=C.size * 10, size100x=C.size * 100)
        .select_except(C.parent, C.size10x)
    )
    result = q.results()
    assert result == [
        ("description", 13, 1300),
        ("cat1", 4, 400),
        ("cat2", 4, 400),
        ("dog1", 4, 400),
        ("dog3", 4, 400),
        ("dog4", 4, 400),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_select_default(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    path = cloud_test_catalog.src_uri
    ds = DatasetQuery(path=path, catalog=catalog, client_config=conf)
    original_result = ds.order_by(C.size.desc(), C.name).limit(6).results()
    q = (
        ds.order_by(C.size.desc(), C.name)
        .limit(6)
        .mutate(size10x=C.size * 10, size100x=C.size * 100)
        .select_default()
    )
    result = q.results()
    assert result == original_result
    assert len(result[0]) == len(DATASET_CORE_COLUMN_NAMES)


@pytest.mark.parametrize("save", [True, False])
@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_mutate(cloud_test_catalog, save):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    path = cloud_test_catalog.src_uri
    ds = DatasetQuery(path=path, catalog=catalog, client_config=conf)
    q = (
        ds.mutate(size10x=C.size * 10)
        .mutate(size1000x=C.size10x * 100)
        .mutate(
            ("s2", C.size * 2),
            ("s3", C.size * 3),
            s4=C.size * 4,
        )
        .filter((C.size10x < 40) | (C.size10x > 100) | C.name.glob("cat*"))
        .order_by(C.size10x.desc(), C.name)
    )
    if save:
        ds_name = "animals_cats"
        q.save(ds_name)
        new_query = DatasetQuery(name=ds_name, catalog=catalog).order_by(
            C.size10x.desc(), C.name
        )
        result = new_query.results(row_factory=lambda c, v: dict(zip(c, v)))
        dataset_record = catalog.get_dataset(ds_name)
        assert dataset_record.status == DatasetStatus.COMPLETE
    else:
        result = q.results(row_factory=lambda c, v: dict(zip(c, v)))
    assert len(result) == 4
    assert len(result[0]) == 23
    cols = {"size10x", "size1000x", "s2", "s3", "s4"}
    new_data = [[v for k, v in r.items() if k in cols] for r in result]
    assert new_data == [
        [130, 13000, 26, 39, 52],
        [40, 4000, 8, 12, 16],
        [40, 4000, 8, 12, 16],
        [30, 3000, 6, 9, 12],
    ]


@pytest.mark.parametrize("save", [True, False])
@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_order_by_limit(cloud_test_catalog, save):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    path = cloud_test_catalog.src_uri
    ds = DatasetQuery(path=path, catalog=catalog, client_config=conf)
    q = ds.order_by(C.name.desc()).limit(5)
    if save:
        ds_name = "animals_cats"
        q.save(ds_name)
        new_query = DatasetQuery(name=ds_name, catalog=catalog).order_by(C.name.desc())
        result = new_query.results()
        dataset_record = catalog.get_dataset(ds_name)
        assert dataset_record.status == DatasetStatus.COMPLETE
    else:
        result = q.results()
    assert [r[5] for r in result] == ["dog4", "dog3", "dog2", "dog1", "description"]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_udf(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    sources = [cloud_test_catalog.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources, client_config=conf)
    catalog.create_shadow_dataset("animals", globs, client_config=conf, recursive=True)

    @udf((("name_len", Int),), (C.name,))
    def name_len(name):
        # A very simple udf.
        return (len(name),)

    q = (
        DatasetQuery(name="animals", catalog=catalog)
        .filter(C.size < 13)
        .filter(C.parent.glob("cats*") | (C.size < 4))
        .add_signals(name_len)
    )
    result1 = q.results()
    # ensure that we're able to run with same query multiple times
    result2 = q.results()
    count = q.count()
    # ensure that temporary tables are cleaned up
    assert [
        t
        for t in sqlalchemy.inspect(catalog.data_storage.data_engine).get_table_names()
        if t.startswith("udf_")
    ] == []
    assert len(result1) == 3
    assert len(result2) == 3
    assert count == 3


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
@pytest.mark.parametrize("batch", [1, 4])
def test_class_udf(cloud_test_catalog, batch):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    sources = [cloud_test_catalog.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources, client_config=conf)
    catalog.create_shadow_dataset("animals", globs, client_config=conf, recursive=True)

    @udf((("total", Int),), (C.size,), method="sum", batch=batch)
    class MyUDF:
        def __init__(self, constant, multiplier=1):
            self.constant = constant
            self.multiplier = multiplier
            self.batch = batch

        def sum(self, size):
            if self.batch > 1:
                return [(self.constant + size_ * self.multiplier,) for (size_,) in size]
            return (self.constant + size * self.multiplier,)

    q = (
        DatasetQuery(name="animals", catalog=catalog)
        .filter(C.size < 13)
        .add_signals(MyUDF(5, multiplier=2))
    )
    results = q.select(C.size, C.total).order_by(C.size).results()
    assert results == [
        (3, 11),
        (4, 13),
        (4, 13),
        (4, 13),
        (4, 13),
        (4, 13),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
@pytest.mark.parametrize("batch", [False, True])
def test_udf_parallel(cloud_test_catalog_tmpfile, batch):
    catalog = cloud_test_catalog_tmpfile.catalog
    conf = cloud_test_catalog_tmpfile.client_config
    sources = [cloud_test_catalog_tmpfile.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources, client_config=conf)
    catalog.create_shadow_dataset("animals", globs, client_config=conf, recursive=True)

    @udf((("name_len", Int),), (C.name,))
    def name_len_local(name):
        # A very simple udf.
        return (len(name),)

    @udf((("name_len", Int),), (C.name,), batch=2)
    def name_len_batch(names):
        # A very simple udf.
        return [(len(name),) for (name,) in names]

    if batch:
        # Batching is enabled, we need a udf that acts on
        # lists of inputs.
        udf_func = name_len_batch
    else:
        udf_func = name_len_local

    q = (
        DatasetQuery(name="animals", catalog=catalog)
        .filter(C.size < 13)
        .filter(C.parent.glob("cats*") | (C.size < 4))
        .add_signals(udf_func, processes=True)
    )
    result = q.results()

    assert len(result) == 3


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_udf_parallel_exec_error(cloud_test_catalog_tmpfile):
    catalog = cloud_test_catalog_tmpfile.catalog
    conf = cloud_test_catalog_tmpfile.client_config
    sources = [cloud_test_catalog_tmpfile.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources, client_config=conf)
    catalog.create_shadow_dataset("animals", globs, client_config=conf, recursive=True)

    @udf((("name_len", Int),), (C.name,))
    def name_len_error(_name):
        # A udf that raises an exception
        raise RuntimeError("Test Error!")

    q = (
        DatasetQuery(name="animals", catalog=catalog)
        .filter(C.size < 13)
        .filter(C.parent.glob("cats*") | (C.size < 4))
        .add_signals(name_len_error, processes=True)
    )
    with pytest.raises(RuntimeError, match="UDF Execution Failed!"):
        q.results()


def test_apply_udf(cloud_test_catalog, tmp_path):
    catalog = cloud_test_catalog.catalog
    sources = [cloud_test_catalog.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources)
    catalog.create_shadow_dataset("animals", globs, recursive=True)

    code = """\
        from dql.query import C, udf
        from dql.sql.types import Int

        @udf((("name_len", Int),), (C.name,))
        def name_len(name):
            # A very simple udf.
            return (len(name),)
    """
    script = tmp_path / "foo.py"
    script.write_text(dedent(code))

    catalog.apply_udf(f"{script}:name_len", cloud_test_catalog.src_uri, "from-storage")
    q = DatasetQuery(name="from-storage", catalog=catalog).filter(C.name_len == 4)
    assert len(q.results()) == 6

    catalog.apply_udf(f"{script}:name_len", "ds://animals", "from-dataset")
    q = DatasetQuery(name="from-dataset", catalog=catalog).filter(C.name_len == 4)
    assert len(q.results()) == 6


def to_str(buf) -> str:
    return io.TextIOWrapper(buf, encoding="utf8").read()


@pytest.mark.parametrize(
    "param", [LocalFilename(), Object(to_str, False), Object(to_str, True)]
)
def test_udf_object_param(cloud_test_catalog, dogs_shadow_dataset, param):
    # Setup catalog.
    catalog = cloud_test_catalog.catalog
    catalog.client_config = cloud_test_catalog.client_config

    if isinstance(param, Object):

        @udf((("signal", String),), (C.name, param))
        def signal(name, obj):
            # A very simple udf.
            return (name + " -> " + obj,)

    else:

        @udf((("signal", String),), (C.name, param))
        def signal(name, local_filename):
            with open(local_filename, encoding="utf8") as f:
                obj = f.read()
            return (name + " -> " + obj,)

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).add_signals(signal)
    result = q.results()

    assert len(result) == 4
    signals = {r[-1] for r in result}
    assert signals == {"dog1 -> woof", "dog2 -> arf", "dog3 -> bark", "dog4 -> ruff"}


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_union(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    sources = [str(cloud_test_catalog.src_uri)]
    catalog.index(sources, client_config=conf)

    src = cloud_test_catalog.src_uri
    catalog.create_shadow_dataset(
        "dogs", [f"{src}/dogs/*"], client_config=conf, recursive=True
    )
    catalog.create_shadow_dataset(
        "cats", [f"{src}/cats/*"], client_config=conf, recursive=True
    )

    dogs = DatasetQuery(name="dogs", catalog=catalog)
    cats = DatasetQuery(name="cats", catalog=catalog)

    (dogs | cats).save("dogs_cats")

    q = DatasetQuery(name="dogs_cats", catalog=catalog)
    result = q.results()
    count = q.count()
    assert len(result) == 6
    assert count == 6


def test_loader_from_query(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    src_uri = cloud_test_catalog.src_uri
    catalog.index([src_uri], client_config=conf)
    catalog.create_shadow_dataset(
        "animals", [f"{src_uri}/*"], client_config=conf, recursive=True
    )
    q = DatasetQuery(name="animals", catalog=catalog).filter(C.parent.glob("cats*"))

    def transform(row, sample):
        return sample, row.name[-1]

    ds = DataView.from_query(
        q, reader=to_str, transform=transform, catalog=catalog, client_config=conf
    )
    assert set(ds) == {("meow", "1"), ("mrow", "2")}


def create_subobject(row, name: str, size: int):
    """Create a subobject with this row as its parent."""
    return {
        # Values that depend on the parent object.
        "vtype": "fake",
        "dir_type": 0,
        "parent_id": row.id,
        # Inherited values.
        "owner_name": row.owner_name,
        "owner_id": row.owner_id,
        "is_latest": row.is_latest,
        "source": row.source,
        # User-provided values.
        "name": name,
        "parent": row.path,
        "size": size,
        # Unspecified.
        "version": None,
        "etag": None,
        # Generated.
        "random": getrandbits(RANDOM_BITS),
    }


def test_row_generator(cloud_test_catalog, dogs_shadow_dataset):
    # Setup catalog.
    catalog = cloud_test_catalog.catalog
    catalog.client_config = cloud_test_catalog.client_config

    @generator(C.name, C.parent)
    def gen(parent, _, __):
        # A very simple generator.
        yield create_subobject(parent, "subobject", 50)

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).generate(gen)
    result = q.results()

    assert len(result) == 8

    signals = {(r[4], r[5]) for r in result}  # parent, name
    assert signals == {
        ("dogs", "dog1"),
        ("dogs/dog1", "subobject"),
        ("dogs", "dog2"),
        ("dogs/dog2", "subobject"),
        ("dogs", "dog3"),
        ("dogs/dog3", "subobject"),
        ("dogs/others", "dog4"),
        ("dogs/others/dog4", "subobject"),
    }


@pytest.mark.parametrize("tree", [TARRED_TREE], indirect=True)
def test_index_tar(cloud_test_catalog):
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.client_config = ctc.client_config
    catalog.index([ctc.src_uri])
    catalog.create_shadow_dataset("animals", [ctc.src_uri])

    q = DatasetQuery(name="animals", catalog=catalog).generate(index_tar)
    q.save("extracted")

    rows = list(catalog.ls_dataset_rows("extracted"))
    assert {row.name for row in rows} == {
        "animals.tar",
        "cat1",
        "cat2",
        "description",
        "dog1",
        "dog2",
        "dog3",
        "dog4",
    }

    offsets = [
        json.loads(row.location)[0]["offset"]
        for row in rows
        if row.name != "animals.tar"
    ]
    # Check that offsets are unique integers
    assert all(isinstance(offset, int) for offset in offsets)
    assert len(set(offsets)) == len(offsets)

    assert all(row.vtype == "tar" for row in rows if row.name != "animals.tar")


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_checksum_udf(cloud_test_catalog, dogs_shadow_dataset):
    # Setup catalog.
    catalog = cloud_test_catalog.catalog
    catalog.client_config = cloud_test_catalog.client_config

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).add_signals(
        checksum
    )
    result = q.results()

    assert len(result) == 4


@pytest.mark.parametrize("tree", [TARRED_TREE], indirect=True)
def test_tar_loader(cloud_test_catalog):
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.client_config = ctc.client_config
    catalog.index([ctc.src_uri])
    catalog.create_shadow_dataset("animals", [ctc.src_uri])
    q = DatasetQuery(name="animals", catalog=catalog).generate(index_tar)
    q.save("extracted")

    q = DatasetQuery(name="extracted", catalog=catalog).filter(C.parent.glob("*/cats*"))
    assert len(q.results()) == 2

    def transform(row, sample):
        return sample, row.name[-1]

    ds = DataView.from_query(q, reader=to_str, transform=transform, catalog=catalog)
    assert set(ds) == {("meow", "1"), ("mrow", "2")}


@pytest.mark.parametrize("tree", [{**DEFAULT_TREE, **TARRED_TREE}], indirect=True)
def test_simple_dataset_query(cloud_test_catalog):
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    data_storage = catalog.data_storage
    catalog.client_config = ctc.client_config
    catalog.index([ctc.src_uri], index_processors=indexer_formats["tar-files"])
    catalog.create_shadow_dataset("ds1", [ctc.src_uri], recursive=True)
    DatasetQuery(ctc.src_uri, catalog=catalog).save("ds2")

    n = data_storage.nodes_table(ctc.src_uri)
    nq = n.dataset_query().order_by(n.c.parent, n.c.name)
    ds_queries = [nq]
    for ds_name in ("ds1", "ds2"):
        dataset = data_storage.get_dataset(ds_name)
        d = data_storage.dataset_rows(dataset.id)
        dq = d.select().order_by(d.c.parent, d.c.name)
        ds_queries.append(dq)

    ignore_cols = ["id", "parent_id"]
    node_ds, ds1, ds2 = (
        [
            {k: v for k, v in zip(DATASET_CORE_COLUMN_NAMES, r) if k not in ignore_cols}
            for r in data_storage.data_execute(q)
        ]
        for q in ds_queries
    )

    # everything except the id field should match
    assert ds1 == node_ds
    assert ds2 == node_ds
    assert [(r["parent"], r["name"]) for r in node_ds] == [
        ("", "animals.tar"),
        ("", "description"),
        ("animals.tar", "description"),
        ("animals.tar/cats", "cat1"),
        ("animals.tar/cats", "cat2"),
        ("animals.tar/dogs", "dog1"),
        ("animals.tar/dogs", "dog2"),
        ("animals.tar/dogs", "dog3"),
        ("animals.tar/dogs/others", "dog4"),
        ("cats", "cat1"),
        ("cats", "cat2"),
        ("dogs", "dog1"),
        ("dogs", "dog2"),
        ("dogs", "dog3"),
        ("dogs/others", "dog4"),
    ]


@pytest.mark.parametrize("tree", [{**DEFAULT_TREE, **TARRED_TREE}], indirect=True)
def test_similarity_search(cloud_test_catalog):
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.client_config = ctc.client_config
    catalog.index([ctc.src_uri], index_processors=indexer_formats["tar-files"])

    @udf(
        output=(("embedding", Array(Float32)),),
        parameters=(Object(to_str),),
        method="embedding",
    )
    class TextEmbeddingGenerator:
        def embedding(self, text):
            return (text_embedding(text),)

    target_embedding, source, parent, name = (
        DatasetQuery(ctc.src_uri, catalog=catalog)
        .filter(~C.name.glob("*.tar"))
        .order_by(C.source, C.parent, C.name)
        .limit(1)
        .add_signals(TextEmbeddingGenerator())
        .select(C.embedding, C.source, C.parent, C.name)
        .results()[0]
    )
    q = (
        DatasetQuery(ctc.src_uri, catalog=catalog)
        .filter(
            ~C.name.glob("*.tar"),
            tuple_(C.source, C.parent, C.name) != (source, parent, name),
        )
        .add_signals(TextEmbeddingGenerator())
        .mutate(
            cos_dist=cosine_distance(C.embedding, target_embedding),
            eucl_dist=euclidean_distance(C.embedding, target_embedding),
        )
        .select(C.parent, C.name, C.cos_dist, C.eucl_dist)
        .order_by(C.source, C.parent, C.name)
    )
    count = q.count()
    assert count == 13

    result = q.results()
    expected = [
        ("animals.tar", "description", 0.0, 0.0),
        ("animals.tar/cats", "cat1", 0.8508677010357059, 1.9078358385397216),
        ("animals.tar/cats", "cat2", 0.8508677010357059, 1.9078358385397216),
        ("animals.tar/dogs", "dog1", 0.7875133863812602, 1.8750659656122843),
        ("animals.tar/dogs", "dog2", 0.7356502722055684, 1.775619888314893),
        ("animals.tar/dogs", "dog3", 0.7695916496857775, 1.8344983482620636),
        ("animals.tar/dogs/others", "dog4", 0.9789704524691446, 2.0531542018152322),
        ("cats", "cat1", 0.8508677010357059, 1.9078358385397216),
        ("cats", "cat2", 0.8508677010357059, 1.9078358385397216),
        ("dogs", "dog1", 0.7875133863812602, 1.8750659656122843),
        ("dogs", "dog2", 0.7356502722055684, 1.775619888314893),
        ("dogs", "dog3", 0.7695916496857775, 1.8344983482620636),
        ("dogs/others", "dog4", 0.9789704524691446, 2.0531542018152322),
    ]
    expected_diffs = [(p, n, 0.0, 0.0) for p, n, _, _ in expected]

    diffs = [
        (p2, n2, adjusted_float_diff(c1, c2, 1e-8), adjusted_float_diff(e1, e2, 1e-5))
        for (p1, n1, c1, e1), (p2, n2, c2, e2) in zip(result, expected)
    ]
    assert diffs == expected_diffs


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_subtract(cloud_test_catalog):
    from dql.dataset import DatasetRow

    @udf((("name_len", Int),), (C.name,))
    def name_len(name):
        # A very simple udf.
        return (len(name),)

    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    sources = [str(cloud_test_catalog.src_uri)]
    catalog.index(sources, client_config=conf)

    src = cloud_test_catalog.src_uri
    catalog.create_shadow_dataset(
        "dogs", [f"{src}/dogs/*"], client_config=conf, recursive=True
    )
    catalog.create_shadow_dataset(
        "cats", [f"{src}/cats/*"], client_config=conf, recursive=True
    )

    dogs = DatasetQuery(name="dogs", catalog=catalog)
    cats = DatasetQuery(name="cats", catalog=catalog)

    (dogs | cats).save("dogs_cats")

    dogs_cats = DatasetQuery(name="dogs_cats", catalog=catalog)

    # subtracting dataset from dataset
    q = dogs_cats.subtract(dogs)
    result = q.results(row_factory=DatasetRow.from_result_row)
    assert sorted([r.name for r in result]) == ["cat1", "cat2"]

    # subtracting dataset out of index
    q = DatasetQuery(f"{src}", catalog=catalog).subtract(cats)
    result = q.results(row_factory=DatasetRow.from_result_row)
    assert sorted([r.name for r in result]) == [
        "description",
        "dog1",
        "dog2",
        "dog3",
        "dog4",
    ]

    # subtracting index out of index
    q = DatasetQuery(f"{src}", catalog=catalog).subtract(
        DatasetQuery(f"{src}/dogs/*", catalog=catalog)
    )
    result = q.results(row_factory=DatasetRow.from_result_row)
    assert sorted([r.name for r in result]) == ["cat1", "cat2", "description"]

    # subtracting with filter
    q = (
        DatasetQuery(f"{src}", catalog=catalog)
        .filter(C.name.glob("dog*"))
        .subtract(cats)
    )
    result = q.results(row_factory=DatasetRow.from_result_row)
    assert sorted([r.name for r in result]) == ["dog1", "dog2", "dog3", "dog4"]

    # chain subtracting
    q = dogs_cats.subtract(dogs).subtract(cats)
    result = q.results()
    count = q.count()
    assert len(result) == 0
    assert count == 0

    # filtering after subtract
    q = (
        DatasetQuery(f"{src}", catalog=catalog)
        .subtract(cats)
        .filter(C.name.glob("dog*"))
    )
    result = q.results(row_factory=DatasetRow.from_result_row)
    assert sorted([r.name for r in result]) == ["dog1", "dog2", "dog3", "dog4"]

    # subtract with usage of udfs and union
    # simulates updating dataset with new changes in index and not re-calculating
    # all udfs, but only for those that are new
    cats.add_signals(name_len).save("cats_with_signals")
    cats_with_signals = DatasetQuery(name="cats_with_signals", catalog=catalog)
    q = (
        DatasetQuery(f"{src}", catalog=catalog)
        .subtract(cats_with_signals)
        .add_signals(name_len)
        .union(cats_with_signals)
    )
    result = q.results(row_factory=DatasetRow.from_result_row)
    assert sorted([r.name for r in result]) == sorted(
        ["description", "dog1", "dog2", "dog3", "dog4", "cat1", "cat2"]
    )
    assert all([r.custom["name_len"] > 0 for r in result])

    # subtracting with source and target filter
    # only dog2 file has size less then 4
    all_except_dog2 = DatasetQuery(f"{src}", catalog=catalog).filter(C.size > 3)
    only_cats = dogs_cats.filter(C.name.glob("cat*"))
    q = all_except_dog2.subtract(only_cats)
    result = q.results(row_factory=DatasetRow.from_result_row)
    assert sorted([r.name for r in result]) == ["description", "dog1", "dog3", "dog4"]

    # subtracting after union
    q = dogs.union(cats).subtract(dogs)
    result = q.results(row_factory=DatasetRow.from_result_row)
    assert sorted([r.name for r in result]) == ["cat1", "cat2"]

    # subtract with itself
    q = dogs.subtract(dogs)
    result = q.results()
    count = q.count()
    assert len(result) == 0
    assert count == 0
