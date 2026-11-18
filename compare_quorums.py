#!/usr/bin/env python3
"""TD 2, Step 1 (Pair A): 2-of-3 fixed panel vs 3-of-5 quorum over all five TD 1 models.

Uses the student's vote_k_sur_n from skeleton-multi-llm-en.py (same loader as atelier-vote.py).
Same proposal rules as atelier-vote.py: last CSV row per member is its last attempt;
only verdict correct/incorrect with a value becomes "executed"; everything else is "error"
(kept in n, no vote). The reference is read ONLY after the decision, to fill the table.

    python3 compare_quorums.py --traces traces-td1.csv > reports/quorum-table.md
    python3 compare_quorums.py --traces traces-td1.csv --csv reports/quorum-table.csv
"""
import argparse
import csv
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

PANEL3 = [
    ("groq", "openai/gpt-oss-120b"),
    ("openrouter", "cohere/north-mini-code:free"),
    ("groq", "qwen/qwen3.8-27b"),
]
CASES = [f"C{i:02d}" for i in range(1, 21)]


def load_vote(skeleton):
    spec = importlib.util.spec_from_file_location("student_skeleton", skeleton)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return lambda proposals, k: module.Orchestrateur.vote_k_sur_n(None, proposals, k)


def short(model):
    if isinstance(model, tuple):
        model = model[1]
    return model.split("/")[-1].replace(":free", "")


def last_rows(rows, case, nature):
    selected = {}
    for row in rows:  # chronological export: the last row wins
        if row["case_id"] == case and row["nature"] == nature:
            selected[(row["provider"], row["model_requested"])] = row
    return selected


def proposals(selected, panel):
    out = []
    for provider, model in panel:
        row = selected.get((provider, model), {})
        value = row.get("value", "")
        valid = row.get("verdict") in {"correct", "incorrect"} and value not in {None, ""}
        out.append(SimpleNamespace(provider=provider, model_requested=model,
                                   value=int(value) if valid else None,
                                   verdict="executed" if valid else "error"))
    return out


def cell(row):
    if not row:
        return "absent"
    v = row.get("verdict", "")
    if v in {"correct", "incorrect"}:
        return f"{row.get('value')} ({'ok' if v == 'correct' else 'KO'})"
    detail = row.get("http_status") or row.get("error") or ""
    return f"{v}{' ' + str(detail)[:20] if detail else ''}"


def fmt(dec):
    if dec["consensus"]:
        return f"**{dec['value']}** ({dec['votes']} votes)"
    return f"abstain (max {dec['votes']})"


def agree(dec, ref):
    if not dec["consensus"]:
        return "abstain"
    if ref is None:
        return "?"
    return "yes" if dec["value"] == ref else "**NO**"


def explain(d3, d5, sel, panel5, ref):
    extra = [m for m in panel5 if m not in PANEL3]
    extra_txt = ", ".join(f"{short(m)}={cell(sel.get(m))}" for m in extra)
    if d3["consensus"] == d5["consensus"] and d3["value"] == d5["value"]:
        return f"same decision; extra members: {extra_txt}"
    if not d3["consensus"] and d5["consensus"]:
        return f"abstention -> consensus {d5['value']} with {d5['votes']}/5; extra: {extra_txt}"
    if d3["consensus"] and not d5["consensus"]:
        failed = [short(m) for m in panel5 if sel.get(m, {}).get("verdict") not in {"correct", "incorrect"}]
        why = f" (no vote from: {', '.join(failed)})" if failed else ""
        return (f"consensus {d3['value']} lost: only {d5['votes']}/5 reach the same value, k=3 needed"
                f"{why}; extra: {extra_txt}")
    return f"value changed {d3['value']} -> {d5['value']}; extra: {extra_txt}"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--traces", type=Path, required=True)
    ap.add_argument("--skeleton", type=Path, default=Path(__file__).with_name("skeleton-multi-llm-en.py"))
    ap.add_argument("--nature", default="real")
    ap.add_argument("--csv", type=Path)
    args = ap.parse_args()

    vote = load_vote(args.skeleton)
    rows = list(csv.DictReader(args.traces.open(encoding="utf-8", newline="")))
    rows = [r for r in rows if r["nature"] == args.nature]
    models = sorted({(r["provider"], r["model_requested"]) for r in rows})
    if len(models) != 5:
        sys.exit(f"Expected 5 distinct (provider, model) in traces, found {len(models)}: {models}")
    missing = [m for m in PANEL3 if m not in models]
    if missing:
        sys.exit(f"Fixed panel members absent from traces: {missing}")
    panel5 = PANEL3 + [m for m in models if m not in PANEL3]

    table, stats = [], {"3": [0, 0, 0], "5": [0, 0, 0]}  # right, wrong, abstain
    for case in CASES:
        sel = last_rows(rows, case, args.nature)
        d3 = vote(proposals(sel, PANEL3), 2)
        d5 = vote(proposals(sel, panel5), 3)
        # reference read only now, after both decisions
        refs = {int(r["reference"]) for r in sel.values() if r.get("reference") not in {None, ""}}
        if len(refs) > 1:
            sys.exit(f"{case}: conflicting references {refs}")
        ref = next(iter(refs), None)
        for key, d in (("3", d3), ("5", d5)):
            a = agree(d, ref)
            stats[key][0 if a == "yes" else 1 if a == "**NO**" else 2] += 1
        table.append({"case": case, **{short(m[1]): cell(sel.get(m)) for m in panel5},
                      "2-of-3": fmt(d3), "3-of-5": fmt(d5), "reference": ref,
                      "agree 2/3": agree(d3, ref), "agree 3/5": agree(d5, ref),
                      "change": explain(d3, d5, sel, panel5, ref)})

    cols = list(table[0].keys())
    print("| " + " | ".join(cols) + " |")
    print("|" + "---|" * len(cols))
    for t in table:
        print("| " + " | ".join(str(t[c]) for c in cols) + " |")
    print()
    for key, label in (("3", "2-of-3 (fixed panel)"), ("5", "3-of-5 (five TD 1 models)")):
        r, w, a = stats[key]
        print(f"- {label}: {r} correct consensus, {w} wrong consensus, {a} abstentions, out of 20.")
    if args.csv:
        with args.csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader(); w.writerows(table)


if __name__ == "__main__":
    main()
