from pathlib import Path
import pyarrow.parquet as pq

OUTPUT_DIR = Path("data/output")

for file_path in sorted(OUTPUT_DIR.glob("*.parquet")):

    table = pq.read_table(file_path)

    print("\nFile:", file_path.name)
    print("Rows:", table.num_rows)
    print("Columns:", table.column_names)
    print("Schema:")
    print(table.schema)
