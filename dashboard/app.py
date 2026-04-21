import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import importlib
import plotly.express as px

# Ensure project root is importable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import utils dynamica--lly
utils = importlib.import_module("dashboard.utils")
load_data = utils.load_data

# Import chart modules dynamically
def _import_mod(name):
    try:
        return importlib.import_module(f"dashboard.{name}")
    except Exception:
        return None

monthly_trend = _import_mod("monthly_trend")
corr_heatmap = _import_mod("corr_heatmap")
category_pie = _import_mod("category_pie")
top10_profit = _import_mod("top10_profit")
loss_by_subcat = _import_mod("loss_by_subcat")
profit_margin_subcat = _import_mod("profit_margin_subcat")
category_bar = _import_mod("category_bar")
seg_ship = _import_mod("seg_ship")

# Initialize session state
if 'selected_categories' not in st.session_state:
    st.session_state.selected_categories = []
if 'selected_segments' not in st.session_state:
    st.session_state.selected_segments = []

# Callbacks for chart selections
def update_category_filter():
    event = st.session_state.get('plotly_event', {})
    if event and 'selection' in event and event['selection'].get('points'):
        selected = [p.get('label') for p in event['selection']['points'] if 'label' in p]
        st.session_state.selected_categories = selected
        st.rerun()

def update_segment_filter():
    event = st.session_state.get('plotly_event', {})
    if event and 'selection' in event and event['selection'].get('points'):
        selected = [p.get('x') for p in event['selection']['points'] if 'x' in p]
        st.session_state.selected_segments = selected
        st.rerun()

