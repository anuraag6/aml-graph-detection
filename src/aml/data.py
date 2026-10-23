"""Load the IBM AML transactions CSV into a clean DataFrame and save it as parquet.

Run as a script to build the processed file once:

    PYTHONPATH=src python -m aml.data data/raw/HI-Small_Trans.csv data/processed/HI-Small_Trans.parquet

Later code should read the parquet (seconds) instead of re-parsing the CSV.
"""

import argparse
from pathlib import Path

import pandas as pd

# The raw header has "Account" twice (sender, then receiver). pandas would
# silently rename the second to "Account.1", which is easy to mix up, so we
# replace the header with explicit snake_case names, in the CSV's column order.
COLUMNS = [
    "timestamp",
    "from_bank",
    "from_account",
    "to_bank",
    "to_account",
    "amount_received",
    "receiving_currency",
    "amount_paid",
    "payment_currency",
    "payment_format",
    "is_laundering",
]

# Bank codes look numeric but have leading zeros ("010", "03208"). Parsing them
# as ints would make "010" and "10" collide; in HI-Small that merges 58 bank
# codes we can't prove are the same bank. Keep codes and accounts as strings.
# Currencies and payment formats have few distinct values, so "category"
# stores each as a small integer code: less memory, faster groupbys.
DTYPES = {
    "from_bank": "str",
    "from_account": "str",
    "to_bank": "str",
    "to_account": "str",
    "amount_received": "float64",
    "receiving_currency": "category",
    "amount_paid": "float64",
    "payment_currency": "category",
    "payment_format": "category",
    "is_laundering": "int8",
}

# Every timestamp in the file looks like "2022/09/01 00:20". Giving the format
# explicitly is much faster than letting pandas guess, and it raises on a
# malformed value instead of silently guessing a different format.
TIMESTAMP_FORMAT = "%Y/%m/%d %H:%M"


def make_account_id(bank: pd.Series, account: pd.Series) -> pd.Series:
    """Combine bank code and account number into one account ID, e.g. "010_8000EBD30".

    Account numbers alone are not unique: in HI-Small, 8 account numbers exist
    at more than one bank, so they are different accounts. The separator stops
    accidental collisions like "01" + "0ABC" vs "010" + "ABC".
    """
    return bank + "_" + account


def load_transactions(csv_path: str | Path) -> pd.DataFrame:
    """Read the raw transactions CSV and return a cleaned DataFrame.

    Rows are sorted by time: the raw file is only roughly ordered, and later
    steps (time-based train/test splits, "transactions in the last N hours"
    features) assume chronological order.
    """
    df = pd.read_csv(
        csv_path,
        header=0,  # skip the raw header row...
        names=COLUMNS,  # ...and use our names instead
        dtype=DTYPES,
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], format=TIMESTAMP_FORMAT)

    df["from_id"] = make_account_id(df["from_bank"], df["from_account"])
    df["to_id"] = make_account_id(df["to_bank"], df["to_account"])

    # A stable sort keeps same-minute transactions in their original file order,
    # so the output is deterministic.
    df = df.sort_values("timestamp", kind="stable", ignore_index=True)
    return df


def save_parquet(df: pd.DataFrame, parquet_path: str | Path) -> Path:
    """Write df to parquet, creating parent directories as needed.

    Parquet stores the column types (datetime, category, int8), so reading it
    back gives the same DataFrame without re-parsing. It is also compressed
    and columnar, so it is much smaller and faster to load than the CSV.
    """
    parquet_path = Path(parquet_path)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet_path, index=False)
    return parquet_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("parquet_path", type=Path)
    args = parser.parse_args()

    df = load_transactions(args.csv_path)
    out = save_parquet(df, args.parquet_path)
    n_accounts = pd.concat([df["from_id"], df["to_id"]]).nunique()
    print(f"Wrote {len(df):,} transactions ({n_accounts:,} accounts) to {out}")


if __name__ == "__main__":
    main()
