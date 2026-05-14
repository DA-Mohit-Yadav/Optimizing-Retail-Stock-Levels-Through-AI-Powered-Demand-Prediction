# Optimizing Retail Stock Levels Through AI-Powered Demand Prediction

This repository contains my M.Sc. Data Science project on retail demand forecasting and inventory planning. The project uses the Corporacion Favorita retail dataset and focuses on a realistic but manageable scope: **store 1** and **three product families** (`BEVERAGES`, `DAIRY`, and `GROCERY I`).

## Project Aim
The aim of the project is to forecast short-term demand and use the forecasts to improve stocking decisions. Instead of stopping at prediction accuracy, the project connects forecasting output to inventory measures such as safety stock, reorder point, and recommended order quantity.

## What Makes This Version Different
The project does not rely only on a pre-filtered dataset. A dedicated preprocessing script rebuilds the modeling dataset from the raw source files, which makes the workflow easier to explain in a report and more defensible in viva.

## Data Used
- Raw source files: `Dataset/Corporacion_Favorita/`
- Processed modeling dataset: `data/processed/store1_three_families_daily.csv`
- Supporting notebook: `notebooks/retail_stock_optimization_project.ipynb`

## Workflow
1. Read the raw retail files.
2. Filter the analysis to one store and three families.
3. Merge item, store, transaction, oil-price, and holiday information.
4. Create lag, rolling, and calendar features.
5. Split the dataset chronologically.
6. Compare forecasting approaches:
   - seasonal naive
   - 7-day moving average
   - linear regression with lag features
   - ARIMA
   - Prophet
7. Select the best model using RMSE.
8. Generate inventory recommendations from the best forecast.
9. Simulate stock movement and reorder alerts.
10. Export a dashboard-style HTML summary.

## Current Results
Current best model: `linear_regression_lags`

| Model | MAE | RMSE | MAPE |
|---|---:|---:|---:|
| linear_regression_lags | 229.492 | 290.328 | 17.860 |
| prophet | 204.624 | 311.009 | 14.123 |
| arima | 243.310 | 393.264 | 16.320 |
| seasonal_naive | 231.963 | 405.221 | 13.945 |
| moving_average_7 | 351.614 | 525.614 | 27.159 |

Inventory recommendations from the current best model:

| Family | Avg Daily Forecast | Safety Stock | Reorder Point | Recommended Order Qty |
|---|---:|---:|---:|---:|
| BEVERAGES | 2057.83 | 1814.10 | 16218.88 | 30623.65 |
| DAIRY | 817.90 | 1292.61 | 7017.94 | 12743.27 |
| GROCERY I | 2748.15 | 2439.30 | 21676.35 | 40913.41 |

The pipeline also generates reorder alerts through simulated stock movement. In the current run, `21` reorder alerts were triggered across the test horizon.

## Main Files
- `scripts/prepare_dataset.py`: builds the processed dataset from raw files
- `run_pipeline.py`: runs the forecasting and inventory workflow
- `src/`: reusable project code
- `notebooks/retail_stock_optimization_project.ipynb`: submission-friendly notebook
- `reports/final_report_draft.md`: original report draft
- `PROJECT_SUBMISSION_GUIDE.md`: chapter-by-chapter submission help

## How To Run
```powershell
python scripts/prepare_dataset.py
python run_pipeline.py
```

## Generated Outputs
- `reports/project_summary.txt`
- `reports/dashboard.html`
- `reports/figures/sales_history.png`
- `reports/figures/best_model_forecast.png`
- `reports/figures/inventory_simulation.png`
- `reports/tables/model_metrics.csv`
- `reports/tables/model_availability.csv`
- `reports/tables/inventory_recommendations.csv`
- `reports/tables/forecast_vs_actual.csv`
- `reports/tables/inventory_simulation.csv`
- `reports/tables/stock_alerts.csv`

## Academic Scope
This project is suitable for an applied master's submission because it combines:
- business problem framing
- raw-data preparation
- time-series feature engineering
- forecasting model comparison
- model evaluation
- operational inventory logic
- stock alert simulation
- dashboard-style output
- report-ready interpretation
