from sqlalchemy import JSON, Column, Float
from sqlalchemy.dialects.sqlite import dialect as sqlite_dialect
from sqlalchemy.schema import CreateTable

from dql.data_storage.schema import DatasetRow


def test_dataset_table_compilation():
    table = DatasetRow.new_table(
        "ds-1",
        custom_columns=[
            Column("score", Float, nullable=False),
            Column("meta_info", JSON),
        ],
    )
    result = CreateTable(table, if_not_exists=True).compile(dialect=sqlite_dialect())

    assert result.string == (
        "\n"
        'CREATE TABLE IF NOT EXISTS "ds-1" (\n'
        "\tid INTEGER NOT NULL, \n"
        "\tvtype TEXT NOT NULL, \n"
        "\tdir_type INTEGER, \n"
        "\tparent_id INTEGER, \n"
        "\tparent TEXT, \n"
        "\tname TEXT NOT NULL, \n"
        "\tchecksum TEXT, \n"
        "\tetag TEXT, \n"
        "\tversion TEXT, \n"
        "\tis_latest BOOLEAN, \n"
        "\tlast_modified DATETIME, \n"
        "\tsize BIGINT NOT NULL, \n"
        "\towner_name TEXT, \n"
        "\towner_id TEXT, \n"
        "\tanno JSON, \n"
        "\trandom BIGINT NOT NULL, \n"
        "\tlocation JSON, \n"
        "\tsource TEXT NOT NULL, \n"
        "\tscore FLOAT NOT NULL, \n"
        "\tmeta_info JSON, \n"
        "\tPRIMARY KEY (id)\n"
        ")\n"
        "\n"
    )
