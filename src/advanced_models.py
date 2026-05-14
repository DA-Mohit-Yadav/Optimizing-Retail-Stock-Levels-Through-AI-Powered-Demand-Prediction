from __future__ import annotations

from dataclasses import dataclass
import warnings

import pandas as pd


@dataclass
class OptionalModelResult:
    name: str
    available: bool
    predictions: pd.Series | None
    note: str


def _empty_result(name: str, note: str) -> OptionalModelResult:
    return OptionalModelResult(name=name, available=False, predictions=None, note=note)


def arima_predict(train_df: pd.DataFrame, test_df: pd.DataFrame) -> OptionalModelResult:
    try:
        from statsmodels.tsa.arima.model import ARIMA
    except Exception:
        return _empty_result("arima", "statsmodels is not installed in the current environment.")

    predictions: list[float] = []
    ordered_test = test_df.sort_values(["family", "date"])

    for family, family_test in ordered_test.groupby("family"):
        family_train = train_df[train_df["family"] == family].sort_values("date")
        horizon = len(family_test)
        history = family_train["sales"].astype(float)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fitted = ARIMA(history, order=(7, 1, 1)).fit()
                forecast_values = fitted.forecast(steps=horizon)
            family_predictions = [max(float(value), 0.0) for value in forecast_values]
        except Exception:
            fallback_value = float(history.tail(7).mean())
            family_predictions = [max(fallback_value, 0.0)] * horizon

        predictions.extend(family_predictions)

    return OptionalModelResult(
        name="arima",
        available=True,
        predictions=pd.Series(predictions, index=ordered_test.index),
        note="ARIMA(7,1,1) fitted separately for each family.",
    )


def prophet_predict(train_df: pd.DataFrame, test_df: pd.DataFrame) -> OptionalModelResult:
    try:
        from prophet import Prophet
    except Exception:
        return _empty_result("prophet", "prophet is not installed in the current environment.")

    predictions: list[float] = []
    ordered_test = test_df.sort_values(["family", "date"])

    for family, family_test in ordered_test.groupby("family"):
        family_train = train_df[train_df["family"] == family].sort_values("date")
        prophet_train = family_train[["date", "sales"]].rename(columns={"date": "ds", "sales": "y"})
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
        )
        model.fit(prophet_train)
        future = family_test[["date"]].rename(columns={"date": "ds"})
        forecast = model.predict(future)
        predictions.extend(forecast["yhat"].clip(lower=0).tolist())

    return OptionalModelResult(
        name="prophet",
        available=True,
        predictions=pd.Series(predictions, index=ordered_test.index),
        note="Prophet fitted separately for each family with weekly and yearly seasonality.",
    )


def lstm_predict(train_df: pd.DataFrame, test_df: pd.DataFrame) -> OptionalModelResult:
    try:
        import numpy as np
        from tensorflow.keras.layers import LSTM, Dense
        from tensorflow.keras.models import Sequential
    except Exception:
        return _empty_result("lstm", "tensorflow/keras is not installed in the current environment.")

    predictions: list[float] = []
    ordered_test = test_df.sort_values(["family", "date"])

    for family, family_test in ordered_test.groupby("family"):
        family_train = train_df[train_df["family"] == family].sort_values("date")
        history = family_train["sales"].astype(float).tolist()
        window = 14

        if len(history) <= window:
            predictions.extend([float(sum(history) / len(history))] * len(family_test))
            continue

        x_train = []
        y_train = []
        for idx in range(window, len(history)):
            x_train.append(history[idx - window : idx])
            y_train.append(history[idx])

        x_array = np.array(x_train).reshape(len(x_train), window, 1)
        y_array = np.array(y_train)

        model = Sequential(
            [
                LSTM(16, input_shape=(window, 1)),
                Dense(1),
            ]
        )
        model.compile(optimizer="adam", loss="mse")
        model.fit(x_array, y_array, epochs=10, batch_size=16, verbose=0)

        family_predictions: list[float] = []
        rolling_history = history.copy()
        for _, row in family_test.iterrows():
            last_window = np.array(rolling_history[-window:]).reshape(1, window, 1)
            pred = float(model.predict(last_window, verbose=0)[0][0])
            family_predictions.append(max(pred, 0.0))
            rolling_history.append(float(row["sales"]))

        predictions.extend(family_predictions)

    return OptionalModelResult(
        name="lstm",
        available=True,
        predictions=pd.Series(predictions, index=ordered_test.index),
        note="Single-layer LSTM using the previous 14 days as sequence input.",
    )


def collect_optional_model_predictions(train_df: pd.DataFrame, test_df: pd.DataFrame) -> list[OptionalModelResult]:
    return [
        arima_predict(train_df, test_df),
        prophet_predict(train_df, test_df),
        lstm_predict(train_df, test_df),
    ]
