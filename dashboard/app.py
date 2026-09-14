import os
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="E-Commerce Sales & Profitability Executive Dashboard",
    page_icon="🛍️",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "data_warehouse.duckdb")

@st.cache_data(ttl=600)
def load_data():
    if not os.path.exists(DB_PATH):
        with st.spinner("⏳ First-time setup: Ingesting dataset and executing dbt ELT pipeline..."):
            import subprocess
            subprocess.run(["python", os.path.join(BASE_DIR, "run_pipeline.py")], check=True)
    
    if not os.path.exists(DB_PATH):
        return None, None, None, None

    con = duckdb.connect(DB_PATH, read_only=True)
    fct_daily = con.execute("SELECT * FROM fct_daily_sales").df()
    mart_cat = con.execute("SELECT * FROM mart_category_profitability").df()
    mart_prod = con.execute("SELECT * FROM mart_product_performance").df()
    mart_low = con.execute("SELECT * FROM mart_low_performers").df()
    con.close()
    return fct_daily, mart_cat, mart_prod, mart_low

st.title("🛍️ Small Business Sales & Profitability Executive Dashboard")
st.caption("Powered by dlt + DuckDB + dbt Data Marts | Real UCI Online Retail Dataset")

fct_daily, mart_cat, mart_prod, mart_low = load_data()

if fct_daily is None or fct_daily.empty:
    st.warning("⚠️ Warehouse data not detected. Please run `python run_pipeline.py` first!")
    st.stop()

# Sidebar Filters
st.sidebar.header("🔍 Dashboard Filters")
categories = ["All Categories"] + list(mart_cat['category'].unique())
selected_cat = st.sidebar.selectbox("Product Category", categories)

min_date = pd.to_datetime(fct_daily['order_date']).min().date()
max_date = pd.to_datetime(fct_daily['order_date']).max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Executive KPI Summary Cards
st.subheader("📌 Executive KPI Summary")
tot_rev = fct_daily['gross_revenue'].sum()
tot_cost = fct_daily['total_cost'].sum()
tot_profit = fct_daily['gross_profit'].sum()
avg_margin = (tot_profit / tot_rev * 100) if tot_rev > 0 else 0
tot_units = fct_daily['total_units_sold'].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Gross Revenue", f"${tot_rev:,.2f}")
c2.metric("Total Cost of Goods Sold", f"${tot_cost:,.2f}")
c3.metric("Net Gross Profit", f"${tot_profit:,.2f}", delta=f"{avg_margin:.1f}% Gross Margin")
c4.metric("Total Units Sold", f"{tot_units:,.0f}")

st.markdown("---")

# Layout Column 1: Sales Trend & Category Margins
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Revenue & Gross Profit Trend")
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=fct_daily['order_date'], y=fct_daily['gross_revenue'], name="Revenue ($)", line=dict(color="#1f77b4", width=2)))
    fig_trend.add_trace(go.Scatter(x=fct_daily['order_date'], y=fct_daily['gross_profit'], name="Gross Profit ($)", line=dict(color="#2ca02c", width=2)))
    fig_trend.update_layout(template="plotly_dark", height=380, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_trend, use_container_width=True)

with col_right:
    st.subheader("📊 Profit Margin % by Category")
    fig_cat = px.bar(
        mart_cat,
        x="category",
        y="category_revenue",
        color="margin_pct",
        color_continuous_scale="Blues",
        labels={"category_revenue": "Revenue ($)", "margin_pct": "Margin %"},
        hover_data=["gross_profit", "margin_pct"]
    )
    fig_cat.update_layout(template="plotly_dark", height=380, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_cat, use_container_width=True)

st.markdown("---")

# Section: Best Sellers & Volume Gap
st.subheader("🏆 Top 10 Best Sellers: Revenue vs Volume Gap Analysis")
top_rev = mart_prod.sort_values(by="total_revenue", ascending=False).head(10)

fig_prod = px.bar(
    top_rev,
    x="total_revenue",
    y="description",
    orientation="h",
    color="category",
    title="Top 10 Products by Revenue",
    hover_data=["units_sold", "revenue_rank", "volume_rank", "rank_gap"]
)
fig_prod.update_layout(template="plotly_dark", height=420, yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_prod, use_container_width=True)

# Section: Actionable Low-Performer Flag Alert Table
st.markdown("---")
st.subheader("⚠️ Actionable Low-Performer Alerts")
st.caption("Products flagged for high price/low velocity, stagnant stock, or below-target profit margins.")

if not mart_low.empty:
    st.dataframe(
        mart_low[["stock_code", "description", "category", "unit_price", "units_sold", "total_revenue", "margin_pct", "performance_flag", "recommended_action"]],
        use_container_width=True
    )
else:
    st.info("No low-performing products flagged.")
