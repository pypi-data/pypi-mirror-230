import re

import pytest
from sqlalchemy import literal, select
from sqlalchemy.sql import func as f

from dql.sql.functions import path as sql_path

PATHS = ["", "/", "name", "/name", "name/", "some/long/path"]


def split_parent(path):
    parent, name = f"/{path}".rsplit("/", 1)
    return parent[1:], name


@pytest.mark.parametrize("func_base", [f.path, sql_path])
@pytest.mark.parametrize("func_name", ["parent", "name"])
def test_default_not_implement(func_base, func_name):
    """
    Importing dql.sql.functions.path should register a custom compiler
    which raises an exception for these functions with the default
    SQLAlchemy dialect.
    """
    fn = getattr(func_base, func_name)
    expr = fn(literal("file:///some/file/path"))
    with pytest.raises(NotImplementedError, match=re.escape(f"path.{func_name}")):
        expr.compile()


@pytest.mark.parametrize("path", PATHS)
def test_parent(data_storage, path):
    query = select(f.path.parent(literal(path)))
    result = tuple(data_storage.data_execute(query))
    assert result == ((split_parent(path)[0],),)


@pytest.mark.parametrize("path", PATHS)
def test_name(data_storage, path):
    query = select(f.path.name(literal(path)))
    result = tuple(data_storage.data_execute(query))
    assert result == ((split_parent(path)[1],),)
