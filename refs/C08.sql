SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN product p ON p.product_id = o.product_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE (CAST(substr('2026-09-24',1,4) AS INTEGER) - CAST(substr(c.birth_date,1,4) AS INTEGER))
      - (substr('2026-09-24',6,5) < substr(c.birth_date,6,5)) = 25;
