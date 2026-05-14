from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.advanced_models import collect_optional_model_predictions
from src.data_utils import load_project_dataset, summarize_dataset
from src.features import add_time_series_features, train_test_split_by_date
from src.inventory import build_inventory_recommendations, simulate_inventory_policy
from src.models import mae, mape, moving_average_predict, regression_predict, rmse, seasonal_naive_predict
from src.reporting import (
    build_html_dashboard,
    plot_inventory_levels,
    plot_model_comparison,
    plot_sales_history,
    save_inventory_table,
    save_metrics_table,
)


PROJECT_ROOT = Path(__file__).resolve().parent
DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "store1_three_families_daily.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
TABLES_DIR = REPORTS_DIR / "tables"


def evaluate_models(train_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple[pd.DataFrame, str, pd.Series, pd.DataFrame]:
    ordered_test = test_df.sort_values(["family", "date"])
    actual = ordered_test["sales"]

    model_predictions = {
        "seasonal_naive": seasonal_naive_predict(train_df, ordered_test),
        "moving_average_7": moving_average_predict(train_df, ordered_test),
        "linear_regression_lags": regression_predict(train_df, ordered_test),
    }
    availability_rows = [
        {"model": "seasonal_naive", "available": True, "note": "Implemented locally as benchmark model."},
        {"model": "moving_average_7", "available": True, "note": "Implemented locally as benchmark model."},
        {"model": "linear_regression_lags", "available": True, "note": "Implemented locally using lag and rolling features."},
    ]

    for optional_result in collect_optional_model_predictions(train_df, ordered_test):
        availability_rows.append(
            {
                "model": optional_result.name,
                "available": optional_result.available,
                "note": optional_result.note,
            }
        )
        if optional_result.available and optional_result.predictions is not None:
            model_predictions[optional_result.name] = optional_result.predictions

    results: list[dict] = []
    best_model = ""
    best_rmse = float("inf")
    best_predictions = pd.Series(dtype=float)

    for model_name, predictions in model_predictions.items():
        aligned_predictions = predictions.loc[ordered_test.index]
        model_rmse = rmse(actual, aligned_predictions)
        results.append(
            {
                "model": model_name,
                "mae": round(mae(actual, aligned_predictions), 3),
                "rmse": round(model_rmse, 3),
                "mape": round(mape(actual, aligned_predictions), 3),
            }
        )

        if model_rmse < best_rmse:
            best_rmse = model_rmse
            best_model = model_name
            best_predictions = aligned_predictions

    metrics_df = pd.DataFrame(results).sort_values("rmse").reset_index(drop=True)
    availability_df = pd.DataFrame(availability_rows)
    return metrics_df, best_model, best_predictions, availability_df


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    raw_df = load_project_dataset(DATASET_PATH)
    summary = summarize_dataset(raw_df)
    feature_df = add_time_series_features(raw_df)
    train_df, test_df = train_test_split_by_date(feature_df, test_days=90)

    metrics_df, best_model, best_predictions, availability_df = evaluate_models(train_df, test_df)

    ordered_test = test_df.sort_values(["family", "date"]).copy()
    ordered_test["predicted_sales"] = best_predictions.loc[ordered_test.index].to_numpy()

    inventory_df = build_inventory_recommendations(ordered_test)
    simulation_df, alerts_df = simulate_inventory_policy(ordered_test, inventory_df)

    plot_sales_history(raw_df, FIGURES_DIR / "sales_history.png")
    plot_model_comparison(ordered_test, FIGURES_DIR / "best_model_forecast.png")
    plot_inventory_levels(simulation_df, FIGURES_DIR / "inventory_simulation.png")
    save_metrics_table(metrics_df, TABLES_DIR / "model_metrics.csv")
    save_inventory_table(inventory_df, TABLES_DIR / "inventory_recommendations.csv")
    availability_df.to_csv(TABLES_DIR / "model_availability.csv", index=False)
    ordered_test.to_csv(TABLES_DIR / "forecast_vs_actual.csv", index=False)
    simulation_df.to_csv(TABLES_DIR / "inventory_simulation.csv", index=False)
    alerts_df.to_csv(TABLES_DIR / "stock_alerts.csv", index=False)

    summary_lines = [
        "Retail Demand Forecasting and Inventory Optimization Project",
        f"Rows analysed: {summary.rows}",
        f"Date range: {summary.start_date} to {summary.end_date}",
        f"Store count: {summary.stores}",
        f"Families: {', '.join(summary.families)}",
        f"Training rows: {len(train_df)}",
        f"Testing rows: {len(test_df)}",
        f"Best model by RMSE: {best_model}",
        "Advanced model hooks prepared for ARIMA, Prophet, and LSTM when the required libraries are installed.",
    ]
    (REPORTS_DIR / "project_summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")
    build_html_dashboard(
        summary_lines=summary_lines,
        metrics_df=metrics_df,
        inventory_df=inventory_df,
        alerts_df=alerts_df,
        figures={
            "Sales History": FIGURES_DIR / "sales_history.png",
            "Best Forecast vs Actual": FIGURES_DIR / "best_model_forecast.png",
            "Inventory Simulation": FIGURES_DIR / "inventory_simulation.png",
        },
        output_path=REPORTS_DIR / "dashboard.html",
    )

    print("\n".join(summary_lines))
    print("\nModel metrics:")
    print(metrics_df.to_string(index=False))
    print("\nModel availability:")
    print(availability_df.to_string(index=False))
    print("\nInventory recommendations:")
    print(inventory_df.to_string(index=False))
    print("\nStock alerts generated:", len(alerts_df))


if __name__ == "__main__":
    main()
