# SaaS Listings Analysis Summary

- Raw listings: 126
- Cleaned listings: 113
- Rows removed because of missing listing headline: 13
- Listings with unknown location after cleaning: 17
- Listings with negative annual profit: 7

## Growth Segment Summary

| growthCategory | listings | median_profit_margin | median_growth | median_payback_years |
| --- | --- | --- | --- | --- |
| High Growth | 28 | 0.34 | 103.00 | 10.91 |
| Low Growth | 44 | 0.10 | 11.09 | 15.32 |
| Medium Growth | 41 | 0.30 | 25.00 | 11.90 |

## Location Summary

Locations with fewer than two listings are excluded from this ranking to reduce sample-size noise.

| location | listings | median_profit_to_price | median_payback_years |
| --- | --- | --- | --- |
| Spain | 3 | 0.08 | 11.96 |
| India | 3 | 0.08 | 13.24 |
| Singapore | 2 | 0.07 | 24.16 |
| United States | 40 | 0.06 | 13.33 |
| United Kingdom | 12 | 0.06 | 10.79 |
| Canada | 10 | 0.05 | 11.80 |
| Mexico | 4 | 0.04 | 14.64 |
| Australia | 4 | 0.03 | 29.07 |
| France | 6 | 0.00 | 123.33 |
| Estonia | 3 | 0.00 | 7275.89 |

## Correlations

- Annual revenue vs asking price: 0.75
- Annual profit vs asking price: 0.51
- Growth vs revenue multiple: -0.06
- Company age vs growth: -0.12

## Notes

- `profitToAskingPrice` is used as the acquisition return proxy: annual profit divided by asking price.
- `paybackYears` estimates how many years of current annual profit are needed to recover the asking price.
- Extreme growth values are retained but should be interpreted carefully because early-stage listings can distort averages.
- Country/location rankings are directional because several locations have small sample sizes.
