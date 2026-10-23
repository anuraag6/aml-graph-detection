"""Tests for the transactions loader.

These use a tiny hand-written CSV instead of the real file: data/ is gitignored,
so the real file won't exist on a fresh clone or in CI, and a small fixture
lets each row target one specific edge case.
"""

import pandas as pd
import pytest

from aml.data import load_transactions, save_parquet

# Same header as the raw file, including the duplicated "Account" column.
# Row 1: self-transfer, bank code with a leading zero.
# Row 2: same account number as row 1 but at bank "10", so a different account.
# Row 3: out of time order, to check sorting.
RAW_CSV = """\
Timestamp,From Bank,Account,To Bank,Account,Amount Received,Receiving Currency,Amount Paid,Payment Currency,Payment Format,Is Laundering
2022/09/01 00:20,010,8000EBD30,010,8000EBD30,3697.34,US Dollar,3697.34,US Dollar,Reinvestment,0
2022/09/01 00:25,10,8000EBD30,001,8000F5340,0.01,US Dollar,0.01,US Dollar,Cheque,1
2022/09/01 00:00,03209,8000F4670,03209,8000F4670,14675.57,Euro,14675.57,Euro,Reinvestment,0
"""


@pytest.fixture
def raw_csv(tmp_path):
    path = tmp_path / "trans.csv"
    path.write_text(RAW_CSV)
    return path


def test_columns_are_renamed_without_duplicates(raw_csv):
    df = load_transactions(raw_csv)
    assert "from_account" in df.columns and "to_account" in df.columns
    assert not any(c.startswith("Account") for c in df.columns)


def test_timestamps_parsed_and_sorted(raw_csv):
    df = load_transactions(raw_csv)
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
    assert df["timestamp"].iloc[0] == pd.Timestamp("2022-09-01 00:00")
    assert df["timestamp"].is_monotonic_increasing


def test_bank_codes_keep_leading_zeros(raw_csv):
    df = load_transactions(raw_csv)
    assert "010" in set(df["from_bank"])
    assert "03209" in set(df["from_bank"])


def test_account_id_combines_bank_and_account(raw_csv):
    df = load_transactions(raw_csv)
    ids = set(df["from_id"])
    # Same account number at banks "010" and "10" must give two distinct IDs.
    assert {"010_8000EBD30", "10_8000EBD30"} <= ids
    # The self-transfer has identical sender and receiver IDs.
    self_transfer = df[df["from_bank"] == "010"].iloc[0]
    assert self_transfer["from_id"] == self_transfer["to_id"]


def test_parquet_round_trip_preserves_data_and_types(raw_csv, tmp_path):
    df = load_transactions(raw_csv)
    out = save_parquet(df, tmp_path / "nested" / "trans.parquet")
    back = pd.read_parquet(out)
    # check_dtype=True (the default) also confirms datetime/category/int8
    # survive the round trip, which is the point of using parquet.
    pd.testing.assert_frame_equal(df, back)
