WITH product_agg AS (
    SELECT
        stock_code,
        MAX(description) AS description,
        ROUND(AVG(unit_price), 2) AS avg_unit_price,
        ROUND(MAX(unit_price), 2) AS max_unit_price,
        SUM(CASE WHEN NOT is_cancelled THEN quantity ELSE 0 END) AS total_units_sold
    FROM {{ ref('stg_orders') }}
    WHERE stock_code IS NOT NULL
    GROUP BY stock_code
),
classified AS (
    SELECT
        stock_code,
        description,
        avg_unit_price,
        -- Category Classification Engine based on NLP keyword patterns
        CASE
            WHEN description LIKE '%BAG%' OR description LIKE '%LUGGAGE%' OR description LIKE '%TOTE%' OR description LIKE '%PURSE%' THEN 'Bags & Accessories'
            WHEN description LIKE '%MUG%' OR description LIKE '%PLATE%' OR description LIKE '%BOWL%' OR description LIKE '%CUP%' OR description LIKE '%GLASS%' OR description LIKE '%TEAPOT%' OR description LIKE '%KITCHEN%' THEN 'Kitchenware & Dining'
            WHEN description LIKE '%HEART%' OR description LIKE '%CANDLE%' OR description LIKE '%HOLDER%' OR description LIKE '%LIGHT%' OR description LIKE '%FRAME%' OR description LIKE '%CLOCK%' OR description LIKE '%DECOR%' OR description LIKE '%SIGN%' THEN 'Home & Living'
            WHEN description LIKE '%CHRISTMAS%' OR description LIKE '%GIFT%' OR description LIKE '%CARD%' OR description LIKE '%BOX%' OR description LIKE '%PAPER%' OR description LIKE '%WRAP%' OR description LIKE '%RIBBON%' THEN 'Stationery & Gifts'
            WHEN description LIKE '%SCARF%' OR description LIKE '%APRON%' OR description LIKE '%HAT%' OR description LIKE '%NECKLACE%' OR description LIKE '%EARRING%' OR description LIKE '%JEWEL%' THEN 'Apparel & Jewelry'
            ELSE 'General Merchandise'
        END AS category,
        -- Cost Engine: Derive cost as ~60% of unit price (giving a standard 40% margin target)
        ROUND(CASE 
            WHEN avg_unit_price > 0 THEN avg_unit_price * 0.60 
            ELSE 0.10 
        END, 2) AS unit_cost,
        total_units_sold
    FROM product_agg
)
SELECT
    stock_code,
    description,
    category,
    avg_unit_price AS unit_price,
    unit_cost,
    ROUND(avg_unit_price - unit_cost, 2) AS unit_profit,
    CASE 
        WHEN avg_unit_price > 0 THEN ROUND((avg_unit_price - unit_cost) / avg_unit_price, 4)
        ELSE 0.0
    END AS target_margin_pct,
    total_units_sold
FROM classified
