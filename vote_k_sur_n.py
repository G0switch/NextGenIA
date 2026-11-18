    # ------------------------------------------------------------------
    # TD 2, Step 1 (Pair A): paste this method inside `class Orchestrateur`
    # in skeleton-multi-llm-en.py, replacing the `raise NotImplementedError`.
    # Standard library only. `Counter` is imported locally so the skeleton's
    # imports do not need to change.
    # ------------------------------------------------------------------
    def vote_k_sur_n(self, traces_question, k):
        """k-of-n vote over distinct (provider, model) pairs, strict majority.

        traces_question: the n panel members for ONE question. Each element has
            provider, model_requested, value (int cents or None) and
            verdict ("executed" or "error"). Objects or dicts are accepted.
        k: threshold, must satisfy n // 2 < k <= n.

        Contract (TD 2):
        1. Only executed proposals with a value vote. Errors and unavailable
           members still count in n, but cast no vote.
        2. k must be a strict majority (n // 2 < k <= n), otherwise ValueError.
        3. The same (provider, model_requested) twice raises ValueError:
           a duplicate is not a second vote.
        4. If a value reaches k votes -> consensus with that value.
        5. Otherwise -> abstention: value None, votes = largest count, models [].
        The reference is never an input: the vote decides before any check.
        """
        from collections import Counter

        def field(proposal, name):
            if isinstance(proposal, dict):
                return proposal.get(name)
            return getattr(proposal, name, None)

        proposals = list(traces_question)
        n = len(proposals)

        # Rule 2: strict majority. bool is excluded because True == 1 in Python.
        if isinstance(k, bool) or not isinstance(k, int):
            raise ValueError(f"k must be an integer, got {k!r}")
        if n == 0:
            raise ValueError("Empty panel: n = 0, no quorum is possible.")
        if not (n // 2 < k <= n):
            raise ValueError(
                f"k={k} is not a strict majority of n={n}: need {n // 2} < k <= {n}."
            )

        # Rule 3: each (provider, model) pair appears once in the panel.
        seen = set()
        for proposal in proposals:
            key = (field(proposal, "provider"), field(proposal, "model_requested"))
            if key in seen:
                raise ValueError(
                    f"Duplicate panel member {key[0]}:{key[1]}: "
                    "a repeated call is not a second vote. Keep only the last attempt."
                )
            seen.add(key)

        # Rule 1: only executed proposals carrying a value vote.
        ballots = {}  # value -> list of "provider/model" in panel order
        for proposal in proposals:
            value = field(proposal, "value")
            if field(proposal, "verdict") != "executed" or value is None:
                continue
            label = f"{field(proposal, 'provider')}:{field(proposal, 'model_requested')}"
            ballots.setdefault(value, []).append(label)

        counts = Counter({value: len(models) for value, models in ballots.items()})

        # Rule 4: since k > n/2, at most one value can reach k.
        for value, votes in counts.items():
            if votes >= k:
                return {"consensus": True, "value": value,
                        "votes": votes, "models": list(ballots[value])}

        # Rule 5: abstain, never invent a value.
        largest = max(counts.values(), default=0)
        return {"consensus": False, "value": None, "votes": largest, "models": []}
