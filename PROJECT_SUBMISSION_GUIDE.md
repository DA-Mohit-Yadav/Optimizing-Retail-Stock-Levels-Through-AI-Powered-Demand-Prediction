# Project Submission Guide

## Project Title
Optimizing Retail Stock Levels Through AI-Powered Demand Prediction

## What This Project Currently Does
- Builds a processed dataset from the raw Corporacion Favorita files
- Uses the processed dataset in `data/processed/store1_three_families_daily.csv`
- Forecasts retail demand for three product families:
  - `BEVERAGES`
  - `DAIRY`
  - `GROCERY I`
- Compares multiple forecasting approaches:
  - seasonal naive
  - 7-day moving average
  - linear regression using lag and rolling features
  - ARIMA
  - Prophet
- Selects the best model using chronological test performance
- Converts forecasts into inventory recommendations:
  - safety stock
  - reorder point
  - recommended order quantity
- Simulates stock movement and generates reorder alerts
- Exports a dashboard-style HTML summary for presentation/demo

## Main Files
- `scripts/prepare_dataset.py`: creates the processed modeling dataset
- `run_pipeline.py`: runs the full project
- `src/advanced_models.py`: optional advanced forecasting models
- `src/data_utils.py`: data loading and validation
- `src/features.py`: time-series feature engineering
- `src/models.py`: forecasting models and evaluation metrics
- `src/inventory.py`: inventory optimization logic
- `src/reporting.py`: charts and report tables
- `notebooks/retail_stock_optimization_project.ipynb`: full submission notebook
- `reports/final_report_draft.md`: original report draft
- `reports/tables/model_metrics.csv`: model comparison results
- `reports/tables/model_availability.csv`: available vs unavailable model notes
- `reports/tables/inventory_recommendations.csv`: final inventory suggestions
- `reports/tables/inventory_simulation.csv`: simulated inventory movement
- `reports/tables/stock_alerts.csv`: reorder alerts generated in the test period
- `reports/tables/forecast_vs_actual.csv`: actual vs predicted values for the test period
- `reports/figures/sales_history.png`: sales trend visualization
- `reports/figures/best_model_forecast.png`: best-model forecast visualization
- `reports/figures/inventory_simulation.png`: simulated stock-level chart
- `reports/dashboard.html`: dashboard-style summary page

## How To Run
```powershell
python scripts/prepare_dataset.py
python run_pipeline.py
```

## Results To Mention In Your Report
Use the latest values from `reports/tables/model_metrics.csv` and `reports/tables/inventory_recommendations.csv`.

At the moment, the best-performing model is `linear_regression_lags` with:
- RMSE: `290.328`
- MAE: `229.492`
- MAPE: `17.860`

## Recommended Report Chapter Structure
1. Introduction
2. Problem Statement
3. Objectives
4. Literature Review
5. Dataset Description
6. Data Preprocessing
7. Exploratory Data Analysis
8. Forecasting Methodology
9. Model Evaluation
10. Inventory Optimization Framework
11. Results and Discussion
12. Conclusion
13. Future Work
14. References

## What To Write In Each Chapter
### 1. Introduction
- Explain why poor demand forecasting causes overstock and stockouts.
- Introduce AI and time-series forecasting as decision-support tools in retail.

### 2. Problem Statement
- Retailers often struggle to maintain the right inventory level.
- Too much stock increases holding cost.
- Too little stock causes lost sales and poor customer satisfaction.

### 3. Objectives
- Forecast daily demand for selected product families.
- Compare forecasting methods including classical and AI-oriented approaches where available.
- Use forecast output to recommend inventory actions.
- Support retail decision-making with visual outputs.

### 4. Literature Review
- Review demand forecasting in retail.
- Review time-series methods and machine learning for sales prediction.
- Review inventory optimization concepts such as safety stock and reorder point.

### 5. Dataset Description
- Mention the original dataset source: Corporacion Favorita retail data.
- Explain that the working project dataset is rebuilt from the raw files and saved in `data/processed/store1_three_families_daily.csv`.
- Describe each feature used in the model.

### 6. Data Preprocessing
- Parsing dates
- Sorting chronologically
- Handling missing values in prepared data
- Clipping negative sales values if needed
- Creating lag and rolling statistics features

### 7. Exploratory Data Analysis
- Plot family-wise daily sales
- Discuss seasonality and demand variation
- Compare sales ranges across the three families

### 8. Forecasting Methodology
- Explain why chronological train-test split is used
- Explain the compared models:
  - seasonal naive
  - moving average
  - linear regression with lag features
  - ARIMA
  - Prophet
  - LSTM as an environment-dependent extension

### 9. Model Evaluation
- Report MAE, RMSE, and MAPE
- Justify choosing the best model by lower RMSE

### 10. Inventory Optimization Framework
- Explain lead time demand
- Explain safety stock
- Explain reorder point
- Explain recommended order quantity
- Explain how reorder alerts were generated in the inventory simulation

### 11. Results and Discussion
- Show that the regression-with-lags model performed best
- Include screenshots of the generated figures
- Interpret the business meaning of the inventory recommendations
- Mention the simulated reorder alerts and dashboard output

### 12. Conclusion
- Summarize the forecasting outcome
- Summarize the stock planning benefit

### 13. Future Work
- Add multiple stores
- Add richer features such as transactions and holidays at finer granularity
- Add full LSTM execution when TensorFlow/Keras is available
- Upgrade the HTML dashboard into a live web dashboard

## Viva Preparation
Be ready to answer:
- Why did you choose this dataset?
- Why is time-based splitting important?
- Why did the linear regression with lags perform better?
- How do ARIMA and Prophet compare with the best model?
- How does forecasting improve inventory decisions?
- What assumptions were used in inventory optimization?

## Final Submission Checklist
- Final report in your university template
- Your own wording based on the analysis and report draft already in this repo
- Source code folder
- Result figures and tables
- PPT presentation
- Short demo explanation
- Proper references and citations
