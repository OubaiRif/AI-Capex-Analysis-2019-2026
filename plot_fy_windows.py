"""
plot_fy_windows.py
Builds the "what does FY2025 actually cover on the calendar" chart,
reading real filing end-dates from fin_data.db (not hardcoded).
Run from the project folder (same folder as fin_data.db):
    python3 plot_fy_windows.py
Output: fy_windows_chart.png, saved next to the script.
"""
from pathlib import Path
from datetime import date, timedelta
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DB_PATH = Path(__file__).parent / "fin_data.db"
OUT_PATH = Path(__file__).parent / "fy_windows_chart.png"

COLORS = {
    "AMZN": "#E69F00", "GOOGL": "#56B4E9", "META": "#009E73",
    "MSFT": "#0072B2", "ORCL": "#D55E00",
}

REFERENCE_YEAR = 2025  # the fiscal year being compared


def load_windows():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """
        SELECT DISTINCT ticker, end_of_period
        FROM fin_data
        WHERE metric = 'capex' AND fiscal_year = ?
        ORDER BY ticker
        """,
        (REFERENCE_YEAR,),
    ).fetchall()
    conn.close()

    windows = []
    for ticker, end_str in rows:
        end = date.fromisoformat(end_str)
        start = end - timedelta(days=364)  # annual period, per the ~350+ day rule
        windows.append((ticker, start, end))
    return windows


LABEL_COLOR = {"AMZN": "#4A2E00", "GOOGL": "#042C53", "META": "white", "MSFT": "white", "ORCL": "white"}


def plot(windows):
    fig, ax = plt.subplots(figsize=(10, 3.2))

    for i, (ticker, start, end) in enumerate(windows):
        color = COLORS.get(ticker, "#888888")
        ax.barh(i, (end - start).days, left=mdates.date2num(start), height=0.5, color=color)
        ax.text(mdates.date2num(end) - 10, i, ticker, ha="right", va="center",
                 fontsize=10, fontweight="bold", color=LABEL_COLOR.get(ticker, "white"))

    ax.set_yticks([])
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_title(f"Actual Fiscal Year Coverage vs. Calendar Year \u2014 FY{REFERENCE_YEAR}",
                 fontsize=13, fontweight="bold", loc="left", pad=14)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.margins(x=0.15)

    fig.text(0.01, -0.05,
              "Source: SEC EDGAR 10-K filings. Fiscal year-end dates as reported by each company \u2014\n"
              "MSFT (Jun) and ORCL (May) close months before the calendar-year peers (GOOGL/AMZN/META, Dec).",
              fontsize=8, color="#777777")

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    windows = load_windows()
    fig = plot(windows)
    fig.savefig(OUT_PATH, dpi=300, bbox_inches="tight")
    print(f"saved {OUT_PATH}")
