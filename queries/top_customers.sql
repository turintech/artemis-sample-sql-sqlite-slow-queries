-- Top 20 EU customers who signed up since July 2024, by 2025 spend on delivered orders.
WITH eligible_customers AS (
    SELECT id, name
    FROM customers
    WHERE region = 'EU'
      AND signup_date >= '2024-07-01'
), order_spend AS (
    SELECT
        o.id,
        o.customer_id,
        SUM(oi.quantity * oi.unit_price) AS spend_2025
    FROM eligible_customers ec
    JOIN orders o ON o.customer_id = ec.id
    LEFT JOIN order_items oi ON oi.order_id = o.id
    WHERE o.status = 'delivered'
      AND strftime('%Y', o.order_date) = '2025'
    GROUP BY o.id, o.customer_id
), order_metrics AS (
    SELECT
        customer_id,
        SUM(spend_2025) AS spend_2025,
        COUNT(*) AS orders_2025
    FROM order_spend
    GROUP BY customer_id
)
SELECT
    c.id,
    c.name,
    om.spend_2025,
    COALESCE(om.orders_2025, 0) AS orders_2025
FROM customers c
LEFT JOIN order_metrics om ON om.customer_id = c.id
WHERE c.region = 'EU'
  AND c.signup_date >= '2024-07-01'
ORDER BY spend_2025 DESC, c.id
LIMIT 20;
