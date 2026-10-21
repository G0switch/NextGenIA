SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o JOIN product p ON p.product_id = o.product_id
WHERE o.date >= '2026-06-01 00:00:00' AND o.date < '2026-09-01 00:00:00';
