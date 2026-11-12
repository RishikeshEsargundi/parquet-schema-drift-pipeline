
import pandas as pd

from pandas.testing import assert_frame_equal

from src.publisher import publish_customer_snapshot


def create_records():

    return pd.DataFrame([
        {
            "customer_id": 101,
            "customer_name": "Rahul",
            "age": 25,
            "email": "rahul@gmail.com",
            "updated_at": pd.Timestamp(
                "2026-01-01",
                tz="UTC"
            ),
            "city": "Hyderabad",
            "salary": 30000.0,
            "source_file": "batch_01.parquet",
            "source_row": 1
        },
        {
            "customer_id": 101,
            "customer_name": "Rahul",
            "age": 30,
            "email": "rahul@gmail.com",
            "updated_at": pd.Timestamp(
                "2026-01-02",
                tz="UTC"
            ),
            "city": "Mumbai",
            "salary": 35000.0,
            "source_file": "batch_02.parquet",
            "source_row": 1
        },
        {
            "customer_id": 102,
            "customer_name": "Priya",
            "age": 24,
            "email": "priya@gmail.com",
            "updated_at": pd.Timestamp(
                "2026-01-01",
                tz="UTC"
            ),
            "city": "Delhi",
            "salary": 40000.0,
            "source_file": "batch_01.parquet",
            "source_row": 2
        }
    ])


def test_publisher_keeps_latest_customer(tmp_path):

    target = tmp_path / "customers.parquet"

    records = create_records()

    published, duplicates = publish_customer_snapshot(
        records,
        target
    )

    assert len(published) == 2
    assert duplicates == 1

    rahul = published[
        published["customer_id"] == 101
    ]

    assert rahul.iloc[0]["age"] == 30


def test_repeated_publish_is_idempotent(tmp_path):

    target = tmp_path / "customers.parquet"

    records = create_records()

    first, _ = publish_customer_snapshot(
        records,
        target
    )

    second, _ = publish_customer_snapshot(
        records,
        target
    )

    stored = pd.read_parquet(target)

    assert_frame_equal(
        first.reset_index(drop=True),
        second.reset_index(drop=True)
    )

    assert_frame_equal(
        second.reset_index(drop=True),
        stored.reset_index(drop=True)
    )

    assert len(stored) == 2


def test_empty_dataset_is_not_published(tmp_path):

    target = tmp_path / "customers.parquet"

    empty = pd.DataFrame()

    try:
        publish_customer_snapshot(empty, target)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Empty dataset should not be published"
        )

    assert not target.exists()
