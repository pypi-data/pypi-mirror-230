import pytest

from dql.cache import DQLCache, UniqueId

# pylint: disable=redefined-outer-name


@pytest.fixture
def cache(tmp_path):
    return DQLCache(str(tmp_path / "cache"), str(tmp_path / "tmp"))


def test_simple(cache):
    uid = UniqueId("s3://foo", "data", "bar", vtype="", location=None)
    data = b"foo"
    assert not cache.contains(uid)

    cache.store_data(uid, data)
    assert cache.contains(uid)
    with open(cache.get_path(uid), mode="rb") as f:
        assert f.read() == data

    cache.clear()
    assert not cache.contains(uid)
