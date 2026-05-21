"""Dummy marketing data generator

Generates a realistic pandas DataFrame with marketing campaign data,
calculates derived metrics, intentionally skews a few segments to perform poorly,
and exports the result to an Excel file.
"""
from faker import Faker
import numpy as np
import pandas as pd
import os

fake = Faker()


def generate_marketing_data(n_rows: int = 500, export_path: str = "data/marketing_data.xlsx") -> pd.DataFrame:
    """Generate dummy marketing data and export to Excel.

    Args:
        n_rows: Number of rows to generate.
        export_path: Path to write Excel file (relative to project root).

    Returns:
        pd.DataFrame: Generated marketing dataset with derived metrics.
    """
    rng = np.random.default_rng(42)

    platforms = ["Meta", "Google", "LinkedIn"]
    audience_segments = [
        "Tech Bros 25-34",
        "Soccer Moms",
        "Budget-Conscious Seniors 65+",
        "Fitness Enthusiasts 18-24",
        "Eco Conscious Millennials 30-40",
        "Luxury Shoppers 35-44",
        "Gaming Geeks 18-35",
    ]

    rows = []
    for i in range(n_rows):
        platform = rng.choice(platforms)
        segment = rng.choice(audience_segments)
        creative = f"{segment.split()[0]} Creative {rng.integers(1,10)}"

        # Base spend and scale by platform
        base_spend = float(rng.normal(200, 80))
        if platform == "Google":
            base_spend *= 1.2
        if platform == "LinkedIn":
            base_spend *= 1.1

        spend = max(20.0, round(base_spend + rng.normal(0, 50), 2))

        # Impressions depend on spend with some noise
        impressions = int(max(1000, rng.poisson(spend * 20)))

        # Click-through tendencies by segment
        ctr_common = {
            "Tech Bros 25-34": 0.006,
            "Soccer Moms": 0.01,
            "Budget-Conscious Seniors 65+": 0.004,
            "Fitness Enthusiasts 18-24": 0.012,
            "Eco Conscious Millennials 30-40": 0.009,
            "Luxury Shoppers 35-44": 0.008,
            "Gaming Geeks 18-35": 0.013,
        }

        # Intentionally skew a few segments to be underperformers
        if segment in ["Tech Bros 25-34", "Budget-Conscious Seniors 65+", "Luxury Shoppers 35-44"]:
            ctr = max(0.001, rng.normal(ctr_common[segment] * 0.4, 0.002))  # lower CTR
        else:
            ctr = max(0.001, rng.normal(ctr_common[segment], 0.002))

        clicks = int(max(0, round(impressions * ctr)))

        # Conversion rate roughly proportional to CTR but with noise
        conv_rate = max(0.0, rng.normal(0.08 * ctr / 0.01, 0.02))
        conversions = int(round(clicks * conv_rate))

        # Average order value varies by segment
        aov_map = {
            "Tech Bros 25-34": 80,
            "Soccer Moms": 45,
            "Budget-Conscious Seniors 65+": 30,
            "Fitness Enthusiasts 18-24": 35,
            "Eco Conscious Millennials 30-40": 60,
            "Luxury Shoppers 35-44": 220,
            "Gaming Geeks 18-35": 70,
        }

        aov = rng.normal(aov_map[segment], aov_map[segment] * 0.15)
        revenue = max(0.0, conversions * aov)

        rows.append(
            {
                "Campaign ID": f"CAMP-{1000 + i}",
                "Platform": platform,
                "Audience Segment": segment,
                "Ad Creative Name": creative,
                "Spend ($)": round(spend, 2),
                "Impressions": impressions,
                "Clicks": clicks,
                "Conversions": conversions,
                "Revenue ($)": round(revenue, 2),
            }
        )

    df = pd.DataFrame(rows)

    # Derived metrics
    df["CTR"] = (df["Clicks"] / df["Impressions"]).fillna(0)
    # CPA: handle zero conversions
    df["CPA"] = df.apply(lambda r: r["Spend ($)"] / r["Conversions"] if r["Conversions"] > 0 else np.nan, axis=1)
    df["ROAS"] = df.apply(lambda r: (r["Revenue ($)"] / r["Spend ($)"]) if r["Spend ($)"] > 0 else np.nan, axis=1)

    # Mark extremely bad CPA for the intentionally bad segments
    mask_bad = df["Audience Segment"].isin(["Tech Bros 25-34", "Budget-Conscious Seniors 65+", "Luxury Shoppers 35-44"]) & (df["Conversions"] <= 2)
    df.loc[mask_bad, "CPA"] = df.loc[mask_bad, "CPA"].fillna(999.0)

    # Ensure export directory exists
    export_dir = os.path.dirname(export_path)
    if export_dir and not os.path.exists(export_dir):
        os.makedirs(export_dir, exist_ok=True)

    # Export to Excel
    df.to_excel(export_path, index=False)

    return df


if __name__ == "__main__":
    # Quick smoke test generation when run directly
    df = generate_marketing_data(500, export_path=os.path.join("data", "marketing_data.xlsx"))
    print("Generated", len(df), "rows and exported to data/marketing_data.xlsx")
