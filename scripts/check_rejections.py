import pandas as pd

df = pd.read_parquet(
    "data/quarantine/rejected_records.parquet"
)

print(df[
    [
        "customer_id",
        "customer_name",
        "age",
        "email",
        "source_file",
        "source_row",
        "rejection_reason"
    ]
].to_string(index=False))
