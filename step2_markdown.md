# Model calls (TD 1, step 2)

The 5 models answered the 20 questions on 2026-10-21 with "skeleton-multi-llm-en.py --run". Same prompt for all models, temperature 0, capped output, 45 s timeout, one request at a time, at least 3 s between requests, at most one retry per cell.

## Trace files

- "state-A.jsonl" to "state-E.jsonl": raw state of each run, one line per attempt. The skeleton uses it to resume and to limit retries.
- "traces-A.csv" to "traces-E.csv": the same attempts, exported as CSV by the skeleton.
- "traces-td1.csv": the 5 CSV files merged under one header, rows unchanged (101 rows).
- "traces-td1.jsonl": the 5 JSONL files merged, lines unchanged (101 lines).

Main columns: "cell_id" (provider:model:question), "prompt_sha256" (prompt fingerprint, the same for the 5 models on a question), "sql", "value", "reference", "verdict", "http_status", "error", "latency_ms", "tokens_*", "cost_native", "attempts" (attempt number), "date_utc", "nature". An empty cell means the value was not measured (for example "cost_native" on free models). All rows are "real": no replay or simulation.

## Results per model

| | Model (exact id) | Access | Correct | Other verdicts |
|---|---|---|---:|---|
| A | openai/gpt-oss-120b | Groq | 20/20 | none |
| B | openai/gpt-oss-20b | Groq | 18/20 | incorrect: C02, C11 |
| C | cohere/north-mini-code:free | OpenRouter (account 1) | 12/20 | incorrect: C09, C10, C11, C15, C16, C17 · sql_invalid: C08, C18 |
| D | qwen/qwen3.8-27b | Groq | 15/20 | incorrect: C10, C15, C16, C17, C19 |
| E | dots-studio/dots-3-note-preview:free | OpenRouter (account 2) | 11/20 | incorrect: C08, C09, C10, C11, C15, C17, C18, C19 · sql_rejected: C16 |

Verdicts:
- **incorrect**: the SQL ran but the value differs from the reference.
- **sql_invalid**: SQL syntax error.
- **sql_rejected**: blocked by the sandbox (here: more than one statement).
- **not_executed**: no answer to run (access error).

## Access failure and retry (gpt-oss-20b, C20)

Cell `groq:openai/gpt-oss-20b:C20` has two attempts in the traces:

| Attempt | Date (UTC) | HTTP | Result |
|---:|---|---:|---|
| 1 | 2026-10-21 10:55:52 | 429 | Refused, no SQL returned: "Rate limit reached for model `openai/gpt-oss-20b` ... on tokens per minute (TPM): Limit 8000, Used 7190, Requested 1052" |
| 2 | 2026-10-21 10:55:55 | 200 | Correct (1 106 090 cents, equal to the reference) |

Cause, read from the error: the Groq Free organisation limit of 8 000 tokens per minute was nearly used by the previous calls of the batch (7 190), and this request needed 1 052 more. It is a temporary access failure, not a wrong answer: the model never received the question on attempt 1. The skeleton retried once, as allowed for a 429, and the cell is final after attempt 2. Both attempts are kept in `traces-B.csv`, `state-B.jsonl` and the merged files.

## Call count

| Type | Groq | OpenRouter |
|---|---:|---:|
| Initial calls (base batch of 100 cells) | 60 (A, B, D) | 40 (C, E) |
| Retries | 1 (B, C20) | 0 |
| Total attempts in the traces | 61 | 40 |
| Access checks before the session (`check_access.py`, not in the traces) | 3 per member who ran it | 2 per member who ran it |

## Deviations from the protocol

- One member (Axel) ran A, B, C and D; another member (Léo) ran E. The protocol plans one operator per model. C and E still used two distinct personal OpenRouter accounts, as required.
- Longer pauses than the 3 s minimum, which the protocol allows:
  - D (qwen): `--pause 8`, after the 429 on B, to stay under the Groq Free limit of 8 000 tokens per minute;
  - C and E (OpenRouter `:free`): `--pause 4`, to stay under the limit of about 20 requests per minute of free models.
  The pause only spaces the calls: prompt, model parameters and fingerprints are unchanged (see `prompt-td1.md`, 20/20 fingerprints recomputed).
- The models were run before the instructor validated the reference values. The references had been checked internally by two independent Python computations on the CSV files (20/20 each, `verification-td1.txt` and `verification-independante.txt`). If a reference changes after validation, the affected cells will be re-scored in new files and the current ones kept.
