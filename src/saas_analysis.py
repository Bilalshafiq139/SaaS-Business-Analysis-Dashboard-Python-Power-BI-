"""Clean SaaS listings data and generate portfolio-ready analysis assets."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
RAW_DATA = ROOT / "data" / "raw" / "saas_businesses_data.csv"
PROCESSED_DATA = ROOT / "data" / "processed" / "saas_cleaned_data.csv"
FIGURES_DIR = ROOT / "assets" / "figures"
SUMMARY_REPORT = ROOT / "docs" / "analysis_summary.md"
TEXT_MARKERS_TO_REMOVE = [
    "\u2705",
    "\U0001f4cc",
    "\U0001f4c8",
    "\u27a1\ufe0f",
    "\u27a1",
    "\ufe0f",
]


def to_markdown_table(frame: pd.DataFrame) -> str:
    """Render a small DataFrame as Markdown without optional dependencies."""
    display_frame = frame.reset_index()
    headers = list(display_frame.columns)
    rows = display_frame.astype(object).where(pd.notna(display_frame), "").values.tolist()

    def format_value(value: object) -> str:
        if isinstance(value, float):
            return f"{value:.2f}"
        return str(value)

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(format_value(value) for value in row) + " |")
    return "\n".join(lines)


def categorize_growth(value: float) -> str:
    """Bucket annual growth into business-friendly segments."""
    if value >= 75:
        return "High Growth"
    if value >= 25:
        return "Medium Growth"
    return "Low Growth"


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()

    df["listingDate"] = pd.to_datetime(df["date"], errors="coerce")
    df["dateFounded"] = pd.to_datetime(df["dateFounded"], errors="coerce")

    df["totalGrowthAnnual"] = df["totalGrowthAnnual"].fillna(
        df["totalGrowthAnnual"].median()
    )
    df["location"] = df["location"].fillna("Unknown")
    df["customers"] = df["customers"].fillna("Not Provided")
    df["techStack"] = df["techStack"].fillna("Not Provided")

    df = df.dropna(subset=["listingHeadline"]).copy()

    # Use the listing year instead of the current year so results are reproducible.
    df["companyAge"] = df["listingDate"].dt.year - df["dateFounded"].dt.year
    df["companyAge"] = df["companyAge"].clip(lower=0)

    df["profitMargin"] = df["totalProfitAnnual"] / df["totalRevenueAnnual"]
    df["askingPriceToRevenue"] = df["askingPrice"] / df["totalRevenueAnnual"]
    df["profitToAskingPrice"] = df["totalProfitAnnual"] / df["askingPrice"]
    df["paybackYears"] = df["askingPrice"] / df["totalProfitAnnual"]
    df.loc[df["totalProfitAnnual"] <= 0, "paybackYears"] = pd.NA
    df["estimatedValuation"] = df["totalRevenueAnnual"] * df["revenueMultiple"]
    df["growthCategory"] = df["totalGrowthAnnual"].apply(categorize_growth)

    text_columns = [
        column
        for column in df.columns
        if pd.api.types.is_string_dtype(df[column])
        or pd.api.types.is_object_dtype(df[column])
    ]
    for column in text_columns:
        df[column] = df[column].astype("string")
        for marker in TEXT_MARKERS_TO_REMOVE:
            df[column] = df[column].str.replace(marker, "", regex=False)
        df[column] = df[column].str.replace("\u2022", "-", regex=False).str.strip()

    numeric_rounding = {
        "profitMargin": 4,
        "askingPriceToRevenue": 2,
        "profitToAskingPrice": 4,
        "paybackYears": 2,
        "estimatedValuation": 2,
    }
    df = df.round(numeric_rounding)

    return df


def save_figures(df: pd.DataFrame) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(9, 5))
    order = ["Low Growth", "Medium Growth", "High Growth"]
    sns.barplot(
        data=df,
        x="growthCategory",
        y="profitMargin",
        order=order,
        errorbar=None,
        color="#2f6f73",
    )
    plt.title("Average Profit Margin by Growth Segment")
    plt.xlabel("Growth Segment")
    plt.ylabel("Average Profit Margin")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "profit_margin_by_growth_segment.png", dpi=160)
    plt.close()

    plt.figure(figsize=(9, 5))
    top_locations = (
        df[df["location"] != "Unknown"]
        .groupby("location")
        .agg(listings=("location", "size"), median_payback=("paybackYears", "median"))
        .query("listings >= 2")
        .sort_values("median_payback")
        .head(10)
    )
    sns.barplot(
        data=top_locations.reset_index(),
        y="location",
        x="median_payback",
        color="#5b7c99",
    )
    plt.title("Median Payback Period by Location (2+ Listings)")
    plt.xlabel("Median Payback Period, Years")
    plt.ylabel("Location")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "median_payback_by_location.png", dpi=160)
    plt.close()

    plt.figure(figsize=(9, 5))
    sns.scatterplot(
        data=df,
        x="totalRevenueAnnual",
        y="askingPrice",
        hue="growthCategory",
        alpha=0.85,
    )
    plt.title("Asking Price vs Annual Revenue")
    plt.xlabel("Annual Revenue")
    plt.ylabel("Asking Price")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "asking_price_vs_revenue.png", dpi=160)
    plt.close()


def write_summary(df: pd.DataFrame, raw_rows: int) -> None:
    SUMMARY_REPORT.parent.mkdir(parents=True, exist_ok=True)

    growth_summary = (
        df.groupby("growthCategory")
        .agg(
            listings=("growthCategory", "size"),
            median_profit_margin=("profitMargin", "median"),
            median_growth=("totalGrowthAnnual", "median"),
            median_payback_years=("paybackYears", "median"),
        )
        .sort_index()
    )

    location_summary = (
        df[df["location"] != "Unknown"]
        .groupby("location")
        .agg(
            listings=("location", "size"),
            median_profit_to_price=("profitToAskingPrice", "median"),
            median_payback_years=("paybackYears", "median"),
        )
        .query("listings >= 2")
        .sort_values("median_profit_to_price", ascending=False)
        .head(10)
    )

    correlations = {
        "Annual revenue vs asking price": df["totalRevenueAnnual"].corr(
            df["askingPrice"]
        ),
        "Annual profit vs asking price": df["totalProfitAnnual"].corr(
            df["askingPrice"]
        ),
        "Growth vs revenue multiple": df["totalGrowthAnnual"].corr(
            df["revenueMultiple"]
        ),
        "Company age vs growth": df["companyAge"].corr(df["totalGrowthAnnual"]),
    }

    lines = [
        "# SaaS Listings Analysis Summary",
        "",
        f"- Raw listings: {raw_rows}",
        f"- Cleaned listings: {len(df)}",
        f"- Rows removed because of missing listing headline: {raw_rows - len(df)}",
        f"- Listings with unknown location after cleaning: {(df['location'] == 'Unknown').sum()}",
        f"- Listings with negative annual profit: {(df['totalProfitAnnual'] < 0).sum()}",
        "",
        "## Growth Segment Summary",
        "",
        to_markdown_table(growth_summary),
        "",
        "## Location Summary",
        "",
        "Locations with fewer than two listings are excluded from this ranking to reduce sample-size noise.",
        "",
        to_markdown_table(location_summary),
        "",
        "## Correlations",
        "",
    ]

    for label, value in correlations.items():
        lines.append(f"- {label}: {value:.2f}")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `profitToAskingPrice` is used as the acquisition return proxy: annual profit divided by asking price.",
            "- `paybackYears` estimates how many years of current annual profit are needed to recover the asking price.",
            "- Extreme growth values are retained but should be interpreted carefully because early-stage listings can distort averages.",
            "- Country/location rankings are directional because several locations have small sample sizes.",
        ]
    )

    SUMMARY_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    raw = pd.read_csv(RAW_DATA)
    cleaned = clean_data(raw)

    PROCESSED_DATA.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(PROCESSED_DATA, index=False)

    save_figures(cleaned)
    write_summary(cleaned, raw_rows=len(raw))

    print(f"Saved cleaned data to {PROCESSED_DATA.relative_to(ROOT)}")
    print(f"Saved figures to {FIGURES_DIR.relative_to(ROOT)}")
    print(f"Saved summary to {SUMMARY_REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
