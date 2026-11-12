
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


# Project root directory
BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_DIR = BASE_DIR / "data" / "input"
EXPECTED_DIR = BASE_DIR / "data" / "expected"

RANDOM_SEED = 42


def generate_customers(
    start_id,
    rows,
    seed=RANDOM_SEED,
    include_city=False,
    include_salary=False
):
    """Generate reproducible synthetic customer records."""

    rng = np.random.default_rng(seed)

    names = np.array([
        "Rahul", "Priya", "Amit", "Neha",
        "Arjun", "Kiran", "Anjali", "Rohit"
    ])

    cities = np.array([
        "Hyderabad", "Mumbai", "Delhi",
        "Bangalore", "Chennai"
    ])

    domains = np.array([
        "gmail.com", "outlook.com", "example.com"
    ])

    customer_ids = np.arange(start_id, start_id + rows)

    data = {
        "customer_id": customer_ids,
        "customer_name": rng.choice(names, rows),
        "age": rng.integers(18, 101, rows),
        "email": [
            f"customer_{cid}@{rng.choice(domains)}"
            for cid in customer_ids
        ],
        "updated_at": pd.date_range(
            "2026-01-01",
            periods=rows,
            freq="min",
            tz="UTC"
        )
    }

    if include_city:
        data["city"] = rng.choice(cities, rows)

    if include_salary:
        data["salary"] = rng.uniform(20000, 100000, rows).round(2)

    return pd.DataFrame(data)


def save_parquet(df, filename):
    """Save a DataFrame as a Parquet file."""

    filepath = INPUT_DIR / filename

    df.to_parquet(
        filepath,
        engine="pyarrow",
        index=False
    )

    print(f"Created: {filename} | Rows: {len(df)}")


def generate_batches(rows=20):
    """Generate seven batches with different data scenarios."""

    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    EXPECTED_DIR.mkdir(parents=True, exist_ok=True)

    # Batch 01: Original schema
    batch_01 = generate_customers(
        start_id=1001,
        rows=rows,
        seed=42
    )
    save_parquet(batch_01, "batch_01.parquet")

    # Batch 02: New nullable city column
    batch_02 = generate_customers(
        start_id=2001,
        rows=rows,
        seed=43,
        include_city=True
    )
    save_parquet(batch_02, "batch_02.parquet")

    # Batch 03: New nullable salary column
    batch_03 = generate_customers(
        start_id=3001,
        rows=rows,
        seed=44,
        include_city=True,
        include_salary=True
    )
    save_parquet(batch_03, "batch_03.parquet")

    # Batch 04: Breaking schema change
    batch_04 = generate_customers(
        start_id=4001,
        rows=rows,
        seed=45
    )
    batch_04["age"] = batch_04["age"].astype("string")
    save_parquet(batch_04, "batch_04.parquet")

    # Batch 05: Required customer_id column missing
    batch_05 = generate_customers(
        start_id=5001,
        rows=rows,
        seed=46
    )
    batch_05 = batch_05.drop(columns=["customer_id"])
    save_parquet(batch_05, "batch_05.parquet")

    # Batch 06: Duplicate customer records
    batch_06 = generate_customers(
        start_id=6001,
        rows=rows,
        seed=47
    )

    if len(batch_06) >= 2:
        duplicates = batch_06.iloc[:2].copy()
        batch_06 = pd.concat(
            [batch_06, duplicates],
            ignore_index=True
        )

    save_parquet(batch_06, "batch_06.parquet")

    # Batch 07: Invalid individual records
    batch_07 = generate_customers(
        start_id=7001,
        rows=max(rows, 6),
        seed=48,
        include_city=True
    )

    # Domain-specific invalid cases
    batch_07["customer_id"] = batch_07["customer_id"].astype("Int64")
    batch_07.loc[0, "age"] = -5
    batch_07.loc[1, "age"] = 150
    batch_07.loc[2, "customer_name"] = None
    batch_07.loc[3, "email"] = "invalid-email"
    batch_07.loc[4, "customer_id"] = None
    batch_07.loc[5, "email"] = None

    # Boundary values: valid ages
    if len(batch_07) > 6:
        batch_07.loc[6, "age"] = 18

    if len(batch_07) > 7:
        batch_07.loc[7, "age"] = 100

    save_parquet(batch_07, "batch_07.parquet")

    # Keep expected answers separate from actual input data.
    expected_scenarios = {
        "batch_01.parquet": "original_schema",
        "batch_02.parquet": "approved_city_column",
        "batch_03.parquet": "approved_salary_column",
        "batch_04.parquet": "incompatible_age_type",
        "batch_05.parquet": "missing_required_column",
        "batch_06.parquet": "duplicate_customer_ids",
        "batch_07.parquet": "invalid_business_records"
    }

    with open(
        EXPECTED_DIR / "expected_scenarios.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(expected_scenarios, file, indent=4)

    print("\nAll seven sample batches generated successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synthetic Parquet batches"
    )

    parser.add_argument(
        "--rows",
        type=int,
        default=20,
        help="Number of normal records per batch"
    )

    args = parser.parse_args()

    if args.rows < 1:
        parser.error("--rows must be at least 1")

    generate_batches(args.rows)
