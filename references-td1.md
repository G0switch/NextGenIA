# TD 1 references (step 1)

The 20 queries are in "refs/C01.sql" to "refs/C20.sql". They run read-only on "data/boutique.sqlite". "fill_reference.py" writes the results to "reference-td1.csv".

## Rules for the querry

- Amount: sum of "quantity_product * price", in cents, excluding VAT
- Period: start included, end excluded. Dates are compared as written, in UTC
- Age: The age of the person. One year is removed if the birthday has not happened yet
- No match: "COALESCE" returns 0 instead of NULL

## What each query computes

- C01, C04, C05, C06, C07, C20: revenue for a period only
  - C01: March to May 2026.
  - C04: January to September 2026 (the whole database).
  - C05: 1 June 2026.
  - C06: year 2025 (no orders, so 0).
  - C07: 31 May 2026.
  - C20: June to August 2026.
- C02, C08, C09, C11: revenue of the customers aged exactly 25 on a reference date, all their orders.
  - C02: 2026-09-25. C08: 2026-09-24. C09: 2026-09-26. C11: 2026-12-01.
- C10: revenue of the orders placed when the customer was 25 on the order date.
- C03, C12, C13, C14: revenue for some products.
  - C03: products a, b, c in the first half of 2026.
  - C12: products a, b, c, all dates.
  - C13: products a and c in April 2026.
  - C14: products a, b, c in October and November 2026 (no orders, so 0).
- C15, C16, C17, C19: combined filters, customers aged 25 on 2026-09-25.
  - C15: March to May 2026.
  - C16: products a, b, c.
  - C17: products a, b, c in the first half of 2026.
  - C19: product d in September 2026.
- C18: orders of May 2026 placed when the customer was 25 on the order date.