import io

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from dql.client import Client
from dql.client.fileslice import FileSlice

from ..utils import uppercase_scheme


def test_bad_url():
    bucket = "whatever"
    path = "my/path"
    with pytest.raises(RuntimeError):
        Client.parse_url(bucket + "/" + path + "/", None, None)


non_null_text = st.text(
    alphabet=st.characters(blacklist_categories=("Cc", "Cs")), min_size=1
)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(rel_path=non_null_text)
def test_parse_url(cloud_test_catalog, rel_path):
    bucket_uri = cloud_test_catalog.src_uri
    url = f"{bucket_uri}/{rel_path}"
    catalog = cloud_test_catalog.catalog
    client, rel_part = catalog.parse_url(url, **cloud_test_catalog.client_config)
    assert client.uri == bucket_uri
    assert rel_part == rel_path


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(rel_path=non_null_text)
def test_parse_url_uppercase_scheme(cloud_test_catalog, rel_path):
    bucket_uri = cloud_test_catalog.src_uri
    bucket_uri_upper = uppercase_scheme(bucket_uri)
    url = f"{bucket_uri_upper}/{rel_path}"
    catalog = cloud_test_catalog.catalog
    client, rel_part = catalog.parse_url(url, **cloud_test_catalog.client_config)
    assert client.uri == bucket_uri
    assert rel_part == rel_path


def test_FileSlice():
    data = b"0123456789abcdef"
    base = io.BytesIO(data)
    f = FileSlice(base, 5, 5, "foo")
    assert base.tell() == 0
    assert f.readable()
    assert not f.writable()
    assert f.seekable()
    assert f.name == "foo"

    # f.seek() doesn't move the underlying stream
    f.seek(0)
    assert f.tell() == 0
    assert base.tell() == 0

    assert f.read(3) == data[5:8]
    assert f.tell() == 3
    assert base.tell() == 8

    assert f.read(4) == data[8:10]
    assert f.tell() == 5
    assert base.tell() == 10

    b = bytearray(5)
    f.seek(0)
    f.readinto(b)
    assert b == data[5:10]


def test_bad_FileSlice():
    data = b"0123456789abcdef"
    base = io.BytesIO(data)
    f = FileSlice(base, 10, 10, "foo")
    assert f.read(4) == data[10:14]
    with pytest.raises(RuntimeError):
        f.read()
