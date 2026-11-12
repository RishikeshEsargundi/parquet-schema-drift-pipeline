
import json
import shutil
from pathlib import Path


QUARANTINE_DIR = Path("data/quarantine")


def quarantine_file(file_path, schema_report):
    """
    Preserve the original file and save its rejection reason.
    """

    QUARANTINE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = Path(file_path)

    # Preserve original Parquet file
    destination = QUARANTINE_DIR / file_path.name

    shutil.copy2(
        file_path,
        destination
    )

    # Create a detailed rejection report
    rejection_report = {
        "source_file": file_path.name,
        "status": "QUARANTINED",
        "reason": [],
        "schema_details": schema_report
    }

    if schema_report["missing_required_columns"]:
        rejection_report["reason"].append(
            "Missing required columns"
        )

    if schema_report["type_changes"]:
        rejection_report["reason"].append(
            "Incompatible data type changes"
        )

    if schema_report["unapproved_columns"]:
        rejection_report["reason"].append(
            "Unapproved new columns"
        )

    report_path = (
        QUARANTINE_DIR /
        f"{file_path.stem}.json"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            rejection_report,
            file,
            indent=4,
            default=str
        )

    print(
        f"QUARANTINED: {file_path.name}"
    )

    return rejection_report
