-- Top 20 EU customers who signed up since July 2024, by 2025 spend on delivered orders.
WITH eligible AS (
    SELECT id, name
    FROM customers
    WHERE region = 'EU'
      AND signup_date >= '2024-07-01'
), totals AS (
    SELECT o.customer_id,
           SUM(oi.quantity * oi.unit_price) AS spend_2025,
           COUNT(DISTINCT o.id) AS orders_2025
    FROM orders o
    JOIN eligible e ON e.id = o.customer_id
    JOIN order_items oi ON oi.order_id = o.id
    WHERE o.status = 'delivered'
      AND o.order_date >= '2025-01-01'
      AND o.order_date < '2026-01-01'
    GROUP BY o.customer_id
)
SELECT e.id,
       e.name,
       t.spend_2025,
       COALESCE(t.orders_2025, 0) AS orders_2025
FROM eligible e
LEFT JOIN totals t ON t.customer_id = e.id
ORDER BY t.spend_2025 DESC, e.id
LIMIT 20;
