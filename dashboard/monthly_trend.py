import pandas as pd
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt


def render(df: pd.DataFrame, height: int = 220, on_select=None, key=None):
    """Monthly sales trend by year. Expects `order_year` and `order_month` or `order_date`."""
    if df is None or df.empty:
        st.info("No data available for monthly trend.")
        return

    df = df.copy()
    if "order_year" not in df.columns or "order_month" not in df.columns:
        if "order_date" in df.columns:
            df["_dt"] = pd.to_datetime(df["order_date"], errors="coerce")
            df["order_year"] = df["_dt"].dt.year
            df["order_month"] = df["_dt"].dt.month
        else:
            st.warning("Missing order_year/order_month or order_date columns.")
            return

    monthly = (
        df.groupby(["order_year", "order_month"])["sales"].sum().reset_index().rename(
            columns={"order_year": "year", "order_month": "month"}
        )
    )
    if monthly.empty:
        st.info("No monthly sales data to display.")
        return

    # use matplotlib color cycle to match notebook colors
    mpl_colors = plt.rcParams.get("axes.prop_cycle").by_key().get("color", None)
    # plot sales in thousands to match the notebook
    monthly["sales_k"] = monthly["sales"] / 1e3
    fig = px.line(
        monthly,
        x="month",
        y="sales_k",
        color=monthly["year"].astype(str),
        markers=True,
        labels={"month": "Month", "sales_k": "Sales ($ Thousands)", "color": "Year"},
        color_discrete_sequence=mpl_colors,
    )
    fig.update_xaxes(tickmode="array", tickvals=list(range(1, 13)), ticktext=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=24, b=6),
        legend=dict(title="Year", orientation="h", yanchor="bottom", y=1.02),
        paper_bgcolor="#f0f0f0",
        plot_bgcolor="#f0f0f0",
    )
    kwargs = {}
    if on_select:
        kwargs['on_select'] = on_select
    if key:
        kwargs['key'] = key
    st.plotly_chart(fig, use_container_width=True, **kwargs)
