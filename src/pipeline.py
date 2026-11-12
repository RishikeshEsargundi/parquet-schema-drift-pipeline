import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from src.schema_detector import inspect_parquet_file
from src.transformer import transform_parquet_file
from src.validator import validate_dataframe
from src.quarantine import quarantine_file
from src.publisher import publish_customer_snapshot
from src.logger import setup_logger


INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/output")
QUARANTINE_DIR = Path("data/quarantine")
TARGET_DIR = Path("data/target")
REPORT_DIR = Path("reports")


def utc_now():
    """Return current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def save_report(report, report_path):
    """Write execution metrics as JSON."""
    report_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
            default=str
        )


def run_pipeline():

    run_id = f"run_{uuid.uuid4().hex[:12]}"
    start = time.perf_counter()

    logger = setup_logger(run_id)

    for directory in [
        OUTPUT_DIR,
        QUARANTINE_DIR,
        TARGET_DIR,
        REPORT_DIR
    ]:
        directory.mkdir(
            parents=True,
            exist_ok=True
        )

    report = {
        "run_id": run_id,
        "start_time": utc_now(),
        "end_time": None,
        "duration_seconds": None,
        "status": "RUNNING",
        "input_files": 0,
        "input_rows": 0,
        "accepted_batches": 0,
        "quarantined_batches": 0,
        "schema_quarantined_rows": 0,
        "valid_rows": 0,
        "rejected_rows": 0,
        "published_rows": 0,
        "failure_reason": None,
        "files": []
    }

    report_path = REPORT_DIR / f"{run_id}.json"

    try:
        logger.info("Pipeline started: %s", run_id)

        files = sorted(INPUT_DIR.glob("*.parquet"))
        report["input_files"] = len(files)

        if not files:
            logger.warning("No input files found")
            report["status"] = "SUCCESS_EMPTY"
            return report

        all_valid = []
        all_rejected = []

        for file_path in files:

            logger.info("Processing: %s", file_path.name)

            # Read row count from Parquet metadata
            parquet_metadata = pq.read_metadata(file_path)
            row_count = parquet_metadata.num_rows

            report["input_rows"] += row_count

            schema_report = inspect_parquet_file(
                file_path
            )

            if schema_report["status"] == "INCOMPATIBLE":

                quarantine_file(
                    file_path,
                    schema_report
                )

                report["quarantined_batches"] += 1
                report["schema_quarantined_rows"] += row_count

                report["files"].append({
                    "source_file": file_path.name,
                    "status": "QUARANTINED",
                    "input_rows": row_count,
                    "reason": schema_report
                })

                logger.warning(
                    "Schema quarantine: %s",
                    file_path.name
                )

                continue

            # Transform compatible batch
            df = transform_parquet_file(file_path)

            # Validate individual records
            valid, rejected = validate_dataframe(
                df,
                source_file=file_path.name,
                run_id=run_id
            )

            all_valid.append(valid)
            all_rejected.append(rejected)

            report["accepted_batches"] += 1
            report["valid_rows"] += len(valid)
            report["rejected_rows"] += len(rejected)

            report["files"].append({
                "source_file": file_path.name,
                "status": "ACCEPTED",
                "input_rows": row_count,
                "valid_rows": len(valid),
                "rejected_rows": len(rejected)
            })

            logger.info(
                "%s: valid=%d rejected=%d",
                file_path.name,
                len(valid),
                len(rejected)
            )

        # Combine all accepted batch results
        valid_df = (
            pd.concat(all_valid, ignore_index=True)
            if all_valid
            else pd.DataFrame()
        )

        rejected_df = (
            pd.concat(all_rejected, ignore_index=True)
            if all_rejected
            else pd.DataFrame()
        )

        # Save per-run rejected records
        if not rejected_df.empty:
            rejected_df.to_parquet(
                QUARANTINE_DIR /
                f"rejected_records_{run_id}.parquet",
                index=False
            )

        # Publish consolidated target
        if not valid_df.empty:

            valid_df.to_parquet(
                OUTPUT_DIR /
                f"valid_customers_{run_id}.parquet",
                index=False
            )

            published_df, duplicates_removed = (
                publish_customer_snapshot(
                    valid_df,
                    TARGET_DIR / "customers.parquet"
                )
            )

            report["published_rows"] = len(published_df)
            report["cross_batch_duplicates"] = (
                duplicates_removed
            )

        else:
            report["cross_batch_duplicates"] = 0

            raise ValueError(
            "No valid records available. "
            "Existing target was not modified."
            )

        # Reconciliation
        accounted_rows = (
            report["schema_quarantined_rows"]
            + report["valid_rows"]
            + report["rejected_rows"]
        )

        if accounted_rows != report["input_rows"]:
            raise AssertionError(
                "Input row reconciliation failed"
            )

        if (
            report["quarantined_batches"] > 0
            or report["rejected_rows"] > 0
        ):
            report["status"] = "SUCCESS_WITH_REJECTS"
        else:
            report["status"] = "SUCCESS"

        logger.info(
            "Published records: %d",
            report["published_rows"]
        )

        logger.info(
            "Pipeline status: %s",
            report["status"]
        )

    except Exception as error:

        report["status"] = "FAILED"
        report["failure_reason"] = str(error)

        logger.exception(
            "Pipeline failed: %s",
            error
        )

        raise

    finally:

        report["end_time"] = utc_now()
        report["duration_seconds"] = round(
            time.perf_counter() - start,
            3
        )

        save_report(report, report_path)

        logger.info(
            "Execution duration: %.3f seconds",
            report["duration_seconds"]
        )

        logger.info(
            "Report saved: %s",
            report_path
        )

    return report


if __name__ == "__main__":
    run_pipeline()
