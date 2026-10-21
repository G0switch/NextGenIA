# TD 1 report: DIA4-G3

Session of 21 October 2026. Five free models answered the same 20 revenue questions on `boutique.sqlite`; each returned SQL was run in the read-only sandbox and compared with our own references.

## What we did

1. References: 20 SQL queries (`refs/`), checked by a second computation in Python on the CSV files (20/20), then compared with the instructor's values published on 2026-10-21 (identical, 20/20, first attempt). See `references-td1.md`.
2. Calls: 5 models x 20 questions = 100 cells (60 Groq, 40 OpenRouter), same prompt for all models (one fingerprint per question), temperature 0. 101 attempts in total: one retry after an HTTP 429. See `step2_markdown.md` and `prompts-en.md`.
3. Analysis: final verdict of each cell in `model-question-comparison-en.csv`, each error explained from the returned SQL or the error field; one row per model in `five-model-summary-en.csv`.

## Results (correct / evaluated)

| Model | Period (6) | Product (4) | Age (5) | Combined (5) | Total |
|---|---:|---:|---:|---:|---:|
| openai/gpt-oss-120b (Groq) | 6/6 | 4/4 | 5/5 | 5/5 | 20/20 |
| openai/gpt-oss-20b (Groq) | 6/6 | 4/4 | 3/5 | 5/5 | 18/20 |
| qwen/qwen3.8-27b (Groq) | 6/6 | 4/4 | 4/5 | 1/5 | 15/20 |
| cohere/north-mini-code:free (OpenRouter) | 6/6 | 4/4 | 1/5 | 1/5 | 12/20 |
| dots-studio/dots-3-note-preview:free (OpenRouter) | 6/6 | 4/4 | 1/5 | 0/5 | 11/20 |

Families: period C01, C04, C05, C06, C07, C20; product C03, C12, C13, C14; age C02, C08, C09, C10, C11; combined C15 to C19.

## Failures and causes

- All 24 wrong or invalid answers involve the age of the customer. Period and product questions were answered correctly by all five models (50/50).
- Causes read from the SQL: age computed from the year only (month and day ignored); birth date hard-coded to a single day; wrong birth-date window; contradictory conditions that return 0; an age test that is always true; birthday on the reference date counted in the wrong year. Details per cell in `model-question-comparison-en.csv`.
- Invalid SQL: cohere C08 (alias inside an expression) and C18 (unbalanced parentheses, not a truncation). Sandbox rejection: dots C16 (two statements returned).
- Access failure, not a wrong answer: gpt-oss-20b C20, attempt 1 refused with HTTP 429 (Groq tokens-per-minute limit); the automatic retry was correct.

## Routing hypothesis for TD 2

On this batch, any of the five models is enough for period and product questions, while only gpt-oss-120b answered all age and combined questions correctly. Hypothesis to test in TD 2: send period and product questions to a cheaper model, and age or combined questions to gpt-oss-120b with an independent check.

## Limits

- 20 questions, one run per cell, one day: no general ranking and no general error rate.
- A model can give a different answer on another run, even at temperature 0.
- Free routes have request and token limits; prices of a paid route are documented only for gpt-oss-120b.
- Deviations from the protocol (one member ran four models, longer pauses between calls) are listed in `step2_markdown.md`.

## Contributions

| Member | Contribution |
|---|---|
| Axel Warot | Reference queries and checks; ran models A, B, C and D |
| Léo Chen | Ran model E with his own OpenRouter account; analysis of its failures |
| Riyane Idrissi Kaitouli | Cross-check of references C01 to C10; prompt extraction |
| Nathan Kang | Cross-check of references C11 to C20; TD 2 preparation |
| Arthur Diserbeau | Analysis of the failures of model C |
| Timéo Brajon | Merge of the traces, comparison CSV and pivot view |
| Lucas Goutodier | Five-model summary |
| Adam Gaabi | Repository, report and Moodle submission |

## AI assistance

The reference queries and scripts were written with the help of an AI assistant (Claude). Every value was checked by a second method and against the instructor's values; no model answer was used as a reference.

## Next steps

Prepare TD 2: read `atelier-vote.py`, write the k-of-n vote, and turn the routing hypothesis above into a written rule tied to the cells of this table.
