import pandas as pd
import re


def validate_dataframe(
    df,
    source_file,
    run_id="manual_run"
):
    """
    Validate customer records.

    Returns:
        valid_records: Records that pass all checks.
        rejected_records: Records with rejection reasons.
    """

    df = df.copy().reset_index(drop=True)

    # Preserve original row position for traceability
    df["source_row"] = range(1, len(df) + 1)
    df["source_file"] = source_file
    df["run_id"] = run_id

    # Store all rejection reasons for each row
    reasons = [[] for _ in range(len(df))]

    # 1. Validate customer_id
    invalid_id = df["customer_id"].isna()

    for idx in df.index[invalid_id]:
        reasons[idx].append("missing_customer_id")

    # 2. Validate customer_name
    invalid_name = (
        df["customer_name"].isna()
        | df["customer_name"].astype("string").str.strip().eq("").fillna(True)
    )

    for idx in df.index[invalid_name]:
        reasons[idx].append("missing_customer_name")

    # 3. Validate age
    age = pd.to_numeric(df["age"], errors="coerce")

    invalid_age = (
        age.isna()
        | ~age.between(18, 100).fillna(False)
    )

    for idx in df.index[invalid_age]:
        reasons[idx].append("invalid_age")

    # 4. Validate email
    email = df["email"].astype("string").str.strip()

    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    invalid_email = (
        email.isna()
        | ~email.str.fullmatch(email_pattern, na=False)
    )

    for idx in df.index[invalid_email]:
        reasons[idx].append("invalid_email")

    # 5. Validate updated_at
    timestamps = pd.to_datetime(
        df["updated_at"],
        errors="coerce",
        utc=True
    )

    invalid_timestamp = timestamps.isna()

    for idx in df.index[invalid_timestamp]:
        reasons[idx].append("invalid_updated_at")

    # 6. Validate salary
    salary = pd.to_numeric(
        df["salary"],
        errors="coerce"
    )

    invalid_salary = (
        df["salary"].notna()
        & (salary.isna() | (salary < 0).fillna(False))
    )

    for idx in df.index[invalid_salary]:
        reasons[idx].append("invalid_salary")

    # 7. Handle duplicate customer IDs.
    # Keep the latest updated_at.
    # For timestamp ties, keep the later source row.

    duplicate_candidates = df.loc[
        df["customer_id"].notna(),
        ["customer_id"]
    ].copy()

    duplicate_candidates["parsed_timestamp"] = timestamps.loc[
        duplicate_candidates.index
    ]

    duplicate_candidates["source_order"] = duplicate_candidates.index

    ordered = duplicate_candidates.sort_values(
        ["parsed_timestamp", "source_order"],
        ascending=[True, True],
        na_position="first",
        kind="stable"
    )

    duplicate_indices = ordered.index[
        ordered.duplicated(
            subset=["customer_id"],
            keep="last"
        )
    ]

    for idx in duplicate_indices:
        reasons[idx].append("duplicate_customer_id")

    # Build valid and rejected datasets
    rejected_mask = pd.Series(
        [len(reason) > 0 for reason in reasons],
        index=df.index
    )

    valid_records = df.loc[~rejected_mask].copy()

    rejected_records = df.loc[rejected_mask].copy()

    rejected_records["rejection_reason"] = [
        ";".join(reasons[idx])
        for idx in rejected_records.index
    ]

    return valid_records, rejected_records
