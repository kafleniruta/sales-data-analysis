import pandas as pd
import plotly.express as px
import streamlit as st


def render(df: pd.DataFrame, height: int = 220, on_select=None, key=None):
    """Horizontal bar of loss-making orders by sub-category."""
    if df is None or df.empty:
        st.info("No data for loss orders.")
        return
    if not {"profit", "order_id", "sub_category"}.issubset(df.columns):
        st.warning("Required columns 'profit', 'order_id', 'sub_category' missing.")
        return

    df = df.copy()
    df["is_loss"] = df["profit"] < 0
    loss_by_sub = (
        df[df["is_loss"]]
        .groupby("sub_category")["order_id"]
        .count()
        .sort_values(ascending=True)
        .tail(15)
        .reset_index()
    )
    if loss_by_sub.empty:
        st.info("No loss-making orders to show.")
        return

    # color stronger loss categories differently
    median = loss_by_sub["order_id"].median()
    loss_by_sub["color"] = loss_by_sub["order_id"].apply(lambda v: "#d73027" if v > median else "#fc8d59")
    fig = px.bar(loss_by_sub, x="order_id", y="sub_category", orientation="h", text="order_id", color="color", color_discrete_map="identity")
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=24, b=8),
        paper_bgcolor="#f0f0f0",
        plot_bgcolor="#f0f0f0",
    )
    # keep the order as produced above (ascending within the selected tail)
    kwargs = {}
    if on_select:
        kwargs['on_select'] = on_select
    if key:
        kwargs['key'] = key
    st.plotly_chart(fig, use_container_width=True, **kwargs)
