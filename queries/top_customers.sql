-- Top 20 EU customers who signed up since July 2024, by 2025 spend on delivered orders.
WITH eligible_customers AS MATERIALIZED (
    SELECT id, name
    FROM customers
    WHERE region = 'EU'
      AND signup_date >= '2024-07-01'
),
filtered_orders AS MATERIALIZED (
    SELECT o.id, o.customer_id
    FROM orders o
    JOIN eligible_customers c ON c.id = o.customer_id
    WHERE o.status = 'delivered'
      AND o.order_date >= '2025-01-01'
      AND o.order_date < '2026-01-01'
),
order_counts AS MATERIALIZED (
    SELECT customer_id, COUNT(*) AS orders_2025
    FROM filtered_orders
    GROUP BY customer_id
),
customer_spend AS MATERIALIZED (
    SELECT fo.customer_id, SUM(oi.quantity * oi.unit_price) AS spend_2025
    FROM filtered_orders fo
    JOIN order_items oi ON oi.order_id = fo.id
    GROUP BY fo.customer_id
)
SELECT c.id, c.name, s.spend_2025, oc.orders_2025
FROM eligible_customers c
LEFT JOIN order_counts oc ON oc.customer_id = c.id
LEFT JOIN customer_spend s ON s.customer_id = c.id
ORDER BY s.spend_2025 DESC, c.id
LIMIT 20;
