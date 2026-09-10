WITH raw_source AS (
    SELECT * FROM raw_ecom.raw_orders
),
cleaned AS (
    SELECT
        CAST(invoice_no AS VARCHAR) AS invoice_no,
        CAST(stock_code AS VARCHAR) AS stock_code,
        UPPER(TRIM(CAST(description AS VARCHAR))) AS description,
        CAST(quantity AS INTEGER) AS quantity,
        CAST(invoice_date AS TIMESTAMP) AS invoice_date,
        CAST(unit_price AS DOUBLE) AS unit_price,
        CAST(customer_id AS VARCHAR) AS customer_id,
        CAST(country AS VARCHAR) AS country,
        -- Flag order status
        CASE 
            WHEN CAST(invoice_no AS VARCHAR) LIKE 'C%' OR CAST(quantity AS INTEGER) < 0 THEN TRUE 
            ELSE FALSE 
        END AS is_cancelled,
        -- Compute gross item revenue
        ROUND(CAST(quantity AS INTEGER) * CAST(unit_price AS DOUBLE), 2) AS line_revenue
    FROM raw_source
    WHERE invoice_no IS NOT NULL
      AND unit_price IS NOT NULL
      AND unit_price >= 0
)
SELECT * FROM cleaned
