from pathlib import Path

import os
import pandas as pd


def publish_customer_snapshot(
    valid_records,
    target_path
):
    """
    Publish the latest valid record for each customer.

    Publishing strategy:
    - customer_id is the business key.
    - Latest updated_at wins.
    - Ties are resolved deterministically.
    - Existing target is replaced, not appended.
    """

    target_path = Path(target_path)
    target_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df = valid_records.copy()

    if df.empty:
        raise ValueError(
            "Cannot publish an empty customer dataset."
        )

    # Required fields for deterministic publishing
    required_columns = {
        "customer_id",
        "updated_at",
        "source_file",
        "source_row"
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing publishing columns: {sorted(missing)}"
        )

    # Primary key must not be NULL
    if df["customer_id"].isna().any():
        raise ValueError(
            "Cannot publish records with NULL customer_id."
        )

    # Normalize timestamps
    df["updated_at"] = pd.to_datetime(
        df["updated_at"],
        errors="raise",
        utc=True
    )

    # Sort records deterministically.
    # Latest timestamp wins.
    # For timestamp ties, source filename and row decide.
    df = df.sort_values(
        [
            "customer_id",
            "updated_at",
            "source_file",
            "source_row"
        ],
        ascending=[True, True, True, True],
        kind="stable"
    )

    input_count = len(df)

    # Keep the latest record for each customer
    df = df.drop_duplicates(
        subset=["customer_id"],
        keep="last"
    )

    duplicate_count = input_count - len(df)

    # Final deterministic output order
    df = df.sort_values(
        "customer_id",
        kind="stable"
    ).reset_index(drop=True)

    # Final uniqueness assertion
    if df["customer_id"].duplicated().any():
        raise AssertionError(
            "Duplicate customer IDs found in target."
        )

    # Write to temporary file first
    temp_path = target_path.with_name(
        target_path.stem + ".tmp.parquet"
    )

    try:
        df.to_parquet(
            temp_path,
            engine="pyarrow",
            index=False
        )

        # Replace target only after successful write
        os.replace(temp_path, target_path)

    finally:
        # Clean up temporary file after failure
        if temp_path.exists():
            temp_path.unlink()

    return df, duplicate_count
