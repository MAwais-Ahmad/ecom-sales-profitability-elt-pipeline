WITH product_stats AS (
    SELECT
        p.stock_code,
        p.description,
        p.category,
        p.unit_price,
        p.unit_cost,
        SUM(CASE WHEN NOT o.is_cancelled THEN o.quantity ELSE 0 END) AS units_sold,
        ROUND(SUM(CASE WHEN NOT o.is_cancelled THEN o.line_revenue ELSE 0 END), 2) AS total_revenue,
        ROUND(SUM(CASE WHEN NOT o.is_cancelled THEN o.line_revenue - (o.quantity * p.unit_cost) ELSE 0 END), 2) AS gross_profit
    FROM {{ ref('stg_orders') }} o
    JOIN {{ ref('dim_products') }} p ON o.stock_code = p.stock_code
    GROUP BY p.stock_code, p.description, p.category, p.unit_price, p.unit_cost
),
ranked AS (
    SELECT
        stock_code,
        description,
        category,
        unit_price,
        unit_cost,
        units_sold,
        total_revenue,
        gross_profit,
        CASE WHEN total_revenue > 0 THEN ROUND(gross_profit / total_revenue, 4) ELSE 0.0 END AS margin_pct,
        DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
        DENSE_RANK() OVER (ORDER BY units_sold DESC) AS volume_rank
    FROM product_stats
    WHERE units_sold > 0
)
SELECT
    stock_code,
    description,
    category,
    unit_price,
    unit_cost,
    units_sold,
    total_revenue,
    gross_profit,
    margin_pct,
    revenue_rank,
    volume_rank,
    CAST(revenue_rank AS INT) - CAST(volume_rank AS INT) AS rank_gap
FROM ranked
