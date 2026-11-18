# TD 2, Step 1: the k-of-n quorum (Pair A)

DIA4-G3 · Pair A: Adam Gaabi, Axel Warot, Timéo Brajon · Session 18 November 2026

## Goal

Make several models vote on each question and accept a value only when k of the n panel members agree (strict majority). Then compare a 2-of-3 fixed panel with a 3-of-5 quorum on the 20 TD 1 questions.

## Files

| file | role |
|---|---|
| [skeleton-multi-llm-en.py](../../td1/skeleton-multi-llm-en.py) | Kit skeleton with `Orchestrateur.vote_k_sur_n` implemented |
| [vote_k_sur_n.py](vote_k_sur_n.py) | The method on its own, for review |
| [atelier-vote.py](atelier-vote.py) | Runs four synthetic examples or one real question |
| [compare_quorums.py](compare_quorums.py) | Compares 2-of-3 and 3-of-5 on C01 to C20 |
| [Comparison table](step1-quorum-table.md), [CSV](step1-quorum-table.csv) | Decisions across the 20 questions |
| [Synthetic decisions](step1-synthetic.jsonl), [real decisions](step1-atelier-vote-real.jsonl) | Workshop outputs |
| [Duplicate route check](step1-duplicate-route.jsonl) | Rejection of a repeated provider and model in a synthetic panel |

## Run (offline, no key), from the repository root

```powershell
python td2/A-quorum/atelier-vote.py
python td2/A-quorum/atelier-vote.py --duplicate-route
python td2/A-quorum/atelier-vote.py --traces td1/traces-td1.csv --case C11
python td2/A-quorum/compare_quorums.py --traces td1/traces-td1.csv
```

## Vote contract

1. Only an executed proposal with a value votes. An error, invalid SQL or HTTP 429 stays in n but does not vote.
2. k must be a strict majority, n // 2 < k <= n, otherwise ValueError.
3. The same (provider, model_requested) twice raises ValueError: a retry is not a second vote.
4. A value with at least k votes is returned with consensus True, its count and the agreeing members (provider:model).
5. Otherwise the vote abstains: consensus False, value None, largest count. It never invents a value.
6. The reference is never an input: it is compared only after the decision.

## Results (real TD 1 traces)

| quorum | correct | wrong | abstentions |
|---|---|---|---|
| 2-of-3: gpt-oss-120b, north-mini-code, qwen3.8-27b | 16 | 0 | 4 (C10, C15, C16, C17) |
| 3-of-5: + gpt-oss-20b, dots-3-note | 15 | 0 | 5 (C10, C11, C15, C16, C17) |

- C11 is the only decision that changes. In 2-of-3, gpt-oss-120b and qwen give 446690 (2 votes) and win. In 3-of-5, dots also gives 0 (like north-mini-code) and gpt-oss-20b gives 322160. The counts are 446690 ×2, 0 ×2 and 322160 ×1, so no value reaches k=3 and the quorum abstains.
- C08 and C18: north-mini-code's SQL does not run. It stays in n without voting, and 2-of-3 holds with the minimum margin.
- C10, C15, C16, C17: only the two gpt-oss models are right, and both quorums abstain.
- C20: gpt-oss-20b got HTTP 429, then succeeded on retry. Only the last attempt counts, as one vote.
- Takeaway: a bigger quorum is not automatically safer. It costs 2 more calls and, here, abstained once more and accepted nothing new.

## Limits

One batch of 20 questions. The two gpt-oss models are the same family, so their agreement is not independent. Synthetic examples are labelled nature: simulation.
