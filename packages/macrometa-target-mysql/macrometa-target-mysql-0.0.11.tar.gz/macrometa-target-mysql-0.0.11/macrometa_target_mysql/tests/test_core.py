""" Attempt at making some standard Target Tests. """
import io
import json

# flake8: noqa
import os
from contextlib import redirect_stdout
from pathlib import Path

import pytest
import sqlalchemy
from jsonschema.exceptions import ValidationError
from singer_sdk.exceptions import (
    MissingKeyPropertiesError,
    RecordsWithoutSchemaException,
)
from sqlalchemy import create_engine

from macrometa_target_mysql.target import MacrometaTargetMySQL

parent_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../tests/")
)
config_path = os.path.join(parent_directory, "config.json")

with open(config_path, "r") as f:
    config_data: dict = json.load(f)


@pytest.fixture()
def mysql_config():
    return config_data


@pytest.fixture
def mysql_target(mysql_config) -> MacrometaTargetMySQL:
    return MacrometaTargetMySQL(config=mysql_config)


def singer_file_to_target(file_name, target) -> None:
    """Singer file to Target, emulates a tap run
    Equivalent to running cat file_path | target-name --config config.json.
    Note that this function loads all lines into memory, so it is
    not good very large files.
    Args:
        file_name: name to file in .tests/data_files to be sent into target
        target: Target to pass data from file_path into..
    """
    file_path = Path(__file__).parent / Path("./data_files") / Path(file_name)
    buf = io.StringIO()
    with redirect_stdout(buf):
        with open(file_path, "r") as f:
            for line in f:
                print(line.rstrip("\r\n"))  # File endings are here,
                # and print adds another line ending so we need to remove one.
    buf.seek(0)
    target.listen(buf)


def get_engine():
    connection_url = sqlalchemy.engine.url.URL.create(
        drivername="mysql",
        username=config_data["user"],
        password=config_data["password"],
        host=config_data["host"],
        port=config_data["port"],
        database=config_data["database"],
    )

    engine = create_engine(connection_url)

    return engine


def get_row_count(table_name):
    engine = get_engine()
    rowcount = engine.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    return rowcount


def get_table_cols(table_name):
    engine = get_engine()
    q = f"""
    SELECT COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA='{config_data["database"]}'
    AND TABLE_NAME='{table_name}'
    ORDER BY ORDINAL_POSITION;
    """
    columns = [col[0] for col in engine.execute(q).fetchall()]
    return columns


def drop_table(table_name):
    engine = get_engine()
    engine.execute(f"DROP TABLE if exists {table_name}")


# this test should throw an exception
def test_record_before_schema(mysql_target):
    with pytest.raises(RecordsWithoutSchemaException) as e_info:
        file_name = "record_before_schema.singer"
        singer_file_to_target(file_name, mysql_target)


# this test should throw an exception
def test_invalid_schema(mysql_target):
    with pytest.raises(Exception) as e_info:
        file_name = "invalid_schema.singer"
        singer_file_to_target(file_name, mysql_target)


# this test should throw an exception
def test_record_missing_key_property(mysql_target):
    with pytest.raises(Exception) as e_info:
        file_name = "record_missing_key_property.singer"
        singer_file_to_target(file_name, mysql_target)


# this test should throw an exception
def test_record_missing_required_property(mysql_target):
    with pytest.raises(Exception) as e_info:
        file_name = "record_missing_required_property.singer"
        singer_file_to_target(file_name, mysql_target)


# test that data is correctly set
# @pytest.mark.skip(reason="Waiting for SDK to handle this")
def test_special_chars_in_attributes(mysql_target):
    with pytest.raises(MissingKeyPropertiesError) as e_info:
        file_name = "special_chars_in_attributes.singer"
        singer_file_to_target(file_name, mysql_target)


# test that data is correctly set
def test_optional_attributes(mysql_target):
    file_name = "optional_attributes.singer"
    singer_file_to_target(file_name, mysql_target)


def test_schema_no_properties(mysql_target):
    file_name = "schema_no_properties.singer"
    singer_file_to_target(file_name, mysql_target)


# test that data is correct
def test_multiple_state_messages(mysql_target):
    file_name = "multiple_state_messages.singer"
    singer_file_to_target(file_name, mysql_target)


def test_relational_data(mysql_target):
    file_name = "user_location_data.singer"
    singer_file_to_target(file_name, mysql_target)

    file_name = "user_location_upsert_data.singer"
    singer_file_to_target(file_name, mysql_target)


# test that data is correct
def test_no_primary_keys(mysql_target):
    file_name = "no_primary_keys.singer"
    singer_file_to_target(file_name, mysql_target)

    file_name = "no_primary_keys_append.singer"
    singer_file_to_target(file_name, mysql_target)


# test that data is correct
def test_duplicate_records(mysql_target):
    file_name = "duplicate_records.singer"
    singer_file_to_target(file_name, mysql_target)


# test that data is correct
def test_update_records(mysql_target):
    file_name = "update_records.singer"
    singer_file_to_target(file_name, mysql_target)


def test_array_data(mysql_target):
    file_name = "array_data.singer"
    singer_file_to_target(file_name, mysql_target)


def test_encoded_string_data(mysql_target):
    file_name = "encoded_strings.singer"
    singer_file_to_target(file_name, mysql_target)


@pytest.mark.skip(reason="Something about objects not supported")
def test_tap_appl(mysql_target):
    file_name = "tap_aapl.singer"
    singer_file_to_target(file_name, mysql_target)


def test_missing_value(mysql_target):
    file_name = "missing_value.singer"
    singer_file_to_target(file_name, mysql_target)


def test_large_int(mysql_target):
    file_name = "large_int.singer"
    singer_file_to_target(file_name, mysql_target)


def test_db_schema(mysql_target):
    file_name = "target_schema.singer"
    singer_file_to_target(file_name, mysql_target)


def test_illegal_colnames(mysql_target):
    with pytest.raises(MissingKeyPropertiesError) as e_info:
        file_name = "illegal_colnames.singer"
        singer_file_to_target(file_name, mysql_target)


def test_numerics(mysql_target):
    file_name = "numerics.singer"
    singer_file_to_target(file_name, mysql_target)
