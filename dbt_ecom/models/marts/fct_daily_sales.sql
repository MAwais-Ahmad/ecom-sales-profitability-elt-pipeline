WITH order_items AS (
    SELECT
        o.invoice_no,
        CAST(o.invoice_date AS DATE) AS order_date,
        o.stock_code,
        o.quantity,
        o.line_revenue,
        p.category,
        p.unit_cost,
        ROUND(o.quantity * p.unit_cost, 2) AS line_cost,
        o.is_cancelled
    FROM {{ ref('stg_orders') }} o
    LEFT JOIN {{ ref('dim_products') }} p ON o.stock_code = p.stock_code
),
daily AS (
    SELECT
        order_date,
        COUNT(DISTINCT CASE WHEN NOT is_cancelled THEN invoice_no END) AS total_valid_orders,
        COUNT(DISTINCT CASE WHEN is_cancelled THEN invoice_no END) AS cancelled_orders,
        SUM(CASE WHEN NOT is_cancelled THEN quantity ELSE 0 END) AS total_units_sold,
        ROUND(SUM(CASE WHEN NOT is_cancelled THEN line_revenue ELSE 0 END), 2) AS gross_revenue,
        ROUND(SUM(CASE WHEN NOT is_cancelled THEN line_cost ELSE 0 END), 2) AS total_cost,
        ROUND(SUM(CASE WHEN NOT is_cancelled THEN line_revenue - line_cost ELSE 0 END), 2) AS gross_profit
    FROM order_items
    WHERE order_date IS NOT NULL
    GROUP BY order_date
)
SELECT
    order_date,
    total_valid_orders,
    cancelled_orders,
    total_units_sold,
    gross_revenue,
    total_cost,
    gross_profit,
    CASE 
        WHEN gross_revenue > 0 THEN ROUND(gross_profit / gross_revenue, 4)
        ELSE 0.0
    END AS gross_margin_pct
FROM daily
ORDER BY order_date ASC
