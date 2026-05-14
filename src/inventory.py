from __future__ import annotations

import math

import pandas as pd


def build_inventory_recommendations(
    forecast_frame: pd.DataFrame,
    lead_time_days: int = 7,
    review_period_days: int = 7,
    service_level_z: float = 1.65,
) -> pd.DataFrame:
    rows: list[dict] = []

    for family, family_frame in forecast_frame.groupby("family"):
        average_forecast = family_frame["predicted_sales"].mean()
        demand_std = family_frame["predicted_sales"].std(ddof=0)
        safety_stock = service_level_z * demand_std * math.sqrt(lead_time_days)
        reorder_point = average_forecast * lead_time_days + safety_stock
        recommended_order_qty = average_forecast * (lead_time_days + review_period_days) + safety_stock

        rows.append(
            {
                "family": family,
                "avg_daily_forecast": round(float(average_forecast), 2),
                "forecast_std_dev": round(float(demand_std), 2),
                "safety_stock": round(float(safety_stock), 2),
                "reorder_point": round(float(reorder_point), 2),
                "recommended_order_qty": round(float(recommended_order_qty), 2),
            }
        )

    return pd.DataFrame(rows).sort_values("family").reset_index(drop=True)


def simulate_inventory_policy(
    forecast_frame: pd.DataFrame,
    inventory_policy_df: pd.DataFrame,
    initial_stock_days: int = 10,
    lead_time_days: int = 7,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    simulation_rows: list[dict] = []
    alert_rows: list[dict] = []

    for family, family_frame in forecast_frame.groupby("family"):
        family_policy = inventory_policy_df[inventory_policy_df["family"] == family].iloc[0]
        family_frame = family_frame.sort_values("date").copy()

        current_stock = float(family_policy["avg_daily_forecast"] * initial_stock_days)
        reorder_point = float(family_policy["reorder_point"])
        order_qty = float(family_policy["recommended_order_qty"])
        open_orders: list[tuple[pd.Timestamp, float]] = []

        for _, row in family_frame.iterrows():
            current_date = row["date"]
            actual_sales = float(row["sales"])
            predicted_sales = float(row["predicted_sales"])

            arrivals_today = sum(qty for arrival_date, qty in open_orders if arrival_date == current_date)
            current_stock += arrivals_today
            open_orders = [(arrival_date, qty) for arrival_date, qty in open_orders if arrival_date != current_date]

            stock_before_sales = current_stock
            fulfilled_sales = min(current_stock, actual_sales)
            stockout_units = max(actual_sales - current_stock, 0.0)
            current_stock = max(current_stock - actual_sales, 0.0)

            placed_order = 0.0
            if current_stock <= reorder_point:
                arrival_date = current_date + pd.Timedelta(days=lead_time_days)
                open_orders.append((arrival_date, order_qty))
                placed_order = order_qty
                alert_rows.append(
                    {
                        "date": current_date,
                        "family": family,
                        "alert_type": "Reorder Triggered",
                        "stock_after_sales": round(current_stock, 2),
                        "reorder_point": round(reorder_point, 2),
                        "recommended_order_qty": round(order_qty, 2),
                    }
                )

            simulation_rows.append(
                {
                    "date": current_date,
                    "family": family,
                    "actual_sales": round(actual_sales, 2),
                    "predicted_sales": round(predicted_sales, 2),
                    "stock_before_sales": round(stock_before_sales, 2),
                    "fulfilled_sales": round(fulfilled_sales, 2),
                    "stockout_units": round(stockout_units, 2),
                    "stock_after_sales": round(current_stock, 2),
                    "arrivals_today": round(arrivals_today, 2),
                    "placed_order_qty": round(placed_order, 2),
                }
            )

    simulation_df = pd.DataFrame(simulation_rows)
    alerts_df = pd.DataFrame(alert_rows)
    return simulation_df, alerts_df
