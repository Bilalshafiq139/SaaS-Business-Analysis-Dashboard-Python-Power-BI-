# Power BI Dashboard Notes

The Power BI dashboard is stored at `dashboard/saas_growth_dashboard.pbix`.

Recommended updates before publishing screenshots:

- Replace any ROI measure based on `profitMargin / askingPrice` with `profitToAskingPrice` or `paybackYears`.
- Add KPI cards for total listings, median asking price, median profit margin, median payback period, and count of profitable listings.
- Add a location visual that excludes locations with fewer than two listings or clearly flags small samples.
- Add a scatter plot for annual revenue vs asking price, with growth segment as the legend.
- Add a table of potential acquisition targets ranked by high profit-to-price ratio, positive profit, and reasonable revenue multiple.
- Add a short methodology tooltip or text block explaining each KPI.

Suggested DAX measures:

```DAX
Median Asking Price = MEDIAN(saas_cleaned_data[askingPrice])

Median Profit Margin = MEDIAN(saas_cleaned_data[profitMargin])

Median Payback Years = MEDIAN(saas_cleaned_data[paybackYears])

Profit-to-Price Ratio = DIVIDE(
    SUM(saas_cleaned_data[totalProfitAnnual]),
    SUM(saas_cleaned_data[askingPrice])
)

Profitable Listings = CALCULATE(
    COUNTROWS(saas_cleaned_data),
    saas_cleaned_data[totalProfitAnnual] > 0
)
```
