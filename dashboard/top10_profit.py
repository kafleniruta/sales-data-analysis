import pandas as pd
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt


def render(df: pd.DataFrame, height: int = 220, on_select=None, key=None):
    """Top 10 profit-making products as horizontal bar chart."""
    if df is None or df.empty:
        st.info("No product profit data available.")
        return
    if "product_name" not in df.columns or "profit" not in df.columns:
        st.warning("Required columns 'product_name' or 'profit' missing.")
        return

    top10 = df.groupby("product_name")["profit"].sum().sort_values(ascending=False).head(10).reset_index()
    if top10.empty:
        st.info("No product profit data to show.")
        return
    mpl_colors = plt.rcParams.get("axes.prop_cycle").by_key().get("color", None)
    base_color = mpl_colors[0] if mpl_colors else "#4C72B0"
    fig = px.bar(top10, x="profit", y="product_name", orientation="h", labels={"profit": "Total Profit", "product_name": "Product"}, color_discrete_sequence=[base_color])
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=24, b=8),
        paper_bgcolor="#f0f0f0",
        plot_bgcolor="#f0f0f0",
    )
    fig.update_yaxes(autorange="reversed")
    kwargs = {}
    if on_select:
        kwargs['on_select'] = on_select
    if key:
        kwargs['key'] = key
    st.plotly_chart(fig, width='stretch', **kwargs)
