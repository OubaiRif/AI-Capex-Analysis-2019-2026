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
        SUM(CASE WHEN metric='capex' THEN value END) AS capex,
        SUM(CASE WHEN metric='revenue' THEN value END) AS revenue
    FROM fin_data
    GROUP BY ticker, fiscal_year
) 
ORDER BY ticker, fiscal_year;