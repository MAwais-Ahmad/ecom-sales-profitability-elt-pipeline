WITH category_sales AS (
    SELECT
        p.category,
        COUNT(DISTINCT p.stock_code) AS total_products,
        SUM(CASE WHEN NOT o.is_cancelled THEN o.quantity ELSE 0 END) AS total_units_sold,
        ROUND(SUM(CASE WHEN NOT o.is_cancelled THEN o.line_revenue ELSE 0 END), 2) AS category_revenue,
        ROUND(SUM(CASE WHEN NOT o.is_cancelled THEN o.quantity * p.unit_cost ELSE 0 END), 2) AS category_cost
    FROM {{ ref('stg_orders') }} o
    JOIN {{ ref('dim_products') }} p ON o.stock_code = p.stock_code
    GROUP BY p.category
)
SELECT
    category,
    total_products,
    total_units_sold,
    category_revenue,
    category_cost,
    ROUND(category_revenue - category_cost, 2) AS gross_profit,
    CASE 
        WHEN category_revenue > 0 THEN ROUND((category_revenue - category_cost) / category_revenue, 4)
        ELSE 0.0
    END AS margin_pct,
    ROUND((category_revenue / SUM(category_revenue) OVER ()) * 100, 2) AS revenue_share_pct
FROM category_sales
ORDER BY category_revenue DESC
