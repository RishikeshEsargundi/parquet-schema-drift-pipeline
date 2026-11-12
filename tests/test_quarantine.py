
import json

import pyarrow as pa
import pyarrow.parquet as pq

from src.quarantine import quarantine_file


def test_quarantine_preserves_original_file(tmp_path, monkeypatch):
    # Create a temporary input Parquet file.
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    input_file = input_dir / "batch_04.parquet"

    table = pa.table({
        "customer_id": [101, 102],
        "age": ["twenty-five", "thirty"],
    })

    pq.write_table(table, input_file)

    original_bytes = input_file.read_bytes()

    # Redirect quarantine output to the temporary directory.
    quarantine_dir = tmp_path / "quarantine"

    monkeypatch.setattr(
        "src.quarantine.QUARANTINE_DIR",
        quarantine_dir
    )

    schema_report = {
        "file_name": "batch_04.parquet",
        "status": "INCOMPATIBLE",
        "missing_required_columns": [],
        "type_changes": {
            "age": {
                "expected": "int64",
                "actual": "string",
            }
        },
        "unapproved_columns": [],
    }

    result = quarantine_file(input_file, schema_report)

    # Original input must remain unchanged.
    assert input_file.exists()
    assert input_file.read_bytes() == original_bytes

    # Quarantined Parquet copy must exist.
    quarantined_file = quarantine_dir / "batch_04.parquet"
    assert quarantined_file.exists()

    # Its contents must match the original.
    quarantined_table = pq.read_table(quarantined_file)
    assert quarantined_table.equals(table)

    # Quarantine metadata must exist and be valid JSON.
    metadata_file = quarantine_dir / "batch_04.json"
    assert metadata_file.exists()

    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))

    assert metadata["status"] == "QUARANTINED"
    assert metadata["source_file"] == "batch_04.parquet"

    assert result["status"] == "QUARANTINED"
