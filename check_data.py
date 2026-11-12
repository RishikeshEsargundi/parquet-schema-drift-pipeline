
from pathlib import Path
import pyarrow.parquet as pq

input_dir = Path("data/input")

for file_path in sorted(input_dir.glob("*.parquet")):

    print("\n" + "=" * 50)
    print("FILE:", file_path.name)

    table = pq.read_table(file_path)

    print("ROWS:", table.num_rows)
    print("SCHEMA:")
    print(table.schema)
