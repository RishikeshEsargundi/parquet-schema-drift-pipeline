
import json
from pathlib import Path


REPORT_DIR = Path("reports")

reports = sorted(
    REPORT_DIR.glob("run_*.json"),
    key=lambda path: path.stat().st_mtime
)

if not reports:
    raise FileNotFoundError("No run reports found")

latest_report = reports[-1]

with open(
    latest_report,
    "r",
    encoding="utf-8"
) as file:
    report = json.load(file)

print("Run ID:", report["run_id"])
print("Status:", report["status"])

input_rows = report["input_rows"]

accounted_rows = (
    report["schema_quarantined_rows"]
    + report["valid_rows"]
    + report["rejected_rows"]
)

print("Input rows:", input_rows)
print("Accounted rows:", accounted_rows)

assert input_rows == accounted_rows
assert report["status"] == "SUCCESS_WITH_REJECTS"
assert report["published_rows"] == 94

print("SUCCESS: Reconciliation checks passed!")
