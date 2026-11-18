# TD 2 report

## Pair A - Quorum

The [quorum comparison](../td2/A-quorum/step1-quorum-table.md) records all twenty decisions. The fixed 2-of-3 panel produced 16 correct consensuses and 4 abstentions. The 3-of-5 panel produced 15 correct consensuses and 5 abstentions. See the [replay commands](../td2/A-quorum/README.md).



## Pair B - Shared wrong answer on C11

C11 asks for the total revenue excluding VAT, in euro cents, from **all orders** placed by customers who were **exactly 25 on 1 December 2026**. The reference in [reference-td1.csv](../td1/reference-td1.csv) is **446,690 cents**.

The [real TD1 traces](../td1/traces-td1.csv) contain 101 attempts for 100 question–model cells. The second attempt for Groq GPT-OSS 20B on C20 replaces the first when inspecting the cells. C11 is the only question for which multiple models share an incorrect numeric answer. OpenRouter Cohere North Mini Code and OpenRouter Dots both returned **0 cents**.

### Manual tally and executable check

| Provider and model | C11 value (cents) | In the fixed 2-of-3 panel |
|---|---:|---|
| Groq `openai/gpt-oss-120b` | 446,690 | Yes |
| OpenRouter `cohere/north-mini-code:free` | 0 | Yes |
| Groq `qwen/qwen3.8-27b` | 446,690 | Yes |
| Groq `openai/gpt-oss-20b` | 322,160 | No |
| OpenRouter `dots-studio/dots-3-note-preview:free` | 0 | No |

- **Fixed 2-of-3.** Two votes for 446,690 and one vote for 0. The quorum returns 446,690, which matches the reference.
- **Full 3-of-5.** Two votes for 446,690, two for 0 and one for 322,160. No value reaches three votes, so the quorum abstains.

Pair A's `Orchestrateur.vote_k_sur_n` reproduced both manual decisions. The fixed panel returned `consensus=True, value=446690, votes=2`. The full panel returned `consensus=False, value=None, votes=2`. The inputs contained the executed model values and model identities. The reference was used after the vote to check the accepted value.

### SQL diagnosis

The two queries below are from the actual C11 traces. Both returned 0 when executed on [boutique.sqlite](../td1/data/boutique.sqlite).

**Cohere North Mini Code**

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE
  -- Compute age on 2026-12-01
  (
    -- Age = year difference
    CAST(SUBSTR(c.birth_date, 1, 4) AS INTEGER) -
    CAST(SUBSTR('2026-12-01', 1, 4) AS INTEGER)
  ) = 25
  AND
  -- Check that the birthday on 2026-12-01 has already occurred (or is today)
  SUBSTR(c.birth_date, 6, 5) <= '12-01'
;
```

The year subtraction is reversed. The predicate selects birth year 2051 and then restricts birthdays to 1 December or earlier in that year. None of the customers matches.

**Dots**

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date IS NOT NULL
  AND (
    -- Exactly 25 years old on 2026-12-01: born on 2001-12-01
    c.birth_date = '2001-12-01'
  );
```

The equality selects people turning 25 that day. C11 includes everyone who had turned 25 by that day and would turn 26 later, so the correct birth-date interval is **after 2000-12-01 and on or before 2001-12-01**. No customer has the exact birthday selected by Dots. In both queries, `COALESCE` returns 0 for the empty selection.

**Reference SQL**

The [TD 1 reference query](../td1/refs/C11.sql) computes completed age by subtracting one year when the birthday has yet to occur on the reference date. It returns 446,690 cents.

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN product p ON p.product_id = o.product_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE (CAST(substr('2026-12-01',1,4) AS INTEGER) - CAST(substr(c.birth_date,1,4) AS INTEGER))
      - (substr('2026-12-01',6,5) < substr(c.birth_date,6,5)) = 25;
```

### Exact reconciliation

The [delta query](../td2/B-consensus/td2-c11-delta.sql) compares the three populations by customer and totals each customer's order lines as `quantity_product * price`. Run it from the repository root with `python td1/run_sql.py td2/B-consensus/td2-c11-delta.sql`.

| Customer | Birth date | Distinct orders | Revenue omitted by each query (cents) |
|---|---|---:|---:|
| C001 | 2001-09-25 | 8 | 135,000 |
| C002 | 2001-09-24 | 3 | 25,920 |
| C003 | 2001-09-26 | 4 | 47,900 |
| C006 | 2001-11-30 | 5 | 77,450 |
| C008 | 2001-05-15 | 7 | 99,090 |
| C009 | 2001-03-10 | 5 | 61,330 |
| **Total** | | **32** | **446,690** |

Each query omitted those six customers and added no revenue. The delta for each model is therefore **446,690 − 0 = 446,690 cents**.

### Independent CSV check and escalation

The [Python check](../td2/B-consensus/check_c11_csv.py) recomputes completed age from the birth dates in `customers.csv`: it subtracts one year if the birthday has yet to occur on the reference date. For customers aged 25, it counts distinct orders in `orders.csv` and sums each order line's quantity times the unit price from `product.csv`. The [recorded output](../td2/B-consensus/c11-csv-check.txt) matches all six customer IDs, all six subtotals and the total of 446,690 cents. The calculation uses only the three source CSVs.

When the 3-of-5 quorum abstains on C11, escalate to the deterministic calculation. For age-based figures used externally or for payments, check the eligible customer IDs and the revenue against a calculation based on completed age, even when the models agree. Comparing the customer sets can catch errors that cancel out in the total. If the check is unavailable or the discrepancy remains unresolved, hold the figure for human review.

The [separate DEMO-VOTE exercise](../td2/B-consensus/README.md#demo-vote---synthetic-example) illustrates how two identical SQL boundary errors can reach a strict majority on an invented sale.

## Pair C - Routing

The [routing rule](../td2/C-routing/routing-rule-td2.md) defines the first model per question family, the checks per use and the fallback when the first model is unavailable. The [routing directory](../td2/C-routing/README.md) contains both simulators and their outputs.
