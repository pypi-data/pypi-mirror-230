import io
import uuid
from unittest.mock import patch

import pytest
import sqlalchemy as sa

from dql.catalog.catalog import DATASET_INTERNAL_ERROR_MESSAGE
from dql.dataset import Status as DatasetStatus
from dql.error import DatasetNotFoundError
from dql.loader import DataView

# pylint: disable=redefined-outer-name,unused-argument,protected-access


def add_column(engine, table_name, column, catalog):
    # Simple method that adds new column to a table, with default value if specified
    column_name = column.compile(dialect=engine.dialect)
    column_type = column.type.compile(engine.dialect)
    if hasattr(catalog.data_storage, "raw_sql_execute"):
        execute = catalog.data_storage.raw_sql_execute
    else:
        execute = catalog.data_storage.db.execute
    if column.default:
        execute(
            "ALTER TABLE %s ADD COLUMN %s %s DEFAULT %s"
            % (table_name, column_name, column_type, column.default.arg)
        )
    else:
        execute(
            "ALTER TABLE {} ADD COLUMN {} {}".format(
                table_name, column_name, column_type
            )
        )


@pytest.fixture
def empty_shadow_dataset(listed_bucket, cloud_test_catalog):
    shadow_dataset_name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog

    catalog.create_shadow_dataset(
        shadow_dataset_name,
        [],
        client_config=cloud_test_catalog.client_config,
        populate=False,
    )

    return catalog.data_storage.get_dataset(shadow_dataset_name)


@pytest.fixture
def cats_shadow_dataset(listed_bucket, cloud_test_catalog):
    shadow_dataset_name = uuid.uuid4().hex
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    catalog.create_shadow_dataset(
        shadow_dataset_name,
        [f"{src_uri}/cats/*"],
        client_config=cloud_test_catalog.client_config,
        recursive=True,
    )

    return catalog.data_storage.get_dataset(shadow_dataset_name)


@pytest.fixture
def cats_registered_dataset(cloud_test_catalog, cats_shadow_dataset):
    catalog = cloud_test_catalog.catalog
    catalog.register_shadow_dataset(
        cats_shadow_dataset.name,
        description="cats dataset",
        labels=["cats", "dataset"],
    )

    return catalog.data_storage.get_dataset(cats_shadow_dataset.name)


