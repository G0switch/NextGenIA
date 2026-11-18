#!/usr/bin/env python3
"""TD 2, Pair C: atelier-routage.py adapted to the routing rule of the sub-group.

Same priority order as the supplied choose: included capacity, then defer, then paid, then abstain.
Changes: the resources are the five TD 1 models plus the paid route of gpt-oss-120b,
eligibility is a list of families where the model was 100 % correct in TD 1,
and the checks follow the use (dashboard, customer, payout).
Synthetic availability, no API call, no key.
"""
import argparse
import json

# Families and their TD 1 cells
FAMILIES = {
    "F1": ["C01", "C04", "C05", "C06", "C07", "C20"],
    "F2": ["C02", "C08", "C09", "C11"],
    "F2b": ["C10"],
    "F3": ["C03", "C12", "C13", "C14"],
    "F1+F2": ["C15"],
    "F2+F3": ["C16"],
    "F1+F2+F3": ["C17", "C19"],
    "F1+F2b": ["C18"],
}
EASY = {"F1", "F3"}  # the 5 models were 100 % correct in TD 1

# Cost of one paid request: median tokens of gpt-oss-120b in TD 1 (638 in, 183 out)
# at 0.15 / 0.60 USD per million tokens (portfolio 2026-09-28, OpenRouter paid route)
PAID_120B = round(638 * 0.15 / 1e6 + 183 * 0.60 / 1e6, 5)

RESOURCES = [
    {"id": "groq:openai/gpt-oss-20b", "index": 9.0, "access": "free",
     "families_ok": ["F1", "F2b", "F3", "F1+F2", "F2+F3", "F1+F2+F3", "F1+F2b"],
     "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "groq:openai/gpt-oss-120b", "index": 11.6, "access": "free",
     "families_ok": list(FAMILIES),
     "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "groq:qwen/qwen3.8-27b", "index": 33.7, "access": "free",
     "families_ok": ["F1", "F2", "F3", "F1+F2b"],
     "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    # not in the portfolio: no public index, free route only, used last
    {"id": "openrouter:cohere/north-mini-code:free", "index": None, "access": "free",
     "families_ok": ["F1", "F3"],
     "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "openrouter:dots-studio/dots-3-note-preview:free", "index": None, "access": "free",
     "families_ok": ["F1", "F3"],
     "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "openrouter:openai/gpt-oss-120b (paid)", "index": 11.6, "access": "tokens",
     "families_ok": list(FAMILIES),
     "available": True, "cash": PAID_120B, "allocation": PAID_120B, "reset_minutes": None},
]


def checks_for(request):
    """Check required by the rule, from the family and the use."""
    family, use = request["family"], request["use"]
    if use == "payout":
        return "reference value check and human review"
    if family in EASY:
        return "none" if use == "dashboard" else "2-of-3 quorum"
    if family == "F2":
        return "2-of-3 quorum" if use == "dashboard" else "2-of-3 quorum and reference value check"
    return "2-of-3 quorum, abstain if no consensus" if use == "dashboard" else "reference value check"


def td1_reason(resource, family):
    cells = FAMILIES[family]
    if resource["access"] == "tokens":
        return f"same model as groq:openai/gpt-oss-120b, measured on Groq: correct on {', '.join(cells)} in TD 1 ({len(cells)}/{len(cells)})"
    return f"{resource['id']} correct on {', '.join(cells)} in TD 1 ({len(cells)}/{len(cells)})"


def order(r):
    # cheapest first; at equal price, lowest public index (smaller model), unknown index last
    return (r["allocation"], r["index"] if r["index"] is not None else 999, r["id"])


def choose(request, resources):
    """Same branches as the supplied choose; eligibility comes from the TD 1 cells."""
    if request["family"] not in FAMILIES:
        return {"action": "abstain", "resource": None, "cash": 0, "checks": "not applicable",
                "reason": f"family {request['family']} not measured in TD 1"}
    checks = checks_for(request)
    eligible = [r for r in resources if request["family"] in r["families_ok"]]
    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    if included:
        chosen = min(included, key=order)
        return {"action": "run", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": "eligible included capacity, " + td1_reason(chosen, request["family"])}
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: (r["reset_minutes"],) + order(r))
        return {"action": "defer", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": "recheck availability at wake-up, " + td1_reason(chosen, request["family"]),
                "wake_in_minutes": chosen["reset_minutes"]}
    paid = [r for r in eligible if r["available"] and r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=order)
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"], "checks": checks,
                "reason": "paid route within the budget, " + td1_reason(chosen, request["family"])}
    return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
            "reason": "no eligible resource within deadline and budget"}


def exhaust(ids, minutes=1):
    """Groq free limits are per minute: the C20 retry of gpt-oss-20b worked 3 s after a 429."""
    return [dict(r, available=False, reset_minutes=minutes) if r["id"] in ids else dict(r)
            for r in RESOURCES]


def scenarios():
    base = {"family": "F1", "use": "dashboard", "can_wait": True,
            "deadline_minutes": 120, "budget": 0.001}
    groq_gpt = exhaust({"groq:openai/gpt-oss-20b", "groq:openai/gpt-oss-120b"})
    return [
        ("simple", base, RESOURCES),
        ("complex", {**base, "family": "F2b", "use": "customer"}, RESOURCES),
        ("priority", {**base, "family": "F2b"}, exhaust({"groq:openai/gpt-oss-20b"})),
        ("deferrable", {**base, "family": "F2b"}, groq_gpt),
        ("urgent", {**base, "family": "F2b", "can_wait": False, "deadline_minutes": 0}, groq_gpt),
        ("budget exhausted", {**base, "family": "F2b", "can_wait": False, "budget": 0}, groq_gpt),
        ("high impact", {**base, "family": "F2", "use": "payout"}, RESOURCES),
        ("unknown family", {**base, "family": "F4"}, RESOURCES),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", help="show only the named scenario")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios():
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "request": request,
                          "result": choose(request, resources)}))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()
