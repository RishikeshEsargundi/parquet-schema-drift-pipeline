import pandas as pd

TARGET_PATH = "data/target/customers.parquet"

df = pd.read_parquet(TARGET_PATH)

print("Target verification")
print("-------------------")

print("Total records:", len(df))
print("Unique customer IDs:", df["customer_id"].nunique())

print(
    "Duplicate IDs:",
    df["customer_id"].duplicated().sum()
)

print("\nSample records:")

print(
    df[
        [
            "customer_id",
            "customer_name",
            "age",
            "city",
            "salary",
            "source_file"
        ]
    ].head(10).to_string(index=False)
)

assert len(df) == df["customer_id"].nunique()

print("\nSUCCESS: Target contains unique customer IDs.")
