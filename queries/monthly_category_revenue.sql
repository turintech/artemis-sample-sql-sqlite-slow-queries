-- Delivered revenue per month and category in 2025.
SELECT
    strftime('%Y-%m', o.order_date) AS month,
    p.category,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue,
    COUNT(DISTINCT o.id) AS orders
FROM order_items oi
JOIN orders o ON o.id = oi.order_id
JOIN products p ON p.id = oi.product_id
WHERE o.status = 'delivered'
  AND strftime('%Y', o.order_date) = '2025'
GROUP BY month, p.category
ORDER BY month, p.category;
