# Power BI Dashboard Notes

The Power BI dashboard is stored at `dashboard/saas_growth_dashboard.pbix`.

## Dashboard Design & DAX Measures

The dashboard includes the following KPI and visual design recommendations:

- Use `profitToAskingPrice` or `paybackYears` instead of ROI measures based on `profitMargin / askingPrice`.
- Display KPI cards for total listings, median asking price, median profit margin, median payback period, and profitable listings.
- Exclude or clearly identify locations with fewer than two listings when comparing countries.
- Include a scatter plot showing annual revenue versus asking price with growth category as the legend.
- Include a ranked acquisition opportunities table using positive profit, strong profit-to-price ratio, and reasonable revenue multiples.
- Add concise methodology notes explaining each KPI.

## Suggested DAX Measures

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