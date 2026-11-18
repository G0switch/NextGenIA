# Part B — Consensus

The [C11 analysis](../../reports/td2.md#pair-b--shared-wrong-answer-on-c11) explains why two models independently returned 0 cents and compares the 2-of-3 and 3-of-5 decisions. The [delta query](td2-c11-delta.sql) identifies the customers and order revenue that both SQL queries missed.

Run from the repository root.

```powershell
python td1/run_sql.py td2/B-consensus/td2-c11-delta.sql
```
