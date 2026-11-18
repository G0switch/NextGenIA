# Part B - Consensus

The [C11 analysis](../../reports/td2.md#pair-b---shared-wrong-answer-on-c11) explains why Cohere and Dots both returned 0 cents on the real TD 1 traces and shows the decisions of both quorums.

## Verify C11

Run from the repository root.

```powershell
python td1/run_sql.py td1/refs/C11.sql
python td1/run_sql.py td2/B-consensus/td2-c11-delta.sql
python td2/B-consensus/check_c11_csv.py
```

The [reference query](../../td1/refs/C11.sql) returns 446,690 cents. The [delta query](td2-c11-delta.sql) identifies the revenue omitted by each model, and the [independent CSV calculation](check_c11_csv.py) reproduces the [customer-level results](c11-csv-check.txt) directly from the source data.

## DEMO-VOTE - synthetic example

The [demo](demo_vote.py) runs both SQL variants on an in-memory table with one invented sale of 100 cents on 1 January 2026. The requested period includes 1 January and ends before 2 January.

```powershell
python td2/B-consensus/demo_vote.py
```

| Lower-bound predicate | Result (cents) |
|---|---:|
| `sale_date > '2026-01-01'` | 0 |
| `sale_date >= '2026-01-01'` | 100 |

The strict lower bound excludes the only sale, which sits exactly on the boundary. With the proposals `[0, 0, 100]`, Pair A's 2-of-3 vote accepted **0 cents** with two votes. The independent reference is **100 cents**, the amount of the single sale in the period. This example uses synthetic data and is separate from the TD 1 results.

The verification scripts were prepared with AI assistance.
