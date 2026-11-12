
import pandas as pd

from src.schema_detector import (
    detect_schema_drift,
    inspect_parquet_file
)


def test_original_schema_is_compatible():

    schema = {
        "customer_id": "int64",
        "customer_name": "string",
        "age": "int64",
        "email": "string",
        "updated_at": "timestamp"
    }

    result = detect_schema_drift(schema)

    assert result["status"] == "COMPATIBLE"
    assert result["missing_required_columns"] == []


def test_approved_new_column_is_compatible():

    schema = {
        "customer_id": "int64",
        "customer_name": "string",
        "age": "int64",
        "email": "string",
        "updated_at": "timestamp",
        "city": "string"
    }

    result = detect_schema_drift(schema)

    assert result["status"] == "COMPATIBLE"
    assert result["added_columns"] == ["city"]


def test_multiple_approved_columns_are_compatible():

    schema = {
        "customer_id": "int64",
        "customer_name": "string",
        "age": "int64",
        "email": "string",
        "updated_at": "timestamp",
        "city": "string",
        "salary": "float64"
    }

    result = detect_schema_drift(schema)

    assert result["status"] == "COMPATIBLE"


def test_changed_age_type_is_incompatible():

    schema = {
        "customer_id": "int64",
        "customer_name": "string",
        "age": "string",
        "email": "string",
        "updated_at": "timestamp"
    }

    result = detect_schema_drift(schema)

    assert result["status"] == "INCOMPATIBLE"

    assert result["type_changes"]["age"] == {
        "expected": "int64",
        "actual": "string"
    }


def test_missing_required_column_is_incompatible():

    schema = {
        "customer_name": "string",
        "age": "int64",
        "email": "string",
        "updated_at": "timestamp"
    }

    result = detect_schema_drift(schema)

    assert result["status"] == "INCOMPATIBLE"

    assert "customer_id" in result["missing_required_columns"]


def test_unknown_column_is_incompatible():

    schema = {
        "customer_id": "int64",
        "customer_name": "string",
        "age": "int64",
        "email": "string",
        "updated_at": "timestamp",
        "country_code": "string"
    }

    result = detect_schema_drift(schema)

    assert result["status"] == "INCOMPATIBLE"
    assert result["unapproved_columns"] == ["country_code"]


def test_malformed_parquet_file_raises_error(tmp_path):

    bad_file = tmp_path / "broken.parquet"
    bad_file.write_text(
        "This is not a valid Parquet file"
    )

    try:
        inspect_parquet_file(bad_file)
    except Exception:
        pass
    else:
        raise AssertionError(
            "Malformed Parquet should raise an error"
        )