def inject_compact_css():
    css = """
    <style>
    /* Reduce outer spacing */
    .block-container {
        padding-top: 0.2rem;
        padding-bottom: 0.2rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
        max-width: 100%;
    }

    /* KPI container (BLACK BORDER) */
    .kpi-card {
        border: 2px solid black;
        border-radius: 8px;
        padding: 6px;
        background-color: white;
        text-align: center;
    }

    .kpi-value {
        font-size: 16px;
        font-weight: 800;
        color: #000;
    }

    .kpi-label {
        font-size: 10px;
        color: #444;
        margin-top: 2px;
    }

    /* Chart container (NO BORDER) */
    .stPlotlyChart > div {
        border: none;
        border-radius: 8px;
        padding: 4px;
        background-color: #f0f0f0;
        overflow: hidden;
    }

    /* Matplotlib chart container (NO BORDER) */
    .stPyplot > div {
        border: none;
        border-radius: 8px;
        padding: 4px;
        background-color: #f0f0f0;
        overflow: hidden;
    }

    /* Force all Plotly charts to equal fixed height and remove internal scroll */
    .stPlotlyChart, .stPlotlyChart > div, .stPlotlyChart .plotly-graph-div {
        min-height: 240px !important;
        max-height: 240px !important;
        overflow: hidden !important;
    }

    /* Force all Matplotlib charts to equal fixed height and remove internal scroll */
    .stPyplot, .stPyplot > div {
        min-height: 240px !important;
        max-height: 240px !important;
        overflow: hidden !important;
    }

    /* Disable scrolling inside chart containers */
    .stPlotlyChart .plotly-graph-div {
        overflow: hidden !important;
    }
    .stPlotlyChart > div > div {
        overflow: hidden !important;
    }

    /* Chart title */
    .chart-title {
        font-weight: 700;
        text-align: center;
        font-size: 12px;
        margin: 0 0 2px 0;
    }

    /* Dashboard title in light gray */
    .dashboard-title-box {
        border-radius: 8px;
        background-color: #f0f0f0;
        color: #111;
        font-size: 28px;
        font-weight: 700;
        text-align: center;
        padding: 6px 10px;
        margin-bottom: 8px;
    }

    .filter-title-box {
        border-radius: 6px;
        background-color: #f0f0f0;
        color: #111;
        font-size: 20px;
        font-weight: 700;
        text-align: center;
        padding: 4px 8px;
        margin-bottom: 6px;
    }

    /* FILTER PANEL AS CONTAINER (BLACK BORDER) */
    section[data-testid="column"]:last-child {
        border: 2px solid black;
        border-radius: 8px;
        padding: 8px;
        background-color: #f0f0f0;
    }

    /* Remove extra gap between columns */
    .stColumns > div {
        gap: 4px;
    }

    /* Reduce margin of headers */
    h1 {
        margin-top: 0;
        margin-bottom: 0.5rem;
    }

    /* Remove Streamlit default top-right menu and header */
    #MainMenu {
        visibility: hidden;
    }
    header {
        visibility: hidden;
    }

    /* Remove footer */
    footer {
        display: none;
    }

    /* Adjust multiselect widget spacing */
    .stMultiSelect {
        margin-bottom: 4px;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Compute KPIs
def compute_kpis(df):
    total_sales = float(df["sales"].sum()) if "sales" in df.columns else 0.0
    total_profit = float(df["profit"].sum()) if "profit" in df.columns else 0.0
    avg_margin = float(df["profit_margin"].mean()) if "profit_margin" in df.columns else 0.0
    num_orders = int(df["order_id"].nunique()) if "order_id" in df.columns else int(len(df))
    customers = df["customer_id"].nunique() if "customer_id" in df.columns else (df["customer_name"].nunique() if "customer_name" in df.columns else 0)
    total_discount = float(df["discount"].sum()) if "discount" in df.columns else 0.0
    total_quantity = int(df["quantity"].sum()) if "quantity" in df.columns else 0
    avg_order_value = total_sales / num_orders if num_orders else 0.0
    return total_sales, total_profit, avg_margin, num_orders, customers, total_discount, total_quantity, avg_order_value

def main():
    st.set_page_config(page_title="Sales Dashboard", layout="wide", initial_sidebar_state="collapsed")
    inject_compact_css()
    st.markdown("<div class='dashboard-title-box'>Sales Dashboard</div>", unsafe_allow_html=True)

    # Load data
    df = load_data("cleandata.csv")
    if "order_date" in df.columns:
        df["_order_date_dt"] = pd.to_datetime(df["order_date"], errors="coerce")

    # === Right-side filter panel layout ===
    main_area, filter_panel = st.columns([4, 1], gap="small")

    with filter_panel:
        st.markdown("<div class='filter-title-box'>Filters</div>", unsafe_allow_html=True)
        category_choices = sorted(df["category"].dropna().unique().tolist()) if "category" in df.columns else []
        segment_choices = sorted(df["segment"].dropna().unique().tolist()) if "segment" in df.columns else []
        year_choices = sorted(df["order_year"].dropna().unique().tolist()) if "order_year" in df.columns else []

        sel_cat = st.multiselect("Category", category_choices, default=st.session_state.selected_categories or category_choices)
        sel_seg = st.multiselect("Segment", segment_choices, default=st.session_state.selected_segments or segment_choices)

        if "_order_date_dt" in df.columns and df["_order_date_dt"].notna().any():
            min_dt = df["_order_date_dt"].min()
            max_dt = df["_order_date_dt"].max()
            date_range = st.date_input("Order date range", value=(min_dt, max_dt))
        elif year_choices:
            sel_years = st.multiselect("Year", year_choices, default=year_choices)
            date_range = None
        else:
            date_range = None
            sel_years = []

        st.session_state.selected_categories = sel_cat
        st.session_state.selected_segments = sel_seg

    # Filter dataframe based on selection
    df_filtered = df.copy()
    if sel_cat:
        df_filtered = df_filtered[df_filtered["category"].isin(sel_cat)]
    if sel_seg:
        df_filtered = df_filtered[df_filtered["segment"].isin(sel_seg)]
    if date_range and isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df_filtered = df_filtered[(df_filtered["_order_date_dt"] >= start) & (df_filtered["_order_date_dt"] <= end)]
    if year_choices and not date_range:
        df_filtered = df_filtered[df_filtered["order_year"].isin(sel_years)]

    # === KPIs & Charts in main area ===
    with main_area:
        # KPI row
        total_sales, total_profit, avg_margin, num_orders, customers, total_discount, total_quantity, avg_order_value = compute_kpis(df_filtered)
        k1, k2, k3, k4, k5, k6 = st.columns([1, 1, 1, 1, 1, 1], gap="small")
        kpi_tpl = "<div class='kpi-card'><div class='kpi-value'>{icon} {value}</div><div class='kpi-label'>{label}</div></div>"
        k1.markdown(kpi_tpl.format(icon="💰", value=f"${total_sales:,.0f}", label="Total Sales"), unsafe_allow_html=True)
        k2.markdown(kpi_tpl.format(icon="📈", value=f"${total_profit:,.0f}", label="Total Profit"), unsafe_allow_html=True)
        k3.markdown(kpi_tpl.format(icon="🧾", value=f"{num_orders:,}", label="Orders"), unsafe_allow_html=True)
        k4.markdown(kpi_tpl.format(icon="🧾", value=f"${avg_order_value:,.2f}", label="Avg Order Value"), unsafe_allow_html=True)
        k5.markdown(kpi_tpl.format(icon="🔽", value=f"${total_discount:,.2f}", label="Total Discount"), unsafe_allow_html=True)
        k6.markdown(kpi_tpl.format(icon="📦", value=f"{total_quantity:,}", label="Total Quantity"), unsafe_allow_html=True)

        # Charts
        charts = [
            ("Sales Distribution", category_pie),
            ("Correlation Matrix", corr_heatmap),
            ("Ship Mode Mix by Segment (%)", seg_ship),
            ("Loss-Making Subcategories", loss_by_subcat),
            ("Monthly Sales Trend", monthly_trend),
        ]
        # Reduced chart height to 200px for better fit on a single screen
        chart_h = 240

        # --- Row 1: first 3 charts ---
        c1, c2, c3 = st.columns(3, gap="small")
        for i, (title, mod) in enumerate(charts[:3]):
            with [c1, c2, c3][i]:
                st.markdown(f"<div class='chart-title'>{title}</div>", unsafe_allow_html=True)
                if mod is not None and hasattr(mod, "render"):
                    if title == "Sales Distribution":
                        mod.render(df_filtered, height=chart_h, on_select=update_category_filter, key=f"chart_{i}")
                    elif title == "Ship Mode Mix by Segment (%)":
                        mod.render(df_filtered, height=chart_h, on_select=update_segment_filter, key=f"chart_{i}")
                    else:
                        mod.render(df_filtered, height=chart_h)

        # --- Row 2: last 2 charts ---
        c1, c2 = st.columns(2, gap="small")
        for i, (title, mod) in enumerate(charts[3:]):
            with [c1, c2][i]:
                st.markdown(f"<div class='chart-title'>{title}</div>", unsafe_allow_html=True)
                if mod is not None and hasattr(mod, "render"):
                    mod.render(df_filtered, height=chart_h, key=f"chart_{i+3}")

if __name__ == "__main__":
    main()