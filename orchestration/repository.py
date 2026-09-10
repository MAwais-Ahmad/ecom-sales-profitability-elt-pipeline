import os
import subprocess
from dagster import asset, Definitions, AssetExecutionContext

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INGESTION_SCRIPT = os.path.join(BASE_DIR, "ingestion", "raw_retail_pipeline.py")
DBT_DIR = os.path.join(BASE_DIR, "dbt_ecom")

@asset(group_name="ingestion", description="Extracts raw UCI Online Retail orders dataset and loads into DuckDB raw_ecom dataset via dlt")
def raw_ecom_orders_asset(context: AssetExecutionContext):
    """Triggers dlt raw e-commerce retail ingestion."""
    context.log.info(f"Running dlt ingestion script: {INGESTION_SCRIPT}")
    result = subprocess.run(["python", INGESTION_SCRIPT], capture_output=True, text=True, check=True)
    context.log.info(result.stdout)
    return "Ingested ~500k raw transaction records"

@asset(deps=[raw_ecom_orders_asset], group_name="transformation", description="Executes dbt staging and analytical metrics models in DuckDB")
def dbt_transformation_mart_asset(context: AssetExecutionContext):
    """Triggers dbt transformation run for data marts."""
    context.log.info(f"Running dbt build in directory: {DBT_DIR}")
    result = subprocess.run(["dbt", "run", "--project-dir", DBT_DIR, "--profiles-dir", DBT_DIR], capture_output=True, text=True, check=True)
    context.log.info(result.stdout)
    return "dbt analytical marts transformed successfully"

defs = Definitions(
    assets=[raw_ecom_orders_asset, dbt_transformation_mart_asset]
)
