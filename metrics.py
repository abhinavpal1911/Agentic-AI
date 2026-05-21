"""Utility functions for marketing metrics."""
import pandas as pd


def compute_group_metrics(df: pd.DataFrame, group_by: str = "Audience Segment") -> pd.DataFrame:
    """Aggregate spend, conversions and compute CTR/CPA/ROAS at group level.

    Args:
        df: Full campaign DataFrame
        group_by: Column to group by

    Returns:
        pd.DataFrame: Aggregated metrics per group
    """
    agg = df.groupby(group_by).agg(
        {
            "Spend ($)": "sum",
            "Impressions": "sum",
            "Clicks": "sum",
            "Conversions": "sum",
            "Revenue ($)": "sum",
        }
    )

    agg["CTR"] = (agg["Clicks"] / agg["Impressions"]).fillna(0)
    agg["CPA"] = agg.apply(lambda r: r["Spend ($)"] / r["Conversions"] if r["Conversions"] > 0 else float("nan"), axis=1)
    agg["ROAS"] = agg.apply(lambda r: (r["Revenue ($)"] / r["Spend ($)"]) if r["Spend ($)"] > 0 else float("nan"), axis=1)

    agg = agg.reset_index()
    return agg
