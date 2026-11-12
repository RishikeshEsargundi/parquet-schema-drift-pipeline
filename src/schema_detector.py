
import pyarrow as pa
import pyarrow.parquet as pq

BASELINE_COLUMNS = {
    "customer_id",
    "customer_name",
    "age",
    "email",
    "updated_at"
}

# Approved target schema
TARGET_SCHEMA = {
    "customer_id": "int64",
    "customer_name": "string",
    "age": "int64",
    "email": "string",
    "updated_at": "timestamp",
    "city": "string",
    "salary": "float64"
}


# Required columns
REQUIRED_COLUMNS = {
    "customer_id",
    "customer_name",
    "age",
    "email",
    "updated_at"
}


# Optional columns
OPTIONAL_COLUMNS = {
    "city",
    "salary"
}


def normalize_type(arrow_type):
    """
    Convert PyArrow types into our canonical type names.
    """

    if pa.types.is_string(arrow_type) or pa.types.is_large_string(arrow_type):
        return "string"

    if pa.types.is_int64(arrow_type):
        return "int64"

    if pa.types.is_float64(arrow_type):
        return "float64"

    if pa.types.is_timestamp(arrow_type):
        return "timestamp"

    if pa.types.is_null(arrow_type):
        return "null"

    return str(arrow_type)


def get_incoming_schema(file_path):
    """
    Read the schema directly from a Parquet file.
    Does not load all records into memory.
    """

    parquet_file = pq.ParquetFile(file_path)

    schema = parquet_file.schema_arrow

    return {
        field.name: normalize_type(field.type)
        for field in schema
    }


def detect_schema_drift(incoming_schema):
    """
    Compare incoming schema against approved target schema.
    """

    incoming_columns = set(incoming_schema.keys())
    target_columns = set(TARGET_SCHEMA.keys())

    added_columns = incoming_columns - BASELINE_COLUMNS
    unapproved_columns = incoming_columns - target_columns
    missing_columns = target_columns - incoming_columns

    missing_required = missing_columns & REQUIRED_COLUMNS
    missing_optional = missing_columns & OPTIONAL_COLUMNS

    type_changes = {}

    for column in incoming_columns & target_columns:

        expected_type = TARGET_SCHEMA[column]
        actual_type = incoming_schema[column]

        if actual_type != expected_type:
            type_changes[column] = {
                "expected": expected_type,
                "actual": actual_type
            }

    is_compatible = (
        len(unapproved_columns) == 0
        and len(missing_required) == 0
        and len(type_changes) == 0
    )

    return {
        "status": "COMPATIBLE" if is_compatible else "INCOMPATIBLE",
        "added_columns": sorted(added_columns),
        "missing_required_columns": sorted(missing_required),
        "missing_optional_columns": sorted(missing_optional),
        "type_changes": type_changes,
        "unapproved_columns": sorted(unapproved_columns)
    }


def inspect_parquet_file(file_path):
    """
    Complete schema inspection for one Parquet file.
    """

    incoming_schema = get_incoming_schema(file_path)

    report = detect_schema_drift(incoming_schema)

    report["file_name"] = str(file_path)
    report["incoming_schema"] = incoming_schema

    return report
