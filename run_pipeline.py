import os
import sys
import subprocess
import duckdb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "data_warehouse.duckdb")
DBT_DIR = os.path.join(BASE_DIR, "dbt_ecom")
INGESTION_SCRIPT = os.path.join(BASE_DIR, "ingestion", "raw_retail_pipeline.py")
DOWNLOAD_SCRIPT = os.path.join(DATA_DIR, "download_raw_data.py")

def main():
    print("=" * 70)
    print("      E-COMMERCE SALES & PROFITABILITY PIPELINE EXECUTION ENGINE     ")
    print("=" * 70)
    
    # 1. Download dataset if missing
    print("\n[STEP 1/4] Checking & Downloading Real-World UCI Retail Dataset...")
    subprocess.run([sys.executable, DOWNLOAD_SCRIPT], check=True)
    
    # 2. Run dlt Ingestion
    print("\n[STEP 2/4] Running dlt Ingestion Pipeline (Loading into DuckDB)...")
    subprocess.run([sys.executable, INGESTION_SCRIPT], check=True)
    
    # 3. Run dbt Transformations
    print("\n[STEP 3/4] Running dbt Analytical Transformation Models...")
    dbt_cmd = ["dbt", "run", "--project-dir", DBT_DIR, "--profiles-dir", DBT_DIR]
    subprocess.run(dbt_cmd, check=True)
    
    # 4. Pipeline Verification & Data Quality Checks
    print("\n[STEP 4/4] Verifying Analytical Data Marts in DuckDB Warehouse...")
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database file not found at {DB_PATH}")
        
    con = duckdb.connect(DB_PATH)
    
    # Check tables
    tables = con.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in tables]
    print(f"\nWarehouse Tables Created ({len(table_names)}): {', '.join(table_names)}")
    
    print("\n--- EXECUTIVE SUMMARY MATRIX ---")
    summary = con.execute("""
        SELECT 
            COUNT(*) AS total_daily_records,
            SUM(total_units_sold) AS units_sold,
            ROUND(SUM(gross_revenue), 2) AS total_revenue_usd,
            ROUND(SUM(total_cost), 2) AS total_cost_usd,
            ROUND(SUM(gross_profit), 2) AS net_gross_profit_usd,
            ROUND(SUM(gross_profit) / SUM(gross_revenue) * 100, 2) AS overall_gross_margin_pct
        FROM fct_daily_sales
    """).df()
    print(summary.to_string(index=False))
    
    print("\n--- CATEGORY PROFITABILITY BREAKDOWN ---")
    cat_summary = con.execute("""
        SELECT 
            category,
            total_products,
            total_units_sold,
            category_revenue AS revenue_usd,
            gross_profit AS profit_usd,
            ROUND(margin_pct * 100, 2) AS margin_pct,
            revenue_share_pct
        FROM mart_category_profitability
        ORDER BY revenue_usd DESC
    """).df()
    print(cat_summary.to_string(index=False))

    print("\n--- ACTIONABLE LOW-PERFORMER ALERTS (TOP 5 RISKS) ---")
    low_perf = con.execute("""
        SELECT 
            stock_code,
            description,
            category,
            unit_price,
            units_sold,
            total_revenue,
            margin_pct,
            performance_flag
        FROM mart_low_performers
        LIMIT 5
    """).df()
    print(low_perf.to_string(index=False))
    
    con.close()
    print("\n" + "=" * 70)
    print(" PIPELINE EXECUTED SUCCESSFULLY! DATA READY FOR POWER BI DASHBOARD. ")
    print("=" * 70)

if __name__ == "__main__":
    main()
