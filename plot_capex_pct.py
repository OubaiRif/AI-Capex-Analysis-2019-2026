"""
plot_capex_pct.py
Builds the capex-as-%-of-revenue chart directly from fin_data.db.
Run from the "AI Revenue Charts" project folder (same folder as fin_data.db):
    python3 plot_capex_pct.py
Output: capex_pct_chart.png, saved next to the script.
"""
from pathlib import Path
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

DB_PATH = Path(__file__).parent / "fin_data.db"
OUT_PATH = Path(__file__).parent / "capex_pct_chart.png"

# Same pivot as queries/capex_pct.sql
QUERY = """
SELECT
    ticker,
    fiscal_year,
    capex,
    revenue,
    ROUND(100.0 * capex / revenue, 1) AS capex_pct
FROM (
    SELECT
        ticker,
        fiscal_year,
        SUM(CASE WHEN metric = 'capex'   THEN value END) AS capex,
        SUM(CASE WHEN metric = 'revenue' THEN value END) AS revenue
    FROM fin_data
    GROUP BY ticker, fiscal_year
)
ORDER BY ticker, fiscal_year;
"""

# Okabe-Ito colorblind-safe palette
COLORS = {
    "AMZN": "#E69F00",
    "GOOGL": "#56B4E9",
    "META": "#009E73",
    "MSFT": "#0072B2",
    "ORCL": "#D55E00",
}

# Last fiscal year every company in COLORS has filed — change this each
# quarter as more 10-Ks come in. Years beyond this render as a dashed
# "early preview" line for whichever companies already have them (MSFT, ORCL).
COMPARABLE_THROUGH = 2025


def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(QUERY, conn)
    conn.close()
    return df


def plot(df):
    fig, ax = plt.subplots(figsize=(10, 6.5))

    for ticker, group in df.groupby("ticker"):
        group = group.sort_values("fiscal_year")
        color = COLORS.get(ticker, "#888888")

        comparable = group[group["fiscal_year"] <= COMPARABLE_THROUGH]
        preview = group[group["fiscal_year"] >= COMPARABLE_THROUGH]

        ax.plot(comparable["fiscal_year"], comparable["capex_pct"],
                marker="o", color=color, linewidth=2.2, label=ticker)

        if len(preview) > 1:
            ax.plot(preview["fiscal_year"], preview["capex_pct"],
                    marker="o", color=color, linewidth=2.2, linestyle="--", alpha=0.6)

        last = group.iloc[-1]
        ax.annotate(f" {ticker}  {last['capex_pct']:.0f}%",
                    (last["fiscal_year"], last["capex_pct"]),
                    color=color, fontsize=10, fontweight="bold", va="center")

    ax.set_title("Capex as a Share of Revenue \u2014 Five US Tech Majors, FY2019\u20132026",
                  fontsize=14, fontweight="bold", loc="left", pad=28)
    ax.text(0, 1.03,
            "Dashed segments: fiscal years already filed by that company but not yet by its peers",
            transform=ax.transAxes, fontsize=9, color="#555555")

    ax.set_ylabel("Capex / Revenue (%)")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f%%'))
    ax.set_xticks(sorted(df["fiscal_year"].unique()))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.margins(x=0.1)

    fig.text(0.01, -0.03,
              "Source: SEC EDGAR 10-K filings (XBRL), reconciled to cash flow statements. Fiscal years as reported by each\n"
              "company; MSFT (Jun) and ORCL (May) year-ends do not align exactly with calendar-year peers.",
              fontsize=8, color="#777777")

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    df = load_data()
    fig = plot(df)
    fig.savefig(OUT_PATH, dpi=300, bbox_inches="tight")
    print(f"saved {OUT_PATH}")
