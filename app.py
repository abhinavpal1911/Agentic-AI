"""Streamlit app: Agentic Campaign Optimization Engine (initial shell)

This is an initial scaffold with pages and basic charts. Run with:

    streamlit run app.py

"""
from io import BytesIO
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import time

from data.generator import generate_marketing_data
from utils.metrics import compute_group_metrics


ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "marketing_data.xlsx"


@st.cache_data
def load_data(n_rows: int = 500):
    # If generated Excel exists, read it; otherwise generate a new one
    if DATA_PATH.exists():
        df = pd.read_excel(DATA_PATH)
    else:
        df = generate_marketing_data(n_rows=n_rows, export_path=str(DATA_PATH))
    return df


def campaign_dashboard(df: pd.DataFrame):
    st.header("Campaign Dashboard")
    st.markdown(
        "This dashboard shows the campaign mix the agent is monitoring in real time. Use these visuals to understand spend efficiency, platform performance, and the campaigns that need attention."
    )

    summary = {
        "Total Spend": f"${df['Spend ($)'].sum():,.0f}",
        "Total Conversions": f"{int(df['Conversions'].sum()):,}",
        "Average CPA": f"${(df['Spend ($)'].sum() / df['Conversions'].sum()):.2f}",
        "Average ROAS": f"{(df['Revenue ($)'].sum() / df['Spend ($)'].sum()):.2f}",
    }
    cols = st.columns(4)
    for label, value in summary.items():
        cols[list(summary.keys()).index(label)].metric(label, value)

    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        "Download campaign dataset",
        data=buffer,
        file_name="marketing_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.scatter(
            df,
            x="Spend ($)",
            y="Conversions",
            color="Platform",
            hover_data=["Audience Segment", "Ad Creative Name", "CTR", "CPA"],
            size="Impressions",
            title="Spend vs Conversions",
            labels={"Spend ($)": "Spend", "Conversions": "Conversions"},
        )
        fig.update_layout(plot_bgcolor="white", legend_title_text="Platform")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        platform_agg = compute_group_metrics(df, group_by="Platform")
        platform_agg = platform_agg.sort_values("CPA")
        fig2 = px.bar(
            platform_agg,
            x="Platform",
            y="CPA",
            color="Platform",
            title="CPA by Platform",
            text_auto=".2f",
        )
        fig2.update_layout(showlegend=False, plot_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

        fig3 = px.bar(
            platform_agg,
            x="Platform",
            y="CTR",
            title="CTR by Platform",
            text_auto=".2%",
        )
        fig3.update_layout(showlegend=False, plot_bgcolor="white")
        st.plotly_chart(fig3, use_container_width=True)


def anomaly_detection(df: pd.DataFrame):
    st.header("Anomaly Detection: Identifying Underperformers")
    st.markdown(
        "The agent scans campaign performance and highlights audience segments that are missing expectations. In this workshop, underperformers are CPA > $50 or CTR < 0.5%."
    )

    agg = compute_group_metrics(df, group_by="Audience Segment")
    underperformers = agg[(agg["CPA"] > 50) | (agg["CTR"] < 0.005)].copy()
    underperformers = underperformers.sort_values(["CPA", "CTR"], ascending=[False, True])

    worst_ctr = agg.nsmallest(1, "CTR")["CTR"].iloc[0]
    worst_cpa = agg.nlargest(1, "CPA")["CPA"].iloc[0]

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Flagged Segments", len(underperformers), delta=f"{len(underperformers)} under threshold")
    kpi2.metric("Worst CPA", f"${worst_cpa:.2f}")
    kpi3.metric("Lowest CTR", f"{worst_ctr:.2%}")

    st.markdown("---")
    st.subheader("Underperforming Segments Table")

    if underperformers.empty:
        st.success("No current audience segments meet the underperformer criteria.")
        return

    underperformers_display = underperformers.copy()
    underperformers_display["CTR"] = underperformers_display["CTR"].map("{:.2%}".format)
    underperformers_display["CPA"] = underperformers_display["CPA"].map("${:,.2f}".format)
    underperformers_display["ROAS"] = underperformers_display["ROAS"].map("{:.2f}".format)
    st.dataframe(underperformers_display.reset_index(drop=True), use_container_width=True)

    st.markdown(
        "**Why this matters:** underperforming segments are where the agent will suggest creative changes and budget shifts to improve efficiency."
    )


def agentic_creative_optimization(df: pd.DataFrame):
    st.header("Agentic Creative Optimization")
    st.markdown(
        "The AI Agent reviews the selected segment and proposes fresh ad copy that speaks directly to the audience's motivations."
    )

    agg = compute_group_metrics(df, group_by="Audience Segment")
    underperformers = agg[(agg["CPA"] > 50) | (agg["CTR"] < 0.005)].copy()
    segments = underperformers["Audience Segment"].tolist()

    if not segments:
        st.info("No underperformers to optimize at the moment.")
        return

    choice = st.selectbox("Choose a segment to optimize", segments)
    if st.button("Run AI Agent"):
        placeholder = st.empty()
        progress = placeholder.progress(0)
        for pct in range(1, 101, 20):
            time.sleep(0.3)
            progress.progress(pct)
        placeholder.empty()

        analysis = (
            f"The agent identifies that **{choice}** is suffering from low engagement. "
            "The current creative likely feels too generic for this audience, and the message does not match the segment's core pain points. "
            "The agent recommends stronger emotional hooks, clearer value, and a more urgent call to action."
        )
        st.subheader("Agent Analysis")
        st.write(analysis)

        st.subheader("Recommended Ad Copy Variants")
        examples = [
            {
                "headline": f"Designed for {choice.split()[0]}s Who Want Better Results",
                "primary_text": "Stop wasting budget on ads that don't convert. Discover a smarter path to more clicks, more leads, and better ROI.",
            },
            {
                "headline": f"{choice.split()[0]} Exclusive: Save Time, Save Money",
                "primary_text": "Targeted messaging crafted for your lifestyle — turn attention into action with relevance, clarity, and trust.",
            },
            {
                "headline": f"Ready for {choice}? Try the smarter creative approach",
                "primary_text": "Tailored messaging that speaks to your audience's goals. Click to activate a higher-performing campaign strategy.",
            },
        ]

        cards = st.columns(3)
        for idx, variant in enumerate(examples):
            with cards[idx]:
                st.markdown(f"### Variant {idx + 1}")
                st.markdown(f"**Headline:** {variant['headline']}")
                st.markdown(f"**Primary Text:** {variant['primary_text']}")
                st.markdown("---")


def budget_reallocation_engine(df: pd.DataFrame):
    st.header("Budget Reallocation Engine")
    st.markdown(
        "The agent recommends shifting budget away from underperforming segments and amplifying the budget for the top performers that are most likely to drive conversions."
    )

    agg = compute_group_metrics(df, group_by="Audience Segment")
    under = agg[(agg["CPA"] > 50) | (agg["CTR"] < 0.005)].copy()
    top = agg.sort_values("ROAS", ascending=False).head(3).copy()
    current_alloc = agg[["Audience Segment", "Spend ($)"]].set_index("Audience Segment")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Current Budget Allocation")
        st.bar_chart(current_alloc)
    with col2:
        st.subheader("Top 3 Forecasted Segments")
        st.dataframe(top[["Audience Segment", "ROAS", "CPA", "CTR"]].reset_index(drop=True).style.format({"ROAS": "{:.2f}", "CPA": "${:.2f}", "CTR": "{:.2%}"}), use_container_width=True)

    if under.empty:
        st.info("All segments are currently performing within acceptable thresholds.")
        return

    freed = (under["Spend ($)"] * 0.2).sum()
    top_roas = top["ROAS"].clip(lower=0.01)
    top_share = top_roas / top_roas.sum()
    allocation = (top_share * freed).rename("Added Spend ($)")

    recommended = current_alloc.copy()
    for _, row in under.iterrows():
        recommended.loc[row["Audience Segment"], "Spend ($)"] -= row["Spend ($)"] * 0.2
    for seg, amt in allocation.items():
        recommended.loc[seg, "Spend ($)"] += amt

    st.markdown("---")
    columns = st.columns(2)
    with columns[0]:
        st.subheader("Current spend")
        st.dataframe(current_alloc.style.format({"Spend ($)": "${:,.2f}"}), use_container_width=True)
    with columns[1]:
        st.subheader("Recommended spend")
        st.dataframe(recommended.style.format({"Spend ($)": "${:,.2f}"}), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Recommended allocation chart")
        st.bar_chart(recommended)
    with col4:
        st.subheader("Budget freed from underperformers")
        st.dataframe(allocation.reset_index().rename(columns={"index": "Audience Segment"}).style.format({"Added Spend ($)": "${:,.2f}"}), use_container_width=True)

    conversion_rate = agg.set_index("Audience Segment")["Conversions"] / agg.set_index("Audience Segment")["Spend ($)"]
    conversion_rate = conversion_rate.replace([pd.NA, float("inf")], 0).fillna(0)
    projected_conversions = (recommended["Spend ($)"] * conversion_rate).sum()
    current_conversions = agg["Conversions"].sum()

    st.markdown("---")
    st.metric("Current Total Conversions", int(current_conversions), delta=None)
    st.metric("Projected Total Conversions", int(projected_conversions), delta=f"{int(projected_conversions - current_conversions):+d}")
    st.caption("Projection assumes linear conversion efficiency from current campaign performance.")


def main():
    st.set_page_config(page_title="Agentic Campaign Optimization Engine", layout="wide")

    st.sidebar.title("Agentic Workshop")
    st.sidebar.markdown(
        "The agentic engine detects campaign weaknesses, rewrites underperforming ad copy, and reallocates media spend for better ROI."
    )
    st.sidebar.info("Use the pages to explore data, diagnose problems, simulate an AI agent, and see a budget shift recommendation.")
    page = st.sidebar.radio(
        "Go to", ["Campaign Dashboard", "Anomaly Detection", "Agentic Creative Optimization", "Budget Reallocation Engine"]
    )

    df = load_data(500)

    if page == "Campaign Dashboard":
        campaign_dashboard(df)
    elif page == "Anomaly Detection":
        anomaly_detection(df)
    elif page == "Agentic Creative Optimization":
        agentic_creative_optimization(df)
    elif page == "Budget Reallocation Engine":
        budget_reallocation_engine(df)


if __name__ == "__main__":
    main()
