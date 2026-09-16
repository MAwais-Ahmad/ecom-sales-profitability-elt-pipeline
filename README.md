# 🛍️ Small Business E-Commerce Sales & Profitability Pipeline (ELT)

[![Live Streamlit Demo](https://img.shields.io/badge/Live%20Dashboard-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://ecom-sales-profitability.streamlit.app)
[![dbt Engine](https://img.shields.io/badge/dbt-DuckDB-FF694B?style=for-the-badge&logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![Dagster](https://img.shields.io/badge/Orchestration-Dagster-4F46E5?style=for-the-badge&logo=dagster&logoColor=white)](https://dagster.io/)

> 🚀 **Live Interactive Web App**: [https://ecom-sales-profitability.streamlit.app](https://ecom-sales-profitability.streamlit.app)  
> ⏱️ **Note on Free-Tier Hosting**: *Hosted on Streamlit Community Cloud (Free Tier). If the container has been idle, it may take ~45–60 seconds to spin up on first click. For immediate review without waiting, high-resolution preview screenshots are provided below.*

An end-to-end Data Engineering pipeline and executive BI dashboard built on the **Modern Data Stack** (`dlt`, `DuckDB`, `dbt`, `Dagster`, `Streamlit`, `Docker`). 

Processes real-world e-commerce transaction data (~540,000 order records) to generate business insights around top-line revenue, category profit margins, product rank volume gaps, and actionable low-performer risk alerts.

---

## 📸 Executive Dashboard Previews

![Executive E-Commerce Sales & Profitability Dashboard Overview](docs/images/ecom_dashboard_overview.png)
*Fig 1: Executive KPI suite ($10.67M Revenue, $1.16M Net Gross Profit, 10.9% Margin), Revenue vs. COGS Trends, and Category Margin % Breakdown.*

<details>
<summary>📊 <b>Click to view Best Seller Volume Gap & Low-Performer Risk Alerts</b></summary>
<br>

![Best Seller Volume Gap and Low-Performer Alerts](docs/images/ecom_dashboard_charts.png)
*Fig 2: Top 10 Best Sellers Revenue vs. Volume Gap analysis and automated inventory risk alert table.*

![Full Dashboard View](docs/images/ecom_dashboard_full.png)
*Fig 3: Complete scroll view of analytics dashboard.*

</details>

---

## 🎯 Business Problem & Key Objectives

Traditional sales dashboards only focus on vanity metrics like gross revenue. Small business owners need visibility into **unit profitability** and **actionable inventory signals**:

1. **Executive Revenue & Gross Profit Overview**: Daily & monthly trends of sales vs. Cost of Goods Sold (COGS).
2. **Category Profit Margins**: Breakdown of margin % `(Revenue - Cost) / Revenue` across product lines.
3. **Best vs Worst Seller Rank Gap**: Identifying high-volume low-revenue items vs. high-revenue low-volume items.
4. **Actionable Low-Performer Flags**: Automatic warnings for products with high retail prices but low sales velocity, or items with sub-target profit margins.

---

## 🏗️ Technical Architecture

```mermaid
flowchart LR
    A[Raw UCI Retail Dataset\n~540k Transaction Rows] -->|dlt Ingestion Engine| B[(DuckDB Warehouse\nraw_ecom.raw_orders)]
    B -->|dbt Transformations| C[Staging Layer\nstg_orders]
    C -->|Category & Cost Engine| D[Data Marts\nfct_daily_sales\nmart_category_profitability\nmart_product_performance\nmart_low_performers]
    D -->|Dagster Asset DAG| E[Orchestration & Data Quality]
    D -->|Streamlit Web UI| F[Executive BI Dashboard]
```

---

## 🛠️ Tech Stack & Licensing ($0.00 Open Source Stack)

* **Ingestion Layer**: `dlt` (Data Load Tool) — 100% Free & Open Source.
* **Storage & Data Warehouse**: `DuckDB` (columnar local analytical database) — 100% Free & Open Source.
* **Transformations & Modeling**: `dbt` (dbt-duckdb adapter) — 100% Free & Open Source.
* **Orchestration**: `Dagster` Software-Defined Assets (`@asset`) — 100% Free & Open Source.
* **Business Intelligence**: `Streamlit` + `Plotly` web dashboard — 100% Free & Open Source.
* **Containerization**: `Docker` + `Docker Compose` — 100% Free & Open Source.

---

## 🚀 Deployment Options

### Option 1: 1-Click Zero-Dependency Deployment with Docker 🐳
Run anywhere (locally or on a client's cloud/on-premise server) without installing Python, dbt, or dependencies:
```bash
docker-compose up --build
```
* Access the Live Dashboard: `http://localhost:8501`

---

### Option 2: Local Python Execution

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Execute End-to-End Pipeline
```bash
python run_pipeline.py
```

#### 3. Launch Live Interactive Dashboard
```bash
streamlit run dashboard/app.py
```

#### 4. Launch Dagster Asset Graph UI
```bash
dagster dev -f orchestration/repository.py
```

---

## 📊 Sample Executive Insights

* **Overall Gross Revenue**: $10,666,684.54 across 308 active trading days.
* **Top Category Revenue**: Home & Living leading sales revenue ($1.65M at 26.6% margin), followed by Stationery & Gifts ($1.27M at 30.5% margin).
* **Low-Performer Flags**: Automatically highlights items needing pricing intervention or clearance discounts.
