import pandas as pd
import streamlit as st
import plotly.express as px


def render(df: pd.DataFrame, height: int = 220, on_select=None, key=None):
    """Render correlation heatmap with fixed dashboard height."""

    if df is None or df.empty:
        st.info("No data available for correlation matrix.")
        return

    cols = [c for c in ["sales", "profit", "discount", "quantity", "shipping_cost"] if c in df.columns]

    if len(cols) < 2:
        st.warning("Not enough numeric columns to compute correlation.")
        return

    corr = df[cols].corr().round(2)
    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="equal",
    )
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=24, b=8),
        paper_bgcolor="#f0f0f0",
        plot_bgcolor="#f0f0f0",
        coloraxis_colorbar=dict(len=0.85, thickness=12),
    )
    fig.update_xaxes(tickangle=45)
    kwargs = {}
    if on_select:
        kwargs["on_select"] = on_select
    if key:
        kwargs["key"] = key
    st.plotly_chart(fig, use_container_width=True, **kwargs)