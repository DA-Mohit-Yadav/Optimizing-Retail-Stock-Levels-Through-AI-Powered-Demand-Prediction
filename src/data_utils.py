from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "date",
    "store_nbr",
    "family",
    "sales",
    "onpromotion",
    "item_count",
    "perishable_share",
    "city",
    "state",
    "type",
    "cluster",
    "transactions",
    "dcoilwtico",
    "holiday",
    "national_holiday",
    "holiday_event_count",
    "national_event_count",
    "year",
    "month",
    "day",
    "day_of_week",
    "week_of_year",
    "day_name",
    "is_weekend",
]


@dataclass
class DataSummary:
    rows: int
    start_date: str
    end_date: str
    families: list[str]
    stores: int


def load_project_dataset(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, parse_dates=["date"])
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    df = df.copy()
    df = df.sort_values(["family", "date"]).reset_index(drop=True)
    df["sales"] = df["sales"].clip(lower=0)
    df["family"] = df["family"].astype(str)
    df["city"] = df["city"].astype(str)
    df["state"] = df["state"].astype(str)
    df["type"] = df["type"].astype(str)
    df["day_name"] = df["day_name"].astype(str)
    return df


def summarize_dataset(df: pd.DataFrame) -> DataSummary:
    return DataSummary(
        rows=len(df),
        start_date=str(df["date"].min().date()),
        end_date=str(df["date"].max().date()),
        families=sorted(df["family"].unique().tolist()),
        stores=int(df["store_nbr"].nunique()),
    )
