-- Top 20 EU customers who signed up since July 2024, by 2025 spend on delivered orders.
SELECT
    c.id,
    c.name,
    (SELECT SUM(oi.quantity * oi.unit_price)
       FROM orders o
       JOIN order_items oi ON oi.order_id = o.id
      WHERE o.customer_id = c.id
        AND o.status = 'delivered'
        AND strftime('%Y', o.order_date) = '2025') AS spend_2025,
    (SELECT COUNT(*)
       FROM orders o
      WHERE o.customer_id = c.id
        AND o.status = 'delivered'
        AND strftime('%Y', o.order_date) = '2025') AS orders_2025
FROM customers c
WHERE c.region = 'EU'
  AND c.signup_date >= '2024-07-01'
ORDER BY spend_2025 DESC, c.id
LIMIT 20;