def test_get_dataset(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    dataset = catalog.get_dataset(dogs_shadow_dataset.name)
    assert dataset.name == dogs_shadow_dataset.name

    with pytest.raises(DatasetNotFoundError):
        catalog.get_dataset("wrong name")


# Returns None if the table does not exist
def get_table_row_count(data_storage, table_name):
    if not data_storage.has_table(table_name):
        return None
    query = sa.select(sa.func.count()).select_from(sa.text(table_name))
    return next(data_storage.execute(query), (None,))[0]


def test_creating_shadow_dataset(listed_bucket, cloud_test_catalog):
    shadow_dataset_name = uuid.uuid4().hex
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    dataset = catalog.create_shadow_dataset(
        shadow_dataset_name,
        [f"{src_uri}/dogs/*"],
        client_config=cloud_test_catalog.client_config,
        recursive=True,
    )

    assert dataset.name == shadow_dataset_name
    assert dataset.description is None
    assert dataset.versions is None
    assert dataset.labels == []
    assert dataset.shadow is True
    assert dataset.status == DatasetStatus.COMPLETE
    assert dataset.created_at
    assert dataset.finished_at
    assert dataset.error_message == ""
    assert dataset.error_stack == ""
    assert dataset.script_output == ""
    assert dataset.sources == f"{src_uri}/dogs/*"
    assert dataset.query_script == ""

    dataset_table_name = catalog.data_storage.dataset_table_name(dataset.id)
    assert get_table_row_count(catalog.data_storage, dataset_table_name)


def test_creating_shadow_dataset_failed(listed_bucket, cloud_test_catalog):
    shadow_dataset_name = uuid.uuid4().hex
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog
    with patch.object(
        catalog.data_storage,
        "insert_into_shadow_dataset",
        side_effect=RuntimeError("Error"),
    ) as _:
        with pytest.raises(RuntimeError):
            catalog.create_shadow_dataset(
                shadow_dataset_name,
                [f"{src_uri}/dogs/*"],
                client_config=cloud_test_catalog.client_config,
                recursive=True,
            )
    dataset = catalog.data_storage.get_dataset(shadow_dataset_name)

    assert dataset.name == shadow_dataset_name
    assert dataset.status == DatasetStatus.FAILED
    assert dataset.created_at
    assert dataset.finished_at
    assert dataset.error_message == DATASET_INTERNAL_ERROR_MESSAGE
    assert dataset.error_stack
    assert dataset.sources == f"{src_uri}/dogs/*"
    assert dataset.query_script == ""

    dataset_table_name = catalog.data_storage.dataset_table_name(dataset.id)
    assert get_table_row_count(catalog.data_storage, dataset_table_name) == 0


def test_creating_empty_dataset(listed_bucket, cloud_test_catalog):
    shadow_dataset_name = uuid.uuid4().hex
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    dataset = catalog.create_shadow_dataset(
        shadow_dataset_name,
        [f"{src_uri}/dogs/*"],
        client_config=cloud_test_catalog.client_config,
        recursive=True,
        populate=False,
    )

    assert dataset.name == shadow_dataset_name
    assert dataset.status == DatasetStatus.CREATED
    assert dataset.shadow is True
    assert dataset.created_at
    assert not dataset.finished_at

    dataset_table_name = catalog.data_storage.dataset_table_name(dataset.id)
    assert get_table_row_count(catalog.data_storage, dataset_table_name) is None


def test_creating_dataset_after_empty(listed_bucket, cloud_test_catalog):
    shadow_dataset_name = uuid.uuid4().hex
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    dataset = catalog.create_shadow_dataset(
        shadow_dataset_name,
        [f"{src_uri}/dogs/*"],
        client_config=cloud_test_catalog.client_config,
        recursive=True,
        populate=False,
    )

    assert dataset.status == DatasetStatus.CREATED

    dataset = catalog.create_shadow_dataset(
        shadow_dataset_name,
        [f"{src_uri}/dogs/*"],
        client_config=cloud_test_catalog.client_config,
        recursive=True,
    )

    assert dataset.status == DatasetStatus.COMPLETE
    assert dataset.created_at
    assert dataset.finished_at

    dataset_table_name = catalog.data_storage.dataset_table_name(dataset.id)
    assert get_table_row_count(catalog.data_storage, dataset_table_name)


def test_creating_shadow_dataset_whole_bucket(listed_bucket, cloud_test_catalog):
    shadow_dataset_name_1 = uuid.uuid4().hex
    shadow_dataset_name_2 = uuid.uuid4().hex
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    catalog.create_shadow_dataset(
        shadow_dataset_name_1,
        [f"{src_uri}"],
        client_config=cloud_test_catalog.client_config,
        recursive=True,
    )
    catalog.create_shadow_dataset(
        shadow_dataset_name_2,
        [f"{src_uri}/"],
        client_config=cloud_test_catalog.client_config,
        recursive=True,
    )

    expected_rows = {
        "description",
        "cat1",
        "cat2",
        "dog1",
        "dog2",
        "dog3",
        "dog4",
    }

    assert {
        r.name for r in catalog.ls_dataset_rows(shadow_dataset_name_1)
    } == expected_rows

    assert {
        r.name for r in catalog.ls_dataset_rows(shadow_dataset_name_2)
    } == expected_rows


def test_registering_dataset(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    catalog.register_shadow_dataset(
        dogs_shadow_dataset.name,
        description="dogs dataset",
        labels=["dogs", "dataset"],
    )

    dataset = catalog.data_storage.get_dataset(dogs_shadow_dataset.name)
    dataset_table_name = catalog.data_storage.dataset_table_name(dataset.id, 1)
    assert dataset.name == dogs_shadow_dataset.name
    assert dataset.description == "dogs dataset"
    assert dataset.versions_values == [1]
    assert dataset.labels == ["dogs", "dataset"]
    assert dataset.shadow is False
    assert dataset.status == DatasetStatus.COMPLETE
    assert dataset.sources == ""
    assert dataset.query_script == ""
    assert dataset.versions[0].sources == dogs_shadow_dataset.sources
    assert dataset.versions[0].query_script == dogs_shadow_dataset.query_script
    assert get_table_row_count(catalog.data_storage, dataset_table_name)


def test_registering_dataset_with_new_name(cloud_test_catalog, dogs_shadow_dataset):
    new_dataset_name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog

    catalog.register_shadow_dataset(
        dogs_shadow_dataset.name,
        registered_name=new_dataset_name,
        description="dogs dataset",
        labels=["dogs", "dataset"],
    )
    dataset = catalog.data_storage.get_dataset(new_dataset_name)
    assert dataset
    dataset_table_name = catalog.data_storage.dataset_table_name(dataset.id, 1)
    assert dataset.name == new_dataset_name
    assert get_table_row_count(catalog.data_storage, dataset_table_name)


def test_registering_dataset_with_custom_version(
    cloud_test_catalog, dogs_shadow_dataset
):
    catalog = cloud_test_catalog.catalog

    catalog.register_shadow_dataset(
        dogs_shadow_dataset.name,
        version=5,
        description="dogs dataset",
        labels=["dogs", "dataset"],
    )

    dataset = catalog.data_storage.get_dataset(dogs_shadow_dataset.name)
    assert dataset.versions_values == [5]


def test_registering_dataset_as_version_of_another_registered(
    cloud_test_catalog, dogs_registered_dataset, cats_shadow_dataset
):
    catalog = cloud_test_catalog.catalog

    catalog.register_shadow_dataset(
        cats_shadow_dataset.name,
        registered_name=dogs_registered_dataset.name,
        version=3,
    )

    dogs_dataset = catalog.data_storage.get_dataset(dogs_registered_dataset.name)
    assert dogs_dataset.versions_values == [1, 3]

    assert dogs_dataset.sources == ""
    assert dogs_dataset.query_script == ""
    dogs_dataset.sort_versions()
    assert dogs_dataset.versions[1].sources == cats_shadow_dataset.sources
    assert dogs_dataset.versions[1].query_script == cats_shadow_dataset.query_script

    # checking newly created dogs version 3 data
    assert {
        r.name for r in catalog.ls_dataset_rows(dogs_registered_dataset.name, version=3)
    } == {
        "cat1",
        "cat2",
    }

    # assert cats shadow dataset is removed
    cats_dataset_name = catalog.data_storage.dataset_table_name(cats_shadow_dataset.id)
    with pytest.raises(DatasetNotFoundError):
        catalog.data_storage.get_dataset(cats_shadow_dataset.name)
    assert get_table_row_count(catalog.data_storage, cats_dataset_name) is None


def test_removing_dataset(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    dataset_table_name = catalog.data_storage.dataset_table_name(dogs_shadow_dataset.id)
    assert get_table_row_count(catalog.data_storage, dataset_table_name)

    catalog.remove_dataset(dogs_shadow_dataset.name)
    with pytest.raises(DatasetNotFoundError):
        catalog.data_storage.get_dataset(dogs_shadow_dataset.name)

    assert get_table_row_count(catalog.data_storage, dataset_table_name) is None


def test_edit_dataset(cloud_test_catalog, dogs_registered_dataset):
    dataset_new_name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog

    catalog.edit_dataset(
        dogs_registered_dataset.name,
        new_name=dataset_new_name,
        description="new description",
        labels=["cats", "birds"],
    )

    dataset = catalog.data_storage.get_dataset(dataset_new_name)
    assert dataset.versions_values == [1]
    assert dataset.name == dataset_new_name
    assert dataset.description == "new description"
    assert dataset.labels == ["cats", "birds"]


def test_edit_dataset_remove_labels_and_description(
    cloud_test_catalog, dogs_registered_dataset
):
    dataset_new_name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog

    catalog.edit_dataset(
        dogs_registered_dataset.name,
        new_name=dataset_new_name,
        description="",
        labels=[],
    )

    dataset = catalog.data_storage.get_dataset(dataset_new_name)
    assert dataset.versions_values == [1]
    assert dataset.name == dataset_new_name
    assert dataset.description == ""
    assert dataset.labels == []


def test_ls_dataset_rows(cloud_test_catalog, dogs_registered_dataset):
    catalog = cloud_test_catalog.catalog

    assert {
        r.name for r in catalog.ls_dataset_rows(dogs_registered_dataset.name, version=1)
    } == {
        "dog1",
        "dog2",
        "dog3",
        "dog4",
    }


def test_ls_dataset_rows_with_custom_columns(
    cloud_test_catalog, dogs_registered_dataset
):
    catalog = cloud_test_catalog.catalog
    dr = catalog.data_storage.dataset_rows(dogs_registered_dataset.id, 1)

    # additional columns added to dataset
    annotation_columns = [
        sa.Column("similarity", sa.Float(), default=0.5),
        sa.Column("pwatermark", sa.Float(), default=0.1),
    ]
    for c in annotation_columns:
        add_column(dr.engine, dr.table.name, c, catalog)

    # refresh catalog data storage to have newly inserted columns in
    # DatasetRow schema metadata
    catalog.data_storage = catalog.data_storage.clone()

    for r in catalog.ls_dataset_rows(
        dogs_registered_dataset.name, version=1, custom_columns=True
    ):
        assert r.custom == pytest.approx({"similarity": 0.5, "pwatermark": 0.1})


def test_merge_datasets_shadow_to_registered(
    cloud_test_catalog, dogs_registered_dataset, cats_shadow_dataset
):
    catalog = cloud_test_catalog.catalog
    catalog.merge_datasets(
        cats_shadow_dataset.name, dogs_registered_dataset.name, dst_version=2
    )

    dogs_dataset = catalog.data_storage.get_dataset(dogs_registered_dataset.name)
    assert dogs_dataset.versions_values == [1, 2]

    # making sure version 1 is not changed
    assert {
        r.name for r in catalog.ls_dataset_rows(dogs_registered_dataset.name, version=1)
    } == {
        "dog1",
        "dog2",
        "dog3",
        "dog4",
    }

    assert {
        r.name for r in catalog.ls_dataset_rows(dogs_registered_dataset.name, version=2)
    } == {
        "dog1",
        "dog2",
        "dog3",
        "dog4",
        "cat1",
        "cat2",
    }


def test_merge_datasets_registered_to_registered(
    cloud_test_catalog, dogs_registered_dataset, cats_registered_dataset
):
    catalog = cloud_test_catalog.catalog
    catalog.merge_datasets(
        cats_registered_dataset.name,
        dogs_registered_dataset.name,
        src_version=1,
        dst_version=2,
    )

    dogs_dataset = catalog.data_storage.get_dataset(dogs_registered_dataset.name)
    assert dogs_dataset.versions_values == [1, 2]

    assert {
        r.name for r in catalog.ls_dataset_rows(dogs_registered_dataset.name, version=2)
    } == {
        "dog1",
        "dog2",
        "dog3",
        "dog4",
        "cat1",
        "cat2",
    }


def test_merge_datasets_shadow_to_shadow(
    cloud_test_catalog, dogs_shadow_dataset, cats_shadow_dataset
):
    catalog = cloud_test_catalog.catalog
    catalog.merge_datasets(
        cats_shadow_dataset.name,
        dogs_shadow_dataset.name,
    )

    dogs_dataset = catalog.data_storage.get_dataset(dogs_shadow_dataset.name)
    assert dogs_dataset.shadow is True  # dataset stays shadow

    assert {r.name for r in catalog.ls_dataset_rows(dogs_shadow_dataset.name)} == {
        "dog1",
        "dog2",
        "dog3",
        "dog4",
        "cat1",
        "cat2",
    }


def test_merge_datasets_registered_to_shadow(
    cloud_test_catalog, dogs_shadow_dataset, cats_registered_dataset
):
    catalog = cloud_test_catalog.catalog
    catalog.merge_datasets(
        cats_registered_dataset.name,
        dogs_shadow_dataset.name,
        src_version=1,
    )

    dogs_dataset = catalog.data_storage.get_dataset(dogs_shadow_dataset.name)
    assert dogs_dataset.shadow is True  # dataset stays shadow

    assert {r.name for r in catalog.ls_dataset_rows(dogs_shadow_dataset.name)} == {
        "dog1",
        "dog2",
        "dog3",
        "dog4",
        "cat1",
        "cat2",
    }


def test_merge_datasets_shadow_to_empty_shadow_without_rows_table(
    cloud_test_catalog, empty_shadow_dataset, cats_shadow_dataset
):
    catalog = cloud_test_catalog.catalog
    catalog.merge_datasets(
        cats_shadow_dataset.name,
        empty_shadow_dataset.name,
    )

    empty_dataset = catalog.data_storage.get_dataset(empty_shadow_dataset.name)
    assert empty_dataset.shadow is True  # dataset stays shadow

    assert {r.name for r in catalog.ls_dataset_rows(empty_shadow_dataset.name)} == {
        "cat1",
        "cat2",
    }


def test_merge_datasets_empty_shadow_without_table_to_shadow(
    cloud_test_catalog, empty_shadow_dataset, cats_shadow_dataset
):
    catalog = cloud_test_catalog.catalog
    catalog.merge_datasets(
        empty_shadow_dataset.name,
        cats_shadow_dataset.name,
    )

    cat_dataset = catalog.data_storage.get_dataset(cats_shadow_dataset.name)
    assert cat_dataset.shadow is True  # dataset stays shadow

    assert {r.name for r in catalog.ls_dataset_rows(cats_shadow_dataset.name)} == {
        "cat1",
        "cat2",
    }


def to_str(buf) -> str:
    return io.TextIOWrapper(buf, encoding="utf8").read()


def test_loader_from_dataset(cloud_test_catalog, dogs_shadow_dataset):
    ctc = cloud_test_catalog

    def transform(row, sample):
        return sample, row.name[-1]

    ds = DataView.from_dataset(
        dogs_shadow_dataset.name,
        reader=to_str,
        transform=transform,
        catalog=ctc.catalog,
        client_config=ctc.client_config,
    )
    assert set(ds) == {("woof", "1"), ("arf", "2"), ("bark", "3"), ("ruff", "4")}


def test_loader_from_dataset_split(cloud_test_catalog, dogs_shadow_dataset):
    ctc = cloud_test_catalog

    def transform(row, sample):
        return sample, row.name[-1]

    N = 5
    all_data = []
    for i in range(N):
        ds = DataView.from_dataset(
            dogs_shadow_dataset.name,
            reader=to_str,
            transform=transform,
            num_workers=N,
            worker_id=i,
            catalog=ctc.catalog,
            client_config=ctc.client_config,
        )
        all_data.extend(ds)

    assert len(all_data) == 4
    assert set(all_data) == {("woof", "1"), ("arf", "2"), ("bark", "3"), ("ruff", "4")}


def test_dataset_row(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog
    data_storage = catalog.data_storage
    dr = data_storage.dataset_rows(dogs_shadow_dataset.id)
    first_id = next(data_storage.data_execute(sa.select(dr.c.id).limit(1)), (None,))[0]
    row = catalog.dataset_row(dogs_shadow_dataset.name, first_id)
    assert row.id == first_id


@pytest.mark.parametrize("tree", [{str(i): str(i) for i in range(50)}], indirect=True)
def test_row_random(cloud_test_catalog):
    # Note: this is technically a probabilistic test, but the probability
    # of accidental failure is < 1e-10
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.index([ctc.src_uri], client_config=ctc.client_config)
    catalog.create_shadow_dataset(
        "test", [ctc.src_uri], client_config=ctc.client_config
    )
    random_values = [row.random for row in catalog.ls_dataset_rows("test")]

    # Random values are unique
    assert len(set(random_values)) == len(random_values)

    RAND_MAX = 2**63
    # Values are drawn uniformly from range(2**63)
    assert 0 <= min(random_values) < 0.4 * RAND_MAX
    assert 0.6 * RAND_MAX < max(random_values) < RAND_MAX

    # Creating a new dataset preserves random values
    catalog.create_shadow_dataset(
        "test2", [ctc.src_uri], client_config=ctc.client_config
    )
    random_values2 = {row.random for row in catalog.ls_dataset_rows("test2")}
    assert random_values2 == set(random_values)


def test_create_shadow_dataset_from_storage(listed_bucket, cloud_test_catalog):
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    catalog.index([src_uri], client_config=cloud_test_catalog.client_config)

    shadow_dataset_name = uuid.uuid4().hex
    dataset = catalog.create_shadow_dataset(
        shadow_dataset_name,
        [f"{src_uri}/dogs/*"],
        client_config=cloud_test_catalog.client_config,
        recursive=True,
    )

    assert dataset.name == shadow_dataset_name
    assert dataset.status == DatasetStatus.COMPLETE
    assert dataset.sources == f"{src_uri}/dogs/*"
    assert dataset.query_script == ""


def test_dataset_stats_shadow_ds(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog
    stats = catalog.dataset_stats(dogs_shadow_dataset.name)
    assert stats.num_objects == 4
    assert stats.size == 15


def test_dataset_stats_registered_ds(cloud_test_catalog, dogs_registered_dataset):
    catalog = cloud_test_catalog.catalog
    stats = catalog.dataset_stats(dogs_registered_dataset.name, 1)
    assert stats.num_objects == 4
    assert stats.size == 15


def test_dataset_stats_missing_version(cloud_test_catalog, dogs_registered_dataset):
    catalog = cloud_test_catalog.catalog
    with pytest.raises(ValueError):
        catalog.dataset_stats(dogs_registered_dataset.name)


def test_dataset_meta_empty_custom_columns(cloud_test_catalog, dogs_registered_dataset):
    catalog = cloud_test_catalog.catalog
    meta = catalog.dataset_meta(dogs_registered_dataset.name, 1)
    assert meta.custom_column_types == []


def test_dataset_meta_with_custom_columns(cloud_test_catalog, dogs_registered_dataset):
    catalog = cloud_test_catalog.catalog
    dr = catalog.data_storage.dataset_rows(dogs_registered_dataset.id, 1)

    def _sort(custom_column_types):
        return sorted(custom_column_types, key=lambda c: c["name"])

    # additional columns added to dataset
    custom_columns = [
        sa.Column("col_integer", sa.Integer()),
        sa.Column("col_float", sa.Float()),
        sa.Column("col_string", sa.String()),
        sa.Column("col_json", sa.JSON()),
        sa.Column("col_boolean", sa.Boolean()),
    ]

    for c in custom_columns:
        add_column(dr.engine, dr.table.name, c, catalog)

    # refresh catalog data storage to have newly inserted columns in
    catalog.data_storage = catalog.data_storage.clone()

    meta = catalog.dataset_meta(dogs_registered_dataset.name, 1)
    assert _sort(meta.custom_column_types) == _sort(
        [
            {"name": "col_integer", "type": "int"},
            {"name": "col_float", "type": "float"},
            {"name": "col_string", "type": "str"},
            {"name": "col_json", "type": "dict"},
            {"name": "col_boolean", "type": "bool"},
        ]
    )


def test_dataset_meta_missing_version(cloud_test_catalog, dogs_registered_dataset):
    catalog = cloud_test_catalog.catalog
    with pytest.raises(ValueError):
        catalog.dataset_meta(dogs_registered_dataset.name)
