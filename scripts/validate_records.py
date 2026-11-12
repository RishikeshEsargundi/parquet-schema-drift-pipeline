from pathlib import Path

import pandas as pd

from src.validator import validate_dataframe


OUTPUT_DIR = Path("data/output")
QUARANTINE_DIR = Path("data/quarantine")

RUN_ID = "run_001"


def main():

    QUARANTINE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    all_valid = []
    all_rejected = []

    files = sorted(
        OUTPUT_DIR.glob("batch_*.parquet")
    )

    for file_path in files:

        print("\n" + "=" * 50)
        print("Validating:", file_path.name)

        df = pd.read_parquet(file_path)

        valid, rejected = validate_dataframe(
            df,
            source_file=file_path.name,
            run_id=RUN_ID
        )

        all_valid.append(valid)
        all_rejected.append(rejected)

        print("Input rows:", len(df))
        print("Valid rows:", len(valid))
        print("Rejected rows:", len(rejected))

    # Combine results from all batches
    valid_df = pd.concat(
        all_valid,
        ignore_index=True
    ) if all_valid else pd.DataFrame()

    rejected_df = pd.concat(
        all_rejected,
        ignore_index=True
    ) if all_rejected else pd.DataFrame()

    # Save valid records
    valid_path = OUTPUT_DIR / "valid_customers.parquet"

    valid_df.to_parquet(
        valid_path,
        engine="pyarrow",
        index=False
    )

    # Save rejected records separately
    rejected_path = (
        QUARANTINE_DIR / "rejected_records.parquet"
    )

    rejected_df.to_parquet(
        rejected_path,
        engine="pyarrow",
        index=False
    )

    print("\n" + "=" * 50)
    print("DATA QUALITY SUMMARY")
    print("=" * 50)

    print("Total input rows:", len(valid_df) + len(rejected_df))
    print("Valid rows:", len(valid_df))
    print("Rejected rows:", len(rejected_df))

    print("\nRejection reasons:")

    if not rejected_df.empty:
        print(
            rejected_df["rejection_reason"]
            .value_counts()
        )

    print("\nValidation completed!")


if __name__ == "__main__":
    main()
