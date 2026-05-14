from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


FEATURE_COLUMNS = [
    "onpromotion",
    "item_count",
    "perishable_share",
    "city_code",
    "state_code",
    "store_type_code",
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
    "day_name_code",
    "day_of_week",
    "week_of_year",
    "is_weekend",
    "lag_1",
    "lag_7",
    "lag_14",
    "lag_28",
    "rolling_mean_7",
    "rolling_mean_14",
    "rolling_mean_28",
    "rolling_std_7",
    "rolling_std_14",
    "rolling_std_28",
]


@dataclass
class ForecastResult:
    model_name: str
    predictions: pd.Series


class LinearDemandRegressor:
    def __init__(self) -> None:
        self.coefficients: np.ndarray | None = None

    def fit(self, frame: pd.DataFrame, target_column: str = "sales") -> None:
        x = frame[FEATURE_COLUMNS].to_numpy(dtype=float)
        y = frame[target_column].to_numpy(dtype=float)
        intercept = np.ones((x.shape[0], 1))
        design = np.hstack([intercept, x])
        self.coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        if self.coefficients is None:
            raise RuntimeError("Model must be fitted before prediction.")
        x = frame[FEATURE_COLUMNS].to_numpy(dtype=float)
        intercept = np.ones((x.shape[0], 1))
        design = np.hstack([intercept, x])
        predictions = design @ self.coefficients
        return np.clip(predictions, a_min=0, a_max=None)


def seasonal_naive_predict(train_df: pd.DataFrame, test_df: pd.DataFrame, season_lag: int = 7) -> pd.Series:
    predictions: list[float] = []
    for family, family_test in test_df.groupby("family"):
        family_train = train_df[train_df["family"] == family].sort_values("date")
        history = family_train["sales"].tolist()
        family_predictions: list[float] = []
        for _, row in family_test.sort_values("date").iterrows():
            if len(history) >= season_lag:
                prediction = history[-season_lag]
            else:
                prediction = float(np.mean(history))
            family_predictions.append(max(prediction, 0.0))
            history.append(row["sales"])
        predictions.extend(family_predictions)
    return pd.Series(predictions, index=test_df.sort_values(["family", "date"]).index)


def moving_average_predict(train_df: pd.DataFrame, test_df: pd.DataFrame, window: int = 7) -> pd.Series:
    predictions: list[float] = []
    for family, family_test in test_df.groupby("family"):
        family_train = train_df[train_df["family"] == family].sort_values("date")
        history = family_train["sales"].tolist()
        family_predictions: list[float] = []
        for _, row in family_test.sort_values("date").iterrows():
            window_values = history[-window:] if len(history) >= window else history
            prediction = float(np.mean(window_values))
            family_predictions.append(max(prediction, 0.0))
            history.append(row["sales"])
        predictions.extend(family_predictions)
    return pd.Series(predictions, index=test_df.sort_values(["family", "date"]).index)


def regression_predict(train_df: pd.DataFrame, test_df: pd.DataFrame) -> pd.Series:
    model = LinearDemandRegressor()
    model.fit(train_df)
    ordered_test = test_df.sort_values(["family", "date"])
    predictions = model.predict(ordered_test)
    return pd.Series(predictions, index=ordered_test.index)


def mae(actual: pd.Series, predicted: pd.Series) -> float:
    return float(np.mean(np.abs(actual.to_numpy() - predicted.to_numpy())))


def rmse(actual: pd.Series, predicted: pd.Series) -> float:
    return float(np.sqrt(np.mean((actual.to_numpy() - predicted.to_numpy()) ** 2)))


def mape(actual: pd.Series, predicted: pd.Series) -> float:
    actual_values = actual.to_numpy(dtype=float)
    predicted_values = predicted.to_numpy(dtype=float)
    denominator = np.where(actual_values == 0, 1, actual_values)
    return float(np.mean(np.abs((actual_values - predicted_values) / denominator)) * 100)
