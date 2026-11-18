# TD 1 — SQL references and model evaluation

The group checked 20 SQL references and evaluated five models on the same questions. See the [TD 1 report](../reports/td1.md) for results and contributions.

- [Questions](questions-td1.json), [SQL queries](refs/) and [reference values](reference-td1.csv)
- [Prompt](prompt-td1.md), [model configuration](modeles-autorises.json) and [call protocol](step2_markdown.md)
- [Raw traces](traces-td1.jsonl), [CSV export](traces-td1.csv) and [five-model summary](five-model-summary-en.csv)

The TD 1 session used Windows, PowerShell, Python 3.14.8, SQLite 3.50.4 and requests 2.34.2 in a virtual environment.

## Offline checks

Run these commands from the repository root. The Python scripts use the standard library.

```powershell
Set-Location td1
Get-FileHash data/boutique.sqlite -Algorithm SHA256
python check_reference.py
python crosscheck_csv.py
python sandbox_sqlite.py --db data/boutique.sqlite
python skeleton-multi-llm-en.py --replay traces-td1.jsonl
```

The [database](data/boutique.sqlite) uses seed 20260925. Its SHA-256 is `0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2`, as recorded in the [data manifest](data/manifest.json).

`python fill_reference.py` recalculates `reference-td1.csv` from the 20 SQL queries. Replay writes `traces-replay.jsonl` and `traces-replay.csv`. Keep API keys in environment variables when running the original course kit against live models.
