
from pathlib import Path


from src.schema_detector import inspect_parquet_file


INPUT_DIR = Path("data/input")


def main():

    files = sorted(INPUT_DIR.glob("*.parquet"))

    if not files:
        print("No Parquet files found!")
        return

    for file_path in files:

        report = inspect_parquet_file(file_path)

        print("\n" + "=" * 60)
        print(f"FILE: {file_path.name}")
        print(f"STATUS: {report['status']}")

        print("Added columns:", report["added_columns"])

        print(
            "Missing required columns:",
            report["missing_required_columns"]
        )

        print(
            "Missing optional columns:",
            report["missing_optional_columns"]
        )

        print("Type changes:", report["type_changes"])

        print(
            "Unapproved columns:",
            report["unapproved_columns"]
        )


if __name__ == "__main__":
    main()
