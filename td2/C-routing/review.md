# Review of part C by group B

Codex drafted this review and ran the checks for group B to confirm.

- Both simulators reproduce the saved outputs. The original version has seven scenarios, and the adapted version has eight, including an added priority scenario. [Original output](sim-before.jsonl) · [Adapted output](sim-after.jsonl)
- The adapted rule falls back to GPT-OSS 120B when 20B is exhausted, waits one minute when the request can wait, uses the paid route when urgent and within budget, and abstains when there is no eligible route. The payout scenario requires a reference check and human review. [Routing rule](routing-rule-td2.md)
