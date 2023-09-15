import pytest

from dql.cache import DQLCache, UniqueId

# pylint: disable=redefined-outer-name


@pytest.fixture
def cache(data_storage, tmp_path):
    data_storage.init_cache_table()
    return DQLCache(str(tmp_path / "cache"), str(tmp_path / "tmp"), data_storage)


def test_simple(cache):
    uid = UniqueId("s3://foo", "data", "bar", vtype="", location=None)
    data = b"foo"
    assert not cache.get_checksum(uid)

    checksum = cache.store_data(data)
    assert cache.exists(checksum)
    assert not cache.get_checksum(uid)
    assert not cache.contains(uid)

    cache.set_checksum(uid, checksum)
    assert cache.get_checksum(uid) == checksum
    assert cache.contains(uid)

    with open(cache.get_path(uid), mode="rb") as f:
        assert f.read() == data

    cache.clear()
    assert not cache.exists(checksum)
    assert not cache.get_checksum(uid)
