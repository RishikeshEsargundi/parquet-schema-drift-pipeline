
import pandas as pd

from src.schema_detector import (
    TARGET_SCHEMA,
    inspect_parquet_file
)


# Fixed order for all target columns
TARGET_COLUMNS = list(TARGET_SCHEMA.keys())


def normalize_dataframe(df):
    """
    Add missing optional columns, normalize data types,
    and arrange columns in target schema order.
    """

    df = df.copy()

    # Add missing optional columns as NULL
    for column in TARGET_COLUMNS:

        if column not in df.columns:

            df[column] = pd.NA

    # Normalize data types
    df["customer_id"] = pd.to_numeric(
        df["customer_id"],
        errors="raise"
    ).astype("Int64")

    df["customer_name"] = df["customer_name"].astype("string")

    df["age"] = pd.to_numeric(
        df["age"],
        errors="raise"
    ).astype("Int64")

    df["email"] = df["email"].astype("string")

    df["city"] = df["city"].astype("string")

    df["salary"] = pd.to_numeric(
        df["salary"],
        errors="raise"
    ).astype("Float64")

    df["updated_at"] = pd.to_datetime(
        df["updated_at"],
        errors="raise",
        utc=True
    )

    # Keep columns in consistent order
    df = df[TARGET_COLUMNS]

    return df


def transform_parquet_file(file_path):
    """
    Read and transform a compatible Parquet file.
    Reject incompatible schemas before transformation.
    """

    schema_report = inspect_parquet_file(file_path)

    if schema_report["status"] != "COMPATIBLE":
        raise ValueError(
            f"Incompatible schema: {schema_report}"
        )

    df = pd.read_parquet(file_path, engine="pyarrow")

    transformed_df = normalize_dataframe(df)

    return transformed_df
