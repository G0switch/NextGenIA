"""Reproduce DEMO-VOTE with one invented sale and the Pair A vote."""

import json
import runpy
import sqlite3
from contextlib import closing
from pathlib import Path

VOTE_WORKSHOP = Path(__file__).resolve().parents[1] / "A-quorum" / "atelier-vote.py"


def main():
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("CREATE TABLE sales (sale_date TEXT, amount_cents INTEGER)")
        db.execute("INSERT INTO sales VALUES ('2026-01-01', 100)")

        query = """
            SELECT COALESCE(SUM(amount_cents), 0)
            FROM sales
            WHERE sale_date {lower_bound} '2026-01-01'
              AND sale_date < '2026-01-02'
        """
        strict_total, inclusive_total = [
            db.execute(query.format(lower_bound=operator)).fetchone()[0]
            for operator in (">", ">=")
        ]

    values = [strict_total, strict_total, inclusive_total]
    proposals = [
        {"provider": "synthetic", "model_requested": f"proposal-{index}",
         "value": value, "verdict": "executed"}
        for index, value in enumerate(values, start=1)
    ]
    workshop = runpy.run_path(str(VOTE_WORKSHOP))
    vote = workshop["load_vote"]()
    independent_reference = 100  # The single invented sale is on the included date.
    result = workshop["evaluate"](vote, proposals, independent_reference)
    print(json.dumps({"example": "DEMO-VOTE", "nature": "simulation", "n": 3, "k": 2,
                      "strict_lower_bound": strict_total, "inclusive_lower_bound": inclusive_total,
                      "proposals": values, **result}))


if __name__ == "__main__":
    main()
