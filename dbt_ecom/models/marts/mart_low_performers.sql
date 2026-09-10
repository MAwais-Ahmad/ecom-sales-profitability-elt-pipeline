WITH stats AS (
    SELECT
        AVG(unit_price) AS avg_catalog_price,
        AVG(units_sold) AS avg_catalog_units
    FROM {{ ref('mart_product_performance') }}
),
flagged AS (
    SELECT
        p.stock_code,
        p.description,
        p.category,
        p.unit_price,
        p.unit_cost,
        p.units_sold,
        p.total_revenue,
        p.gross_profit,
        p.margin_pct,
        s.avg_catalog_price,
        s.avg_catalog_units,
        CASE
            WHEN p.unit_price > s.avg_catalog_price AND p.units_sold < (s.avg_catalog_units * 0.3) THEN 'HIGH_PRICE_LOW_VELOCITY'
            WHEN p.margin_pct < 0.35 THEN 'SUB_TARGET_MARGIN'
            WHEN p.units_sold < 5 THEN 'STAGNANT_INVENTORY'
            ELSE 'HEALTHY'
        END AS performance_flag,
        CASE
            WHEN p.unit_price > s.avg_catalog_price AND p.units_sold < (s.avg_catalog_units * 0.3) THEN 'Consider promotional discount or bundling to drive volume.'
            WHEN p.margin_pct < 0.35 THEN 'Renegotiate supplier wholesale cost or adjust price upward.'
            WHEN p.units_sold < 5 THEN 'Evaluate liquidating or delisting product.'
            ELSE 'Performant product.'
        END AS recommended_action
    FROM {{ ref('mart_product_performance') }} p
    CROSS JOIN stats s
)
SELECT * FROM flagged
WHERE performance_flag != 'HEALTHY'
ORDER BY total_revenue DESC
