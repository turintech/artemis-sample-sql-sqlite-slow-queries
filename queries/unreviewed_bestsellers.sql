-- The 25 best-selling tech products that have never been reviewed.
SELECT
    p.id,
    p.name,
    (SELECT SUM(oi.quantity) FROM order_items oi WHERE oi.product_id = p.id) AS units_sold
FROM products p
WHERE p.category = 'tech'
  AND p.id NOT IN (SELECT r.product_id FROM reviews r)
  AND p.id IN (SELECT DISTINCT oi.product_id FROM order_items oi)
ORDER BY units_sold DESC, p.id
LIMIT 25;
