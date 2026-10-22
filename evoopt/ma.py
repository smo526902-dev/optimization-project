"""Memetic Algorithm (MA): the Genetic Algorithm plus individual learning.

The MA inherits the GA's generation loop unchanged. The only difference is the
``learn`` step at the end of each generation, where some individuals are
improved by a local search, the "meme" (Moscato, 1989):

* the best individual of the population (if ``ls_best``), with a long budget
  of ``ls_best_evals`` evaluations: intensive refinement of the elite, and
* each new child, independently with probability ``ls_rate``, with a short
  budget of ``ls_child_evals``: enough to settle the child into the bottom of
  its local basin, so that selection compares basins rather than raw points.

Learning model
    lamarckian  the improved solution replaces the individual, so acquired
                improvements are inherited by its offspring
    baldwinian  only the fitness is updated and the genes stay as they were:
                learning changes which individuals survive, not what they pass on

Local-search chains: the final step size of every refined individual is
remembered, so when the same individual is refined again in a later generation
its search resumes where it stopped (Molina et al., 2010) instead of starting
over with a large step and repeating the same work.

Every local-search evaluation is charged to the same budget as the GA's, so
GA and MA are always compared at an equal number of function evaluations.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from .ga import GAConfig, GeneticAlgorithm
from .local_search import LOCAL_SEARCHES, converged

LEARNING_MODELS = ("lamarckian", "baldwinian")


@dataclass
class MAConfig(GAConfig):
    local_search: str = "hooke_jeeves"  # hooke_jeeves | hill_climbing
    learning: str = "lamarckian"  # lamarckian | baldwinian
    ls_best: bool = True  # refine the best individual every generation...
    ls_best_evals: int | None = None  # ...with this many evaluations; None: 20 * d
    ls_rate: float = 0.05  # probability that each child is refined...
    ls_child_evals: int | None = None  # ...with this many evaluations; None: 5 * d

    def resolved(self, dim):
        return replace(
            super().resolved(dim),
            ls_best_evals=self.ls_best_evals or 20 * dim,
            ls_child_evals=self.ls_child_evals or 5 * dim,
        )

    def validate(self):
        super().validate()
        if self.local_search not in LOCAL_SEARCHES:
            raise ValueError(f"local_search must be one of {tuple(LOCAL_SEARCHES)}, not {self.local_search!r}")
        if self.learning not in LEARNING_MODELS:
            raise ValueError(f"learning must be one of {LEARNING_MODELS}, not {self.learning!r}")
        if not 0 <= self.ls_rate <= 1:
            raise ValueError("ls_rate must be in [0, 1]")
        for name in ("ls_best_evals", "ls_child_evals"):
            if getattr(self, name) is not None and getattr(self, name) < 1:
                raise ValueError(f"{name} must be at least 1")


class MemeticAlgorithm(GeneticAlgorithm):
    name = "MA"
    Config = MAConfig

    def reset_learning(self):
        self._steps = {}  # genes (as bytes) -> step to resume from; None = fully refined
        self._ls_evals = self._ls_calls = self._ls_improved = 0

    def run(self, problem, seed=None, callback=None):
        self.reset_learning()
        result = super().run(problem, seed=seed, callback=callback)
        result.stats = {
            "ls_calls": self._ls_calls,
            "ls_improved": self._ls_improved,
            "ls_evals": self._ls_evals,
            "ls_share": self._ls_evals / max(result.n_evals, 1),
        }
        return result

    def learn(self, problem, pop, fit, rng):
        """Refine the best individual and a random share of the children.

        GeneticAlgorithm.step puts the elites first and the children after them,
        so rows ``elitism ..`` are this generation's children.
        """
        cfg = self.cfg
        best = int(np.argmin(fit))
        chosen = [best] if cfg.ls_best else []
        if cfg.ls_rate > 0:
            children = np.arange(cfg.elitism, len(pop))
            chosen += [int(i) for i in children[rng.random(len(children)) < cfg.ls_rate] if i not in chosen]

        if chosen:
            search = LOCAL_SEARCHES[cfg.local_search]
            # A fresh search starts with steps on the scale of the population's spread.
            fresh_step = np.clip(pop.std(axis=0), 1e-8 * problem.span, 0.1 * problem.span)
            pop, fit = pop.copy(), fit.copy()
            for i in chosen:
                if problem.exhausted:
                    break
                if not np.isfinite(fit[i]):
                    continue
                key = pop[i].tobytes()
                step = self._steps.get(key, fresh_step)
                if step is None:  # this individual is already fully refined
                    continue
                budget = cfg.ls_best_evals if i == best and cfg.ls_best else cfg.ls_child_evals
                used_before = problem.n_evals
                x, fx, step = search(problem, pop[i], fit[i], step, budget, rng)
                self._ls_calls += 1
                self._ls_evals += problem.n_evals - used_before
                self._ls_improved += fx < fit[i]
                fit[i] = fx
                if cfg.learning == "lamarckian":
                    pop[i] = x
                    self._steps[x.tobytes()] = None if converged(step, problem) else step
                else:
                    self._steps[key] = None  # Baldwinian: an individual learns once

        # Forget the search state of individuals that have left the population.
        alive = {row.tobytes() for row in pop}
        self._steps = {k: v for k, v in self._steps.items() if k in alive}
        return pop, fit
