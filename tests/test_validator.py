
import pandas as pd
import pytest

from src.validator import validate_dataframe


def create_customer(**overrides):
    """Create one valid customer record."""

    customer = {
        "customer_id": 101,
        "customer_name": "Rahul",
        "age": 25,
        "email": "rahul@gmail.com",
        "updated_at": pd.Timestamp(
            "2026-01-01",
            tz="UTC"
        ),
        "city": "Hyderabad",
        "salary": 30000.0
    }

    customer.update(overrides)

    return customer


def test_valid_customer_is_accepted():

    df = pd.DataFrame([create_customer()])

    valid, rejected = validate_dataframe(
        df,
        source_file="test.parquet"
    )

    assert len(valid) == 1
    assert len(rejected) == 0


def test_missing_customer_id_is_rejected():

    df = pd.DataFrame([
        create_customer(customer_id=pd.NA)
    ])

    valid, rejected = validate_dataframe(
        df,
        source_file="test.parquet"
    )

    assert len(valid) == 0
    assert len(rejected) == 1

    assert (
        "missing_customer_id"
        in rejected.iloc[0]["rejection_reason"]
    )


@pytest.mark.parametrize(
    "age",
    [-5, 101, None]
)
def test_invalid_age_is_rejected(age):

    df = pd.DataFrame([
        create_customer(age=age)
    ])

    valid, rejected = validate_dataframe(
        df,
        source_file="test.parquet"
    )

    assert len(valid) == 0
    assert len(rejected) == 1

    assert (
        "invalid_age"
        in rejected.iloc[0]["rejection_reason"]
    )


def test_invalid_email_is_rejected():

    df = pd.DataFrame([
        create_customer(email="invalid-email")
    ])

    valid, rejected = validate_dataframe(
        df,
        source_file="test.parquet"
    )

    assert len(valid) == 0
    assert len(rejected) == 1


def test_duplicate_customer_id_keeps_latest():

    df = pd.DataFrame([
        create_customer(
            age=25,
            updated_at=pd.Timestamp(
                "2026-01-01",
                tz="UTC"
            )
        ),
        create_customer(
            age=30,
            updated_at=pd.Timestamp(
                "2026-01-02",
                tz="UTC"
            )
        )
    ])

    valid, rejected = validate_dataframe(
        df,
        source_file="test.parquet"
    )

    assert len(valid) == 1
    assert len(rejected) == 1

    assert valid.iloc[0]["age"] == 30

    assert (
        "duplicate_customer_id"
        in rejected.iloc[0]["rejection_reason"]
    )


def test_empty_dataframe_is_handled():

    df = pd.DataFrame(columns=[
        "customer_id",
        "customer_name",
        "age",
        "email",
        "updated_at",
        "city",
        "salary"
    ])

    valid, rejected = validate_dataframe(
        df,
        source_file="empty.parquet"
    )

    assert len(valid) == 0
    assert len(rejected) == 0


def test_rejected_record_has_source_information():

    df = pd.DataFrame([
        create_customer(age=-5)
    ])

    valid, rejected = validate_dataframe(
        df,
        source_file="batch_test.parquet",
        run_id="test_run_001"
    )

    assert rejected.iloc[0]["source_file"] == "batch_test.parquet"
    assert rejected.iloc[0]["run_id"] == "test_run_001"
    assert rejected.iloc[0]["source_row"] == 1


def test_age_boundaries_are_valid():

    df = pd.DataFrame([
        create_customer(
            customer_id=101,
            age=18
        ),
        create_customer(
            customer_id=102,
            age=100
        )
    ])

    valid, rejected = validate_dataframe(
        df,
        source_file="boundary_test.parquet"
    )

    assert len(valid) == 2
    assert len(rejected) == 0
