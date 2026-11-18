# Routing rule of the sub-group (TD 2, Pair C)

Sources include [the TD 1 traces](../../td1/traces-td1.csv) (last attempt of each cell), [the TD 1 references](../../td1/reference-td1.csv) and the [model portfolio](../../td1/portefeuille-modeles-en.md) dated 2026-09-28. Twenty questions give a hypothesis for this batch only, not a general error rate.

## TD 1 rates per family

| Family | Cells | 120B | 20B | Qwen | Cohere | Dots |
|---|---|---|---|---|---|---|
| F1 period | C01 C04 C05 C06 C07 C20 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| F3 products | C03 C12 C13 C14 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| F2 age at a date | C02 C08 C09 C11 | 4/4 | 2/4 | 4/4 | 1/4 | 1/4 |
| F2b age at the order | C10 | 1/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| F1+F2 | C15 | 1/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| F2+F3 | C16 | 1/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| F1+F2+F3 | C17 C19 | 2/2 | 2/2 | 0/2 | 1/2 | 0/2 |
| F1+F2b | C18 | 1/1 | 1/1 | 1/1 | 0/1 | 0/1 |

120B is openai/gpt-oss-120b, 20B is openai/gpt-oss-20b, Qwen is qwen/qwen3.8-27b (all Groq free). Cohere is cohere/north-mini-code:free and Dots is dots-studio/dots-3-note-preview:free (OpenRouter free). 20B on C20 is correct after a 429 and one retry.

## First model called

All five TD 1 routes cost 0 (free plans), so price does not separate them. Cohere and Dots are not in the portfolio, so we cannot say they are the cheapest and we use them last. At equal price we take the model with the lowest public index in the portfolio (20B 9, 120B 11.6, Qwen 33.7), so the stronger model stays free for harder questions.

- F1 and F3: 20B
- F2: 120B (20B made errors on C02 and C11)
- F2b and all combinations: 20B (only 120B and 20B are always correct there)

## Checks per use

| Family | Internal dashboard | Figure shown to the customer | Amount paid out |
|---|---|---|---|
| F1, F3 | none | 2-of-3 quorum | reference check and human review |
| F2 | 2-of-3 quorum | 2-of-3 quorum and reference check | reference check and human review |
| F2b and combinations | 2-of-3 quorum, abstain if no consensus | reference check | reference check and human review |

- none is only used on F1 and F3, where the first model and the four others were 100 % correct in TD 1.
- 2-of-3 quorum is the fixed panel 120B, Cohere, Qwen. In TD 1 it gives the right value on all F1, F3 and F2 cells and on C18 and C19, and abstains on C10, C15, C16 and C17. It never gives a wrong value.
- We do not use 3-of-5. In TD 1 it is never right where 2-of-3 is wrong, and it abstains once more, on C11 (120B and Qwen give 446690, Cohere and Dots both give the wrong value 0).
- For F2b and combinations the quorum often abstains, so a figure for a customer needs the reference check (value computed by a checked query or script).
- 120B and 20B are the only models always right on the hard families, but they are the same family (gpt-oss), so a quorum of the two would not protect against a shared error.

## If the first model is unavailable

1. Next eligible model in this order: 20B, 120B, Qwen, then Cohere and Dots (only for F1 and F3).
2. If none is available and the request can wait: wait for the Groq refill (limits are per minute, the 20B retry on C20 worked 3 s after the 429), then check again.
3. If it cannot wait: paid route of the same model, openai/gpt-oss-120b on OpenRouter, 0.15 / 0.60 USD per million tokens, about 0.0002 USD per request with the median TD 1 tokens of 120B (638 in, 183 out).
4. If there is no budget: abstain.

## Simulator

The [original simulator](atelier-routage.py) produced [sim-before.jsonl](sim-before.jsonl). The [adapted simulator](atelier-routage-td2.py) produced [sim-after.jsonl](sim-after.jsonl).

Changes: the resources are the five TD 1 models and the paid 120B route. Eligibility is the list of families where the model was 100 % correct, instead of a level. The order between free models uses the public index. The checks depend on the use. Each reason cites the TD 1 cells.

| Scenario | Request | Decision | Resource |
|---|---|---|---|
| simple | F1, dashboard | run, no check | 20B |
| complex | F2b, customer | run, reference check | 20B |
| priority | F2b, 20B exhausted | run | 120B (free) |
| deferrable | F2b, 20B and 120B exhausted, can wait | defer 1 min | 20B |
| urgent | same, cannot wait | run, 0.00021 USD | 120B paid |
| budget exhausted | same, budget 0 | abstain | none |
| high impact | F2, payout | run, reference check and review | 120B |
| unknown family | F4 | abstain | none |

## Why choose runs the subscription before deferring

In choose, the included branch is tested first and returns at once. A resource is included when it is available and cash == 0, and a subscription is in that case (already paid, allocation > 0). The defer branch is only reached when no included resource is available, so a free resource that refills before deadline_minutes is never waited for while the subscription is usable. Allocation is only used to sort the included resources, not to skip them. The idea is that running now costs no new money and gives the answer at once, while waiting only saves the subscription allocation.

This should be reversed when the subscription allocation is scarce: for example when it is close to its limit and needed for urgent or hard requests before its own reset, while this request can wait for the free refill. In that case using the subscription now could block a later request that has no other route.
