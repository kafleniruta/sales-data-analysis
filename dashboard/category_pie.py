import pandas as pd
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt


def render(df: pd.DataFrame, height: int = 220, on_select=None, key=None):
    """Pie chart of sales share by category."""
    if df is None or df.empty:
        st.info("No data available for category distribution.")
        return
    if "category" not in df.columns or "sales" not in df.columns:
        st.warning("Required columns 'category' or 'sales' missing.")
        return

    cat_sales = df.groupby("category")["sales"].sum().reset_index()
    mpl_colors = plt.rcParams.get("axes.prop_cycle").by_key().get("color", None)
    fig = px.pie(cat_sales, names="category", values="sales", hole=0.0, color_discrete_sequence=mpl_colors)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=24, b=8),
        paper_bgcolor="#f0f0f0",
        plot_bgcolor="#f0f0f0",
    )
    kwargs = {}
    if on_select:
        kwargs['on_select'] = on_select
    if key:
        kwargs['key'] = key
    st.plotly_chart(fig, use_container_width=True, **kwargs)
    
