import logging
import json
import os
import tempfile
import time
from pathlib import Path

import pandas as pd

from src import pipeline
from src import quarantine as quarantine_module


def generate_batch(batch_number, rows, output_dir):
    """Generate one synthetic Parquet batch."""

    start_id = (batch_number * rows) + 1

    df = pd.DataFrame({
        "customer_id": range(start_id, start_id + rows),
        "customer_name": [f"Customer_{i}" for i in range(rows)],
        "age": [25 + (i % 50) for i in range(rows)],
        "email": [f"customer_{i}@example.com" for i in range(rows)],
        "updated_at": pd.date_range(
            "2026-01-01",
            periods=rows,
            freq="s",
            tz="UTC"
        ),
    })

    if batch_number in [2, 3, 6, 7]:
        df["city"] = "Hyderabad"

    if batch_number in [3, 6, 7]:
        df["salary"] = 30000.0

    if batch_number == 4:
        # Breaking schema change: age becomes string.
        df["age"] = df["age"].astype(str)

    if batch_number == 5:
        # Breaking schema change: required ID is missing.
        df = df.drop(columns=["customer_id"])

    if batch_number == 7:
        # Inject a few invalid records.
        if rows >= 2:
            df.loc[df.index[0], "age"] = 10
            df.loc[df.index[1], "email"] = "invalid-email"

    file_path = output_dir / f"batch_{batch_number:02}.parquet"
    df.to_parquet(file_path, index=False)

    return file_path


def run_benchmark(rows_per_batch):
    """Run the pipeline in isolated temporary directories."""

    with tempfile.TemporaryDirectory(prefix="parquet_benchmark_") as temp:
        root = Path(temp)

        input_dir = root / "data" / "input"
        output_dir = root / "data" / "output"
        quarantine_dir = root / "data" / "quarantine"
        target_dir = root / "data" / "target"
        report_dir = root / "reports"

        for directory in [
            input_dir,
            output_dir,
            quarantine_dir,
            target_dir,
            report_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        # Save original pipeline directory settings.
        original_pipeline_paths = {
            "INPUT_DIR": pipeline.INPUT_DIR,
            "OUTPUT_DIR": pipeline.OUTPUT_DIR,
            "QUARANTINE_DIR": pipeline.QUARANTINE_DIR,
            "TARGET_DIR": pipeline.TARGET_DIR,
            "REPORT_DIR": pipeline.REPORT_DIR,
        }

        original_quarantine_dir = quarantine_module.QUARANTINE_DIR

        # Redirect pipeline paths into the temporary directory.
        pipeline.INPUT_DIR = input_dir
        pipeline.OUTPUT_DIR = output_dir
        pipeline.QUARANTINE_DIR = quarantine_dir
        pipeline.TARGET_DIR = target_dir
        pipeline.REPORT_DIR = report_dir

        quarantine_module.QUARANTINE_DIR = quarantine_dir
        # Generate seven batches.
        for batch_number in range(1, 8):
            generate_batch(batch_number, rows_per_batch, input_dir)

        # Redirect pipeline paths into the temporary directory.
        pipeline.INPUT_DIR = input_dir
        pipeline.OUTPUT_DIR = output_dir
        pipeline.QUARANTINE_DIR = quarantine_dir
        pipeline.TARGET_DIR = target_dir
        pipeline.REPORT_DIR = report_dir

        # Quarantine module has its own directory constant.
        quarantine_module.QUARANTINE_DIR = quarantine_dir

        # Logger uses a relative logs/ directory.
        previous_directory = Path.cwd()
        os.chdir(root)

        try:
            start = time.perf_counter()
            report = pipeline.run_pipeline()
            elapsed = time.perf_counter() - start

            input_files = list(input_dir.glob("*.parquet"))
            input_size = sum(
                file.stat().st_size for file in input_files
            )

            output_files = list(output_dir.glob("*.parquet"))
            output_files += list(quarantine_dir.glob("*.parquet"))
            output_files += list(target_dir.glob("*.parquet"))

            output_size = sum(
                file.stat().st_size for file in output_files
            )

            return {
                "rows_per_batch": rows_per_batch,
                "input_files": len(input_files),
                "input_rows": report["input_rows"],
                "valid_rows": report["valid_rows"],
                "rejected_rows": report["rejected_rows"],
                "schema_quarantined_rows": report[
                    "schema_quarantined_rows"
                ],
                "published_rows": report["published_rows"],
                "duration_seconds": round(elapsed, 3),
                "rows_per_second": round(
                    report["input_rows"] / elapsed, 2
                ) if elapsed else 0,
                "input_size_mb": round(input_size / (1024 ** 2), 2),
                "output_size_mb": round(output_size / (1024 ** 2), 2),
                "status": report["status"],
            }

        finally:
    # Close log handlers to release Windows file locks.
            logger = logging.getLogger("customer_pipeline")

            for handler in logger.handlers[:]:
                handler.flush()
                handler.close()
                logger.removeHandler(handler)

            # Restore original pipeline directories.
            for name, value in original_pipeline_paths.items():
                setattr(pipeline, name, value)

            quarantine_module.QUARANTINE_DIR = original_quarantine_dir

            # Restore the original working directory.
            os.chdir(previous_directory)          

def main():
    benchmark_sizes = [1_000, 10_000, 100_000]
    results = []

    for size in benchmark_sizes:
        print(f"\nBenchmarking {size:,} rows per batch...")

        result = run_benchmark(size)
        results.append(result)

        print(json.dumps(result, indent=2))

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    results_df = pd.DataFrame(results)

    csv_path = reports_dir / "benchmark_results.csv"
    json_path = reports_dir / "benchmark_results.json"

    results_df.to_csv(csv_path, index=False)

    json_path.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8"
    )

    print("\nBenchmark complete!")
    print(f"CSV report: {csv_path}")
    print(f"JSON report: {json_path}")

    print("\nPerformance summary:")
    print(results_df.to_string(index=False))


if __name__ == "__main__":
    main()
