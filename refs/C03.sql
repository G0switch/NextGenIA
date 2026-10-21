SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o JOIN product p ON p.product_id = o.product_id
WHERE o.product_id IN ('a', 'b', 'c')
  AND o.date >= '2026-01-01 00:00:00' AND o.date < '2026-07-01 00:00:00';
