
from pathlib import Path

import pandas as pd

from src.publisher import publish_customer_snapshot


VALID_DATA_PATH = Path(
    "data/output/valid_customers.parquet"
)

TARGET_PATH = Path(
    "data/target/customers.parquet"
)


def main():

    if not VALID_DATA_PATH.exists():
        raise FileNotFoundError(
            "Run record validation before publishing."
        )

    valid_df = pd.read_parquet(VALID_DATA_PATH)

    print("Input valid records:", len(valid_df))

    published_df, duplicates_removed = (
        publish_customer_snapshot(
            valid_records=valid_df,
            target_path=TARGET_PATH
        )
    )

    print("\nPUBLISHING SUMMARY")
    print("------------------")

    print("Input records:", len(valid_df))
    print("Duplicates removed:", duplicates_removed)
    print("Published records:", len(published_df))
    print("Target file:", TARGET_PATH)

    print(
        "Unique customer IDs:",
        published_df["customer_id"].nunique()
    )


if __name__ == "__main__":
    main()
