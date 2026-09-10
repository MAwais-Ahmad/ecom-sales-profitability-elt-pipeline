import os
import pandas as pd
import dlt
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "online_retail.csv")
DB_PATH = os.path.join(BASE_DIR, "data", "data_warehouse.duckdb")

@dlt.resource(name="raw_orders", write_disposition="replace")
def fetch_online_retail_orders():
    """Reads raw retail CSV dataset and yields clean dict records for dlt ingestion."""
    if not os.path.exists(DATA_PATH):
        from data.download_raw_data import download_data
        download_data()

    print(f"Loading raw data from {DATA_PATH} into Pandas...")
    # Load dataset with fallback encodings commonly found in retail CSVs
    try:
        df = pd.read_csv(DATA_PATH, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(DATA_PATH, encoding="ISO-8859-1")
    
    # Normalize column names to standard snake_case
    df.columns = [col.strip().replace(" ", "_").lower() for col in df.columns]
    
    # Standardize column mapping if names differ slightly across mirrors
    col_map = {
        'invoiceno': 'invoice_no',
        'invoice': 'invoice_no',
        'stockcode': 'stock_code',
        'code': 'stock_code',
        'description': 'description',
        'quantity': 'quantity',
        'invoicedate': 'invoice_date',
        'date': 'invoice_date',
        'unitprice': 'unit_price',
        'price': 'unit_price',
        'customerid': 'customer_id',
        'customer_id': 'customer_id',
        'country': 'country'
    }
    df.rename(columns=col_map, inplace=True)
    
    # Fill missing values appropriately
    df['description'] = df['description'].fillna('UNLABELLED PRODUCT')
    df['customer_id'] = df['customer_id'].fillna(-1).astype(int).astype(str)
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce').fillna(0.0)
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)
    
    df['invoice_date'] = pd.to_datetime(df['invoice_date'], format='mixed', errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
    
    df['ingested_at'] = datetime.utcnow().isoformat()
    
    print(f"Yielding {len(df):,} records to dlt pipeline...")
    for record in df.to_dict(orient="records"):
        yield record

def run_ingestion_pipeline():
    """Runs the dlt ingestion pipeline targeting DuckDB."""
    pipeline = dlt.pipeline(
        pipeline_name="ecom_retail_ingestion",
        destination=dlt.destinations.duckdb(credentials=DB_PATH),
        dataset_name="raw_ecom"
    )
    
    print(f"Starting dlt pipeline execution -> DuckDB: {DB_PATH}")
    info = pipeline.run(fetch_online_retail_orders())
    print("dlt Ingestion Pipeline Completed Successfully!")
    print(info)
    return info

if __name__ == "__main__":
    run_ingestion_pipeline()
