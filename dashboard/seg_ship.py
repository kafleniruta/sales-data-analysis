import pandas as pd
import plotly.express as px
import streamlit as st


def render(df: pd.DataFrame, height: int = 220, on_select=None, key=None):
    """Stacked 100% bar showing ship mode mix by segment."""
    if df is None or df.empty:
        st.info("No data available for ship mode mix.")
        return
    if not {"segment", "ship_mode", "sales"}.issubset(df.columns):
        st.warning("Required columns 'segment', 'ship_mode', or 'sales' missing.")
        return

    seg_ship = df.groupby(["segment", "ship_mode"])["sales"].sum().unstack(fill_value=0)
    seg_ship = seg_ship.div(seg_ship.sum(axis=1), axis=0) * 100
    seg_ship = seg_ship.reset_index().melt(id_vars="segment", var_name="ship_mode", value_name="share_pct")
    if seg_ship.empty:
        st.info("No segment/ship_mode data to show.")
        return

    fig = px.bar(seg_ship, x="segment", y="share_pct", color="ship_mode", labels={"share_pct": "Share (%)"}, color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(
        barmode="stack",
        height=height,
        margin=dict(l=8, r=8, t=24, b=8),
        legend=dict(font=dict(size=9)),
        paper_bgcolor="#f0f0f0",
        plot_bgcolor="#f0f0f0",
    )
    fig.update_yaxes(tickformat=".0f")
    kwargs = {}
    if on_select:
        kwargs['on_select'] = on_select
    if key:
        kwargs['key'] = key
    st.plotly_chart(fig, use_container_width=True, **kwargs)
