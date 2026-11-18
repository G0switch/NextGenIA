-- Positive deltas are revenue omitted by a model. Negative deltas are extras.
WITH customer_revenue AS (
    SELECT
        c.customer_id,
        c.birth_date,
        COUNT(DISTINCT o.order_id) AS order_count,
        SUM(o.quantity_product * p.price) AS revenue_cents
    FROM customers AS c
    JOIN orders AS o ON o.customer_id = c.customer_id
    JOIN product AS p ON p.product_id = o.product_id
    GROUP BY c.customer_id, c.birth_date
),
population_flags AS (
    SELECT
        *,
        (birth_date > '2000-12-01' AND birth_date <= '2001-12-01') AS in_reference,
        (
            CAST(SUBSTR(birth_date, 1, 4) AS INTEGER) - 2026 = 25
            AND SUBSTR(birth_date, 6, 5) <= '12-01'
        ) AS in_cohere,
        (birth_date = '2001-12-01') AS in_dots
    FROM customer_revenue
)
SELECT
    customer_id,
    birth_date,
    order_count,
    revenue_cents,
    (in_reference - in_cohere) * revenue_cents AS cohere_delta_cents,
    (in_reference - in_dots) * revenue_cents AS dots_delta_cents
FROM population_flags
WHERE in_reference <> in_cohere OR in_reference <> in_dots
ORDER BY customer_id;
