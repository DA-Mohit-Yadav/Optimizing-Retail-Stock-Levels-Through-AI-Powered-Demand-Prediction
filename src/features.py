from __future__ import annotations

import pandas as pd


LAG_COLUMNS = [1, 7, 14, 28]
ROLLING_WINDOWS = [7, 14, 28]


def add_time_series_features(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    frame = frame.sort_values(["family", "date"]).reset_index(drop=True)

    frame["city_code"] = pd.Categorical(frame["city"]).codes
    frame["state_code"] = pd.Categorical(frame["state"]).codes
    frame["store_type_code"] = pd.Categorical(frame["type"]).codes
    frame["day_name_code"] = pd.Categorical(frame["day_name"]).codes

    for lag in LAG_COLUMNS:
        frame[f"lag_{lag}"] = frame.groupby("family")["sales"].shift(lag)

    for window in ROLLING_WINDOWS:
        shifted = frame.groupby("family")["sales"].shift(1)
        frame[f"rolling_mean_{window}"] = (
            shifted.groupby(frame["family"]).rolling(window).mean().reset_index(level=0, drop=True)
        )
        frame[f"rolling_std_{window}"] = (
            shifted.groupby(frame["family"]).rolling(window).std().reset_index(level=0, drop=True)
        )
    numeric_fill_columns = [column for column in frame.columns if column.startswith("rolling_std_")]
    for column in numeric_fill_columns:
        frame[column] = frame[column].fillna(0)

    frame = frame.dropna().reset_index(drop=True)
    return frame


def train_test_split_by_date(df: pd.DataFrame, test_days: int = 90) -> tuple[pd.DataFrame, pd.DataFrame]:
    cutoff = df["date"].max() - pd.Timedelta(days=test_days)
    train_df = df[df["date"] <= cutoff].copy()
    test_df = df[df["date"] > cutoff].copy()
    return train_df, test_df
