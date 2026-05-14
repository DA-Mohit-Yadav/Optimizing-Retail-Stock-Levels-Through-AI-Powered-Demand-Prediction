from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def save_metrics_table(metrics_df: pd.DataFrame, output_path: Path) -> None:
    metrics_df.to_csv(output_path, index=False)


def save_inventory_table(inventory_df: pd.DataFrame, output_path: Path) -> None:
    inventory_df.to_csv(output_path, index=False)


def plot_sales_history(df: pd.DataFrame, output_path: Path) -> None:
    plt.figure(figsize=(12, 6))
    for family, family_frame in df.groupby("family"):
        plt.plot(family_frame["date"], family_frame["sales"], label=family, linewidth=1.6)
    plt.title("Daily Sales by Product Family")
    plt.xlabel("Date")
    plt.ylabel("Sales")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_model_comparison(test_frame: pd.DataFrame, output_path: Path) -> None:
    families = test_frame["family"].unique().tolist()
    fig, axes = plt.subplots(len(families), 1, figsize=(12, 10), sharex=True)
    if len(families) == 1:
        axes = [axes]

    for axis, family in zip(axes, families):
        family_frame = test_frame[test_frame["family"] == family].sort_values("date")
        axis.plot(family_frame["date"], family_frame["sales"], label="Actual", linewidth=1.8)
        axis.plot(family_frame["date"], family_frame["predicted_sales"], label="Predicted", linewidth=1.4)
        axis.set_title(f"{family}: Actual vs Predicted Sales")
        axis.set_ylabel("Sales")
        axis.legend()

    plt.xlabel("Date")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_inventory_levels(simulation_df: pd.DataFrame, output_path: Path) -> None:
    families = simulation_df["family"].unique().tolist()
    fig, axes = plt.subplots(len(families), 1, figsize=(12, 10), sharex=True)
    if len(families) == 1:
        axes = [axes]

    for axis, family in zip(axes, families):
        family_frame = simulation_df[simulation_df["family"] == family].sort_values("date")
        axis.plot(family_frame["date"], family_frame["stock_after_sales"], label="Stock After Sales", linewidth=1.6)
        axis.bar(family_frame["date"], family_frame["stockout_units"], label="Stockout Units", alpha=0.35)
        axis.set_title(f"{family}: Simulated Inventory Position")
        axis.set_ylabel("Units")
        axis.legend()

    plt.xlabel("Date")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def _image_to_base64(image_path: Path) -> str:
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")


def build_html_dashboard(
    summary_lines: list[str],
    metrics_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    alerts_df: pd.DataFrame,
    figures: dict[str, Path],
    output_path: Path,
) -> None:
    sections = []
    for title, path in figures.items():
        encoded = _image_to_base64(path)
        sections.append(
            f"<section><h2>{title}</h2><img src='data:image/png;base64,{encoded}' alt='{title}' style='max-width:100%; border:1px solid #ccc;'></section>"
        )

    alerts_preview = alerts_df.head(20) if not alerts_df.empty else pd.DataFrame(
        [{"message": "No reorder alerts were triggered in the simulated test period."}]
    )

    html = f"""
    <html>
    <head>
        <title>Retail Forecasting Dashboard</title>
        <style>
            body {{ font-family: Georgia, serif; margin: 32px; color: #222; background: #faf8f4; }}
            h1, h2 {{ color: #1f3a5f; }}
            .summary {{ background: #fff; padding: 18px; border-radius: 10px; border: 1px solid #ddd; }}
            table {{ border-collapse: collapse; width: 100%; background: #fff; margin-top: 12px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background: #f0efe9; }}
            section {{ margin-top: 28px; }}
        </style>
    </head>
    <body>
        <h1>Retail Demand Forecasting and Inventory Dashboard</h1>
        <div class="summary">
            <h2>Project Summary</h2>
            <ul>
                {''.join(f'<li>{line}</li>' for line in summary_lines)}
            </ul>
        </div>
        <section>
            <h2>Model Comparison</h2>
            {metrics_df.to_html(index=False)}
        </section>
        <section>
            <h2>Inventory Recommendations</h2>
            {inventory_df.to_html(index=False)}
        </section>
        <section>
            <h2>Stock Alert Preview</h2>
            {alerts_preview.to_html(index=False)}
        </section>
        {''.join(sections)}
    </body>
    </html>
    """
    output_path.write_text(html, encoding="utf-8")
