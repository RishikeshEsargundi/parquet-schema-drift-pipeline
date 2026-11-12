
import json

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from src import pipeline


def configure_test_directories(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    quarantine_dir = tmp_path / "quarantine"
    target_dir = tmp_path / "target"
    report_dir = tmp_path / "reports"

    for directory in [
        input_dir,
        output_dir,
        quarantine_dir,
        target_dir,
        report_dir,
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(pipeline, "INPUT_DIR", input_dir)
    monkeypatch.setattr(pipeline, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(pipeline, "QUARANTINE_DIR", quarantine_dir)
    monkeypatch.setattr(pipeline, "TARGET_DIR", target_dir)
    monkeypatch.setattr(pipeline, "REPORT_DIR", report_dir)

    return input_dir, target_dir, report_dir


def create_valid_batch(file_path):
    df = pd.DataFrame({
        "customer_id": [101, 102],
        "customer_name": ["Alice", "Bob"],
        "age": [25, 30],
        "email": ["alice@example.com", "bob@example.com"],
        "updated_at": pd.to_datetime(
            ["2026-01-01", "2026-01-02"],
            utc=True
        ),
        "city": ["Hyderabad", "Mumbai"],
        "salary": [30000.0, 40000.0],
    })

    df.to_parquet(file_path, index=False)


def test_empty_input_directory(tmp_path, monkeypatch):
    _, _, report_dir = configure_test_directories(
        tmp_path, monkeypatch
    )

    report = pipeline.run_pipeline()

    assert report["status"] == "SUCCESS_EMPTY"
    assert report["input_rows"] == 0
    assert report["published_rows"] == 0

    report_file = report_dir / f"{report['run_id']}.json"
    assert report_file.exists()

    saved_report = json.loads(
        report_file.read_text(encoding="utf-8")
    )

    assert saved_report["status"] == "SUCCESS_EMPTY"


def test_malformed_input_creates_failed_report(
    tmp_path, monkeypatch
):
    input_dir, _, report_dir = configure_test_directories(
        tmp_path, monkeypatch
    )

    malformed_file = input_dir / "broken.parquet"
    malformed_file.write_text(
        "This is not a Parquet file",
        encoding="utf-8"
    )

    with pytest.raises(Exception):
        pipeline.run_pipeline()

    report_files = list(report_dir.glob("*.json"))

    assert len(report_files) == 1

    report = json.loads(
        report_files[0].read_text(encoding="utf-8")
    )

    assert report["status"] == "FAILED"
    assert report["failure_reason"]


def test_successful_pipeline_publishes_records(
    tmp_path, monkeypatch
):
    input_dir, target_dir, report_dir = configure_test_directories(
        tmp_path, monkeypatch
    )

    create_valid_batch(input_dir / "batch_01.parquet")

    report = pipeline.run_pipeline()

    assert report["status"] == "SUCCESS"
    assert report["input_rows"] == 2
    assert report["valid_rows"] == 2
    assert report["rejected_rows"] == 0
    assert report["published_rows"] == 2

    target_file = target_dir / "customers.parquet"
    assert target_file.exists()

    published = pd.read_parquet(target_file)

    assert len(published) == 2
    assert published["customer_id"].is_unique

    report_file = report_dir / f"{report['run_id']}.json"
    assert report_file.exists()



def test_pipeline_recovers_after_malformed_input_is_fixed(
    tmp_path, monkeypatch
):
    input_dir, target_dir, report_dir = configure_test_directories(
        tmp_path, monkeypatch
    )

    input_file = input_dir / "batch_01.parquet"

    # First run: create a malformed input file.
    input_file.write_text(
        "Not a valid Parquet file",
        encoding="utf-8"
    )

    with pytest.raises(Exception):
        pipeline.run_pipeline()

    failed_reports = list(report_dir.glob("*.json"))
    assert len(failed_reports) == 1

    failed_report = json.loads(
        failed_reports[0].read_text(encoding="utf-8")
    )
    assert failed_report["status"] == "FAILED"

    # Repair the input file.
    input_file.unlink()
    create_valid_batch(input_file)

    # Second run: the pipeline should now succeed.
    successful_report = pipeline.run_pipeline()

    assert successful_report["status"] == "SUCCESS"
    assert successful_report["published_rows"] == 2

    target_file = target_dir / "customers.parquet"
    assert target_file.exists()

    published = pd.read_parquet(target_file)
    assert len(published) == 2
    assert published["customer_id"].is_unique

    # Both runs should have separate reports.
    all_reports = list(report_dir.glob("*.json"))
    assert len(all_reports) == 2
