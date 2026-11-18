# Consensus — Review 2

Reviewed by Codex (AI). Scope covers the C11 SQL diagnosis and independent check.

- Both model queries return 0. Cohere reverses the year subtraction. Dots selects one birth date instead of the full range.
- The reference SQL and the independent CSV calculation agree on 446,690 cents across 32 orders from 6 customers. The delta query accounts for the full difference. [CSV output](c11-csv-check.txt) · [Delta query](td2-c11-delta.sql)
- The report explains when to use the independent calculation and when to ask for human review. [Checking and escalation](../../reports/td2.md#independent-csv-check-and-escalation)
