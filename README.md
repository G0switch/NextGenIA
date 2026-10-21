class : DIA4 ;
group : DIA4-G3
pack version : 2026-10-14-students-1

Names:
Diserbeau Arthur;
Gaabi Adam;
Brajon Timeo;
Warot Axel;
Goutodier Lucas;
Chen Léo;
Kang Nathan;
Idrissi kaitouli Riyane

Database: data/boutique.sqlite, seed 20260925, SHA-256 0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2 (identical to data/manifest.json).
Environment: Windows, PowerShell, Python 3.14.8, SQLite 3.50.4, requests 2.34.2 in a venv. API keys are set as environment variables only, never in a file.
Configuration: modeles-autorises.json of the kit, unchanged.

Replay from a fresh clone:

    python -m venv .venv
    .venv\Scripts\python.exe -m pip install requests
    .venv\Scripts\python.exe verify-data.py
    .venv\Scripts\python.exe fill_reference.py
    .venv\Scripts\python.exe check_reference.py
    .venv\Scripts\python.exe skeleton-multi-llm-en.py --replay traces-td1.jsonl

verify-data.py checks the database fingerprints; fill_reference.py reruns the 20 queries of refs/; check_reference.py recomputes them in Python from the CSV files (20/20); --replay reruns the SQL stored in the traces offline, without keys.

Completed work: TD 1 steps 1 to 3 (see reports/td1.md).
Open blocks: none.
