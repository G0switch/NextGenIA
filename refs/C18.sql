SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN product p ON p.product_id = o.product_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.date >= '2026-05-01 00:00:00' AND o.date < '2026-06-01 00:00:00'
  AND (CAST(substr(o.date,1,4) AS INTEGER) - CAST(substr(c.birth_date,1,4) AS INTEGER))
      - (substr(o.date,6,5) < substr(c.birth_date,6,5)) = 25;
