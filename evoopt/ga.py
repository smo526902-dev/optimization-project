"""Real-coded Genetic Algorithm (GA) for continuous minimisation.

Each individual is a vector of d real numbers inside the search domain. One
generation of the GA is:

1. Selection    choose parents, favouring low f(x)
2. Crossover    recombine pairs of parents (with probability crossover_rate)
3. Mutation     perturb single genes (each with probability mutation_rate)
4. Evaluation   every child costs one function evaluation
5. Replacement  the `elitism` best parents survive unchanged; children fill the rest
6. Learning     a hook for the Memetic Algorithm; a plain GA does nothing here

The run stops when the evaluation budget is spent, or earlier if a target
error is set and reached.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, replace

import numpy as np

from . import operators as ops
from .problem import Problem
from .results import RunResult


@dataclass
class GAConfig:
    pop_size: int | None = None  # None: 50 for d < 10, otherwise 100
    selection: str = "tournament"  # tournament | roulette | rank
    tournament_size: int = 3
    rank_pressure: float = 1.5
    crossover: str = "sbx"  # sbx | blx | arithmetic
    crossover_rate: float = 0.9
    sbx_eta: float = 15.0
    blx_alpha: float = 0.5
    mutation: str = "polynomial"  # polynomial | gaussian | uniform
    mutation_rate: float | None = None  # None: 1/d, i.e. one gene per child on average
    mutation_eta: float = 20.0
    mutation_sigma: float = 0.1
    elitism: int = 2
    target_error: float | None = None  # stop early once f - f* <= target_error
    record_population: bool = False  # keep every generation's population (2-D animation)

    def resolved(self, dim):
        """A copy with the dimension-dependent defaults filled in."""
        return replace(
            self,
            pop_size=self.pop_size or (50 if dim < 10 else 100),
            mutation_rate=1.0 / dim if self.mutation_rate is None else self.mutation_rate,
        )

    def validate(self):
        for name, value, choices in (
            ("selection", self.selection, ops.SELECTIONS),
            ("crossover", self.crossover, ops.CROSSOVERS),
            ("mutation", self.mutation, ops.MUTATIONS),
        ):
            if value not in choices:
                raise ValueError(f"{name} must be one of {choices}, not {value!r}")
        if self.pop_size is not None and self.pop_size < 2:
            raise ValueError("pop_size must be at least 2")
        if self.pop_size is not None and not 0 <= self.elitism < self.pop_size:
            raise ValueError("elitism must be between 0 and pop_size - 1")
        if not 0 <= self.crossover_rate <= 1:
            raise ValueError("crossover_rate must be in [0, 1]")
        if self.mutation_rate is not None and not 0 <= self.mutation_rate <= 1:
            raise ValueError("mutation_rate must be in [0, 1]")
        if self.tournament_size < 1:
            raise ValueError("tournament_size must be at least 1")
        if not 1 <= self.rank_pressure <= 2:
            raise ValueError("rank_pressure must be in [1, 2]")


class GeneticAlgorithm:
    name = "GA"
    Config = GAConfig

    def __init__(self, config: GAConfig | None = None, **params):
        self.config = replace(config or self.Config(), **params)
        self.config.validate()

    def __repr__(self):
        return f"{type(self).__name__}({self.config})"

    # ------------------------------------------------------------------ run
    def run(self, problem: Problem, seed=None, callback=None) -> RunResult:
        """Minimise ``problem`` until its evaluation budget is spent.

        ``callback(state)``, if given, is called after every generation with a
        dict holding the generation number, population, fitness, evaluations
        used and best value so far. Returning True from it stops the run early
        (the app uses this for live plots and a stop button).
        """
        self.cfg = cfg = self.config.resolved(problem.dim)
        cfg.validate()
        rng = np.random.default_rng(seed)
        start = time.perf_counter()

        pop = problem.random_points(cfg.pop_size, rng)
        fit = problem.evaluate(pop)
        generation = 0
        history = {key: [] for key in ("generation", "evals", "best", "pop_best", "pop_mean", "diversity")}
        snapshots = [] if cfg.record_population else None
        self._log(history, snapshots, generation, problem, pop, fit)

        while not self._finished(problem):
            pop, fit = self.step(problem, pop, fit, rng)
            generation += 1
            self._log(history, snapshots, generation, problem, pop, fit)
            if callback is not None and callback(
                {
                    "generation": generation,
                    "population": pop,
                    "fitness": fit,
                    "n_evals": problem.n_evals,
                    "best_f": problem.best_f,
                    "best_x": problem.best_x,
                }
            ):
                break

        return RunResult.from_problem(
            problem,
            self.name,
            seed,
            generations=generation,
            runtime=time.perf_counter() - start,
            history=history,
            params=asdict(cfg),
            snapshots=snapshots,
        )

    def _finished(self, problem):
        target = self.cfg.target_error
        return problem.exhausted or (target is not None and problem.best_error <= target)

    # ----------------------------------------------------------- generation
    def step(self, problem, pop, fit, rng):
        """One generation: offspring, evaluation, elitist replacement, learning."""
        children = self.make_offspring(problem, pop, fit, rng)
        child_fit = problem.evaluate(children)
        elite = np.argsort(fit)[: self.cfg.elitism]
        pop = np.vstack([pop[elite], children])
        fit = np.concatenate([fit[elite], child_fit])
        return self.learn(problem, pop, fit, rng)

    def make_offspring(self, problem, pop, fit, rng):
        """Selection, crossover and mutation: len(pop) - elitism new children."""
        n_children = len(pop) - self.cfg.elitism
        n_pairs = (n_children + 1) // 2
        parents = self.select(fit, 2 * n_pairs, rng)
        P1, P2 = pop[parents[:n_pairs]], pop[parents[n_pairs:]]
        C1, C2 = self.crossover(P1, P2, problem, rng)
        crossed = rng.random(n_pairs) < self.cfg.crossover_rate  # the rest are copied
        C1 = np.where(crossed[:, None], C1, P1)
        C2 = np.where(crossed[:, None], C2, P2)
        children = np.vstack([C1, C2])[:n_children]
        return self.mutate(children, problem, rng)

    def learn(self, problem, pop, fit, rng):
        """Individual learning. A plain GA has none; the Memetic Algorithm overrides this."""
        return pop, fit

    # ------------------------------------------------------------ operators
    def select(self, fit, n, rng):
        cfg = self.cfg
        if cfg.selection == "tournament":
            return ops.tournament_selection(fit, n, rng, k=cfg.tournament_size)
        if cfg.selection == "rank":
            return ops.rank_selection(fit, n, rng, pressure=cfg.rank_pressure)
        return ops.roulette_selection(fit, n, rng)

    def crossover(self, P1, P2, problem, rng):
        cfg, lo, hi = self.cfg, problem.lower, problem.upper
        if cfg.crossover == "sbx":
            return ops.sbx_crossover(P1, P2, rng, lo, hi, eta=cfg.sbx_eta)
        if cfg.crossover == "blx":
            return ops.blx_alpha_crossover(P1, P2, rng, lo, hi, alpha=cfg.blx_alpha)
        return ops.arithmetic_crossover(P1, P2, rng, lo, hi)

    def mutate(self, X, problem, rng):
        cfg, lo, hi = self.cfg, problem.lower, problem.upper
        if cfg.mutation == "polynomial":
            return ops.polynomial_mutation(X, rng, lo, hi, cfg.mutation_rate, eta=cfg.mutation_eta)
        if cfg.mutation == "gaussian":
            return ops.gaussian_mutation(X, rng, lo, hi, cfg.mutation_rate, sigma=cfg.mutation_sigma)
        return ops.uniform_mutation(X, rng, lo, hi, cfg.mutation_rate)

    # -------------------------------------------------------------- logging
    @staticmethod
    def _log(history, snapshots, generation, problem, pop, fit):
        finite = fit[np.isfinite(fit)]
        history["generation"].append(generation)
        history["evals"].append(problem.n_evals)
        history["best"].append(problem.best_f)
        history["pop_best"].append(float(finite.min()) if finite.size else np.inf)
        history["pop_mean"].append(float(finite.mean()) if finite.size else np.inf)
        history["diversity"].append(float(np.mean(pop.std(axis=0) / problem.span)))
        if snapshots is not None:
            snapshots.append(pop.copy())
