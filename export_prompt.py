"""Export the prompt actually used in TD 1 to prompt-td1.md, and prove it is the one used.

Run from the repository folder, giving the path of kit-td1:
    python export_prompt.py "C:\\...\\esilv-student-2026-10-18\\kit-td1"

It reads SYSTEM_PROMPT and USER_PROMPT_TEMPLATE from skeleton-multi-llm-en.py (without running it),
fills the template with schema.sql and each question, recomputes the sha256 the same way as the
skeleton (system + "\\n" + user) and compares it with prompt_sha256 in traces-td1.csv.
Coding assistance disclosed: script drafted with Claude, reviewed by the sub-group.
"""
import ast
import csv
import hashlib
import sys
from pathlib import Path

kit = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
source = (kit / "skeleton-multi-llm-en.py").read_text(encoding="utf-8")

consts = {}
for node in ast.parse(source).body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        name = node.targets[0].id
        if name in ("SYSTEM_PROMPT", "USER_PROMPT_TEMPLATE"):
            consts[name] = ast.literal_eval(node.value)
system, template = consts["SYSTEM_PROMPT"], consts["USER_PROMPT_TEMPLATE"]
schema = (kit / "schema.sql").read_text(encoding="utf-8").strip()

# Recompute the fingerprint of every question and compare with the traces.
with open("traces-td1.csv", encoding="utf-8-sig", newline="") as f:
    traces = list(csv.DictReader(f))
questions = {r["case_id"]: (r["question"], r["prompt_sha256"]) for r in traces}
ok = 0
for case, (question, sha) in sorted(questions.items()):
    user = template.format(schema=schema, question=question)
    mine = hashlib.sha256((system + "\n" + user).encode("utf-8")).hexdigest()
    ok += mine == sha
    print(f"{'[OK]  ' if mine == sha else '[DIFF]'} {case} {sha[:16]}")
distinct = {(r["case_id"], r["prompt_sha256"]) for r in traces}
same_for_all = len(distinct) == len(questions)
print(f"\n{ok}/{len(questions)} fingerprints recomputed; one fingerprint per question for all models: {same_for_all}")

with open("prompt-td1.md", "w", encoding="utf-8") as f:
    f.write("# Prompt used in TD 1\n\n")
    f.write("Taken verbatim from `skeleton-multi-llm-en.py` (kit pack 2026-10-18-students-1), unchanged, identical for the five models. ")
    f.write("`{schema}` is filled with `schema.sql`, `{question}` with the question of `questions-td1.json`. ")
    f.write("Fingerprint: `sha256(system + \"\\n\" + user)`, recorded as `prompt_sha256` on every trace line.\n\n")
    f.write(f"Check: {ok}/{len(questions)} fingerprints recomputed from this text match `traces-td1.csv`; ")
    f.write(f"one fingerprint per question shared by all models: {same_for_all}.\n\n")
    f.write("## System message\n\n```text\n" + system + "\n```\n\n")
    f.write("## User message template\n\n```text\n" + template + "\n```\n\n")
    f.write("## Schema inserted in `{schema}`\n\n```sql\n" + schema + "\n```\n\n")
    f.write("## Model parameters\n\nTemperature 0; exact identifiers and parameters in `modeles-autorises.json` (selection of 14 October 2026).\n")
print("-> prompt-td1.md")
