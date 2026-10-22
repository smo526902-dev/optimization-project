"""evoopt: Genetic and Memetic Algorithms for benchmark function optimisation."""
from .baselines import RandomSearch, ScipyDE
from .benchmarks import CATEGORIES, FUNCTIONS, BenchmarkFunction, get_function
from .ga import GAConfig, GeneticAlgorithm
from .ma import MAConfig, MemeticAlgorithm
from .problem import EVALS_PER_DIM, Problem
from .results import RunResult

# Algorithms by command-line / app name.
ALGORITHMS = {
    "ga": GeneticAlgorithm,
    "ma": MemeticAlgorithm,
    "rs": RandomSearch,
    "de": ScipyDE,
}

__all__ = [
    "ALGORITHMS",
    "RandomSearch",
    "ScipyDE",
    "CATEGORIES",
    "EVALS_PER_DIM",
    "FUNCTIONS",
    "BenchmarkFunction",
    "GAConfig",
    "GeneticAlgorithm",
    "MAConfig",
    "MemeticAlgorithm",
    "Problem",
    "RunResult",
    "get_function",
]
