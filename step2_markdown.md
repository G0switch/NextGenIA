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
