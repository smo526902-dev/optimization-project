"""What the experiments run: problems, algorithms, seeds, budgets and ablations."""
from __future__ import annotations

from evoopt import FUNCTIONS
from evoopt.operators import CROSSOVERS, MUTATIONS, SELECTIONS

# A run "succeeds" when its best error f - f* is at most this.
SUCCESS_ERROR = 1e-4
# CEC benchmark convention: an error below this is taken as zero when results
# are compared, so floating-point rounding (1e-15 against 0) never counts as a
# difference between algorithms. The raw results keep the exact values.
ERROR_FLOOR = 1e-8
# Convergence is recorded at 1%, 2%, ..., 100% of each run's budget.
CURVE_POINTS = 100

MODES = {
    # 30 independent runs per setting, full budget of 10,000 * d evaluations
    "full": dict(seeds=tuple(range(30)), budget_scale=1.0),
    # smoke test: 3 runs at a tenth of the budget
    "quick": dict(seeds=tuple(range(3)), budget_scale=0.1),
}

# ------------------------------------------------------------------ main suite
# Display name -> (algorithm key in evoopt.ALGORITHMS, parameters)
MAIN_ALGORITHMS = {
    "GA": ("ga", {}),
    "MA": ("ma", {}),
    "RS": ("rs", {}),
    "DE": ("de", {}),
}


def main_problems():
    """Scalable functions at d = 2, 10, 30; the others at their own dimensions."""
    for key, fn in FUNCTIONS.items():
        for d in fn.dims or (2, 10, 30):
            yield key, d


# ------------------------------------------------------------- ablation suite
ABLATION_PROBLEMS = [
    ("rastrigin", 10),
    ("rosenbrock", 10),
    ("ackley", 10),
    ("griewank", 10),
    ("schwefel", 10),
]

# Each ablation varies one design choice and keeps every other setting at its
# default. Config label -> (algorithm key, parameters). The first entry of each
# ablation is the default configuration.
ABLATIONS = {
    "local_search": {
        "Hooke-Jeeves": ("ma", {}),
        "hill climbing": ("ma", {"local_search": "hill_climbing"}),
    },
    "learning": {
        "Lamarckian": ("ma", {}),
        "Baldwinian": ("ma", {"learning": "baldwinian"}),
    },
    "ls_rate": {
        **{"0.05": ("ma", {})},
        **{f"{r}": ("ma", {"ls_rate": r}) for r in (0.0, 0.02, 0.1, 0.2)},
    },
    "selection": {s: ("ga", {"selection": s}) for s in SELECTIONS},
    "crossover": {c: ("ga", {"crossover": c}) for c in CROSSOVERS},
    "mutation": {
        **{f"GA {m}": ("ga", {"mutation": m}) for m in MUTATIONS},
        **{f"MA {m}": ("ma", {"mutation": m}) for m in MUTATIONS},
    },
    "pop_size": {f"{n}": ("ga", {"pop_size": n}) for n in (100, 20, 50, 200)},
    # every ablation problem has d = 10, so these are 1/d, 0.5/d, 2/d and 5/d
    "mutation_rate": {f"{k}/d": ("ga", {"mutation_rate": k / 10}) for k in (1, 0.5, 2, 5)},
}

SUITES = ("main", "ablations")
