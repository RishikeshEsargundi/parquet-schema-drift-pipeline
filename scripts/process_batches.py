
from pathlib import Path

import pandas as pd

from src.schema_detector import inspect_parquet_file
from src.transformer import transform_parquet_file
from src.quarantine import quarantine_file


INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/output")


def process_batches():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    files = sorted(INPUT_DIR.glob("*.parquet"))

    accepted_count = 0
    quarantined_count = 0

    for file_path in files:

        print("\n" + "=" * 60)
        print(f"Processing: {file_path.name}")

        schema_report = inspect_parquet_file(file_path)

        if schema_report["status"] == "INCOMPATIBLE":

            quarantine_file(
                file_path,
                schema_report
            )

            quarantined_count += 1
            continue

        transformed_df = transform_parquet_file(file_path)

        output_path = OUTPUT_DIR / file_path.name

        transformed_df.to_parquet(
            output_path,
            engine="pyarrow",
            index=False
        )

        print(f"ACCEPTED: {file_path.name}")
        print(f"Output rows: {len(transformed_df)}")

        accepted_count += 1

    print("\n" + "=" * 60)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 60)

    print(f"Total input files: {len(files)}")
    print(f"Accepted batches: {accepted_count}")
    print(f"Quarantined batches: {quarantined_count}")


if __name__ == "__main__":
    process_batches()
