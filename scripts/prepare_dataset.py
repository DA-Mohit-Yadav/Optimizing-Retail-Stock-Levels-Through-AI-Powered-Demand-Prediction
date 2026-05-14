from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "Dataset" / "Corporacion_Favorita"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "store1_three_families_daily.csv"
SELECTED_FAMILIES = ["BEVERAGES", "DAIRY", "GROCERY I"]
SELECTED_STORE = 1


def prepare_oil_features(oil_df: pd.DataFrame) -> pd.DataFrame:
    oil_df = oil_df.copy()
    oil_df["date"] = pd.to_datetime(oil_df["date"])
    oil_df = oil_df.sort_values("date")
    full_range = pd.date_range(oil_df["date"].min(), oil_df["date"].max(), freq="D")
    oil_df = oil_df.set_index("date").reindex(full_range).rename_axis("date").reset_index()
    oil_df["dcoilwtico"] = oil_df["dcoilwtico"].interpolate(method="linear").bfill().ffill()
    return oil_df


def prepare_holiday_features(holidays_df: pd.DataFrame) -> pd.DataFrame:
    holidays_df = holidays_df.copy()
    holidays_df["date"] = pd.to_datetime(holidays_df["date"])
    holidays_df = holidays_df[holidays_df["transferred"] == False]  # noqa: E712

    holiday_flag = holidays_df.groupby("date").size().rename("holiday_event_count").reset_index()
    holiday_flag["holiday"] = 1

    national_flag = (
        holidays_df[holidays_df["locale"] == "National"]
        .groupby("date")
        .size()
        .rename("national_event_count")
        .reset_index()
    )
    national_flag["national_holiday"] = 1

    merged = holiday_flag.merge(national_flag, on="date", how="left")
    merged["national_holiday"] = merged["national_holiday"].fillna(0).astype(int)
    return merged[["date", "holiday", "national_holiday", "holiday_event_count", "national_event_count"]].fillna(0)


def build_processed_dataset() -> pd.DataFrame:
    items = pd.read_csv(RAW_DIR / "items.csv")
    stores = pd.read_csv(RAW_DIR / "stores.csv")
    oil = prepare_oil_features(pd.read_csv(RAW_DIR / "oil.csv"))
    holidays = prepare_holiday_features(pd.read_csv(RAW_DIR / "holidays_events.csv"))
    transactions = pd.read_csv(RAW_DIR / "transactions.csv", parse_dates=["date"])
    daily_chunks: list[pd.DataFrame] = []

    for chunk in pd.read_csv(
        RAW_DIR / "train.csv",
        usecols=["date", "store_nbr", "item_nbr", "unit_sales", "onpromotion"],
        parse_dates=["date"],
        dtype={"onpromotion": "string"},
        chunksize=500_000,
    ):
        filtered = chunk[chunk["store_nbr"] == SELECTED_STORE].merge(items, on="item_nbr", how="left")
        filtered = filtered[filtered["family"].isin(SELECTED_FAMILIES)].copy()
        if filtered.empty:
            continue
        filtered["sales"] = filtered["unit_sales"].clip(lower=0)
        filtered["onpromotion"] = filtered["onpromotion"].fillna("False").eq("True").astype(int)
        chunk_daily = (
            filtered.groupby(["date", "store_nbr", "family"], as_index=False)
            .agg(
                sales=("sales", "sum"),
                onpromotion=("onpromotion", "sum"),
                item_count=("item_nbr", "nunique"),
                perishable_share=("perishable", "mean"),
            )
        )
        daily_chunks.append(chunk_daily)

    daily_family = (
        pd.concat(daily_chunks, ignore_index=True)
        .groupby(["date", "store_nbr", "family"], as_index=False)
        .agg(
            sales=("sales", "sum"),
            onpromotion=("onpromotion", "sum"),
            item_count=("item_count", "max"),
            perishable_share=("perishable_share", "mean"),
        )
    )

    store_meta = stores[stores["store_nbr"] == SELECTED_STORE].copy()
    daily_family = daily_family.merge(store_meta, on="store_nbr", how="left")
    daily_family = daily_family.merge(oil, on="date", how="left")
    daily_family = daily_family.merge(transactions, on=["date", "store_nbr"], how="left")
    daily_family = daily_family.merge(holidays, on="date", how="left")

    daily_family["transactions"] = daily_family["transactions"].fillna(0)
    daily_family["holiday"] = daily_family["holiday"].fillna(0).astype(int)
    daily_family["national_holiday"] = daily_family["national_holiday"].fillna(0).astype(int)
    daily_family["holiday_event_count"] = daily_family["holiday_event_count"].fillna(0).astype(int)
    daily_family["national_event_count"] = daily_family["national_event_count"].fillna(0).astype(int)

    daily_family["year"] = daily_family["date"].dt.year
    daily_family["month"] = daily_family["date"].dt.month
    daily_family["day"] = daily_family["date"].dt.day
    daily_family["day_of_week"] = daily_family["date"].dt.dayofweek
    daily_family["week_of_year"] = daily_family["date"].dt.isocalendar().week.astype(int)
    daily_family["day_name"] = daily_family["date"].dt.day_name()
    daily_family["is_weekend"] = daily_family["day_of_week"].isin([5, 6]).astype(int)

    ordered_columns = [
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
    return daily_family[ordered_columns].sort_values(["family", "date"]).reset_index(drop=True)


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    dataset = build_processed_dataset()
    dataset.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved processed dataset to: {OUTPUT_PATH}")
    print(f"Shape: {dataset.shape}")
    print(dataset.head().to_string(index=False))


if __name__ == "__main__":
    main()
