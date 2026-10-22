"""Benchmark functions from the SFU Virtual Library of Simulation Experiments.

Surjanovic, S. & Bingham, D. (2013). Virtual Library of Simulation Experiments:
Test Functions and Datasets. https://www.sfu.ca/~ssurjano/optimization.html

Every function takes a 2-D array ``X`` of shape (n, d), i.e. n candidate
solutions with d variables each, and returns a 1-D array of n objective values.
This lets an algorithm evaluate a whole population in one vectorised call.

The twelve functions cover all six landscape categories used by the library.
Where the library prints a rounded optimum (e.g. Styblinski-Tang, Schwefel,
Eggholder), the value stored here was recomputed to full double precision so
that the error ``f(x) - f*`` of a perfect solution is ~0 rather than ~1e-4.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

SFU_URL = "https://www.sfu.ca/~ssurjano/"

# Category labels, in the order the SFU library lists them.
MANY_LOCAL_MINIMA = "Many local minima"
BOWL = "Bowl-shaped"
PLATE = "Plate-shaped"
VALLEY = "Valley-shaped"
STEEP = "Steep ridges / drops"
OTHER = "Other"
CATEGORIES = (MANY_LOCAL_MINIMA, BOWL, PLATE, VALLEY, STEEP, OTHER)


# --------------------------------------------------------------------------- #
# Objective functions (vectorised: X has shape (n, d), result has shape (n,))
# --------------------------------------------------------------------------- #

def sphere(X):
    return np.sum(X**2, axis=1)


def zakharov(X):
    i = np.arange(1, X.shape[1] + 1)
    s = np.sum(0.5 * i * X, axis=1)
    return np.sum(X**2, axis=1) + s**2 + s**4


def rosenbrock(X):
    return np.sum(100.0 * (X[:, 1:] - X[:, :-1] ** 2) ** 2 + (X[:, :-1] - 1.0) ** 2, axis=1)


def six_hump_camel(X):
    x1, x2 = X[:, 0], X[:, 1]
    return (4 - 2.1 * x1**2 + x1**4 / 3) * x1**2 + x1 * x2 + (-4 + 4 * x2**2) * x2**2


# Michalewicz is separable (term i depends on x_i only), so its global minimiser
# is found one coordinate at a time; the d-dimensional optimum is the first d
# coordinates of this sequence. Solved numerically to ~1e-15.
MICHALEWICZ_X_OPT = (
    2.2029055201716, 1.5707963267949, 1.28499157054941, 1.92305846986544, 1.72046977256586,
    1.5707963267949, 1.4544139713617, 1.75608652094415, 1.65571741682079, 1.5707963267949,
)


def michalewicz(X, m=10):
    i = np.arange(1, X.shape[1] + 1)
    return -np.sum(np.sin(X) * np.sin(i * X**2 / np.pi) ** (2 * m), axis=1)


def easom(X):
    x1, x2 = X[:, 0], X[:, 1]
    return -np.cos(x1) * np.cos(x2) * np.exp(-((x1 - np.pi) ** 2) - (x2 - np.pi) ** 2)


def rastrigin(X):
    d = X.shape[1]
    return 10 * d + np.sum(X**2 - 10 * np.cos(2 * np.pi * X), axis=1)


def ackley(X, a=20.0, b=0.2, c=2 * np.pi):
    d = X.shape[1]
    return (
        -a * np.exp(-b * np.sqrt(np.sum(X**2, axis=1) / d))
        - np.exp(np.sum(np.cos(c * X), axis=1) / d)
        + a
        + np.e
    )


def griewank(X):
    i = np.arange(1, X.shape[1] + 1)
    return np.sum(X**2, axis=1) / 4000 - np.prod(np.cos(X / np.sqrt(i)), axis=1) + 1


# max of x*sin(sqrt|x|) on [-500, 500]; the library rounds it to 418.9829.
SCHWEFEL_CONSTANT = 418.9828872724328


def schwefel(X):
    d = X.shape[1]
    return SCHWEFEL_CONSTANT * d - np.sum(X * np.sin(np.sqrt(np.abs(X))), axis=1)


def eggholder(X):
    x1, x2 = X[:, 0], X[:, 1]
    return -(x2 + 47) * np.sin(np.sqrt(np.abs(x2 + x1 / 2 + 47))) - x1 * np.sin(
        np.sqrt(np.abs(x1 - (x2 + 47)))
    )


def styblinski_tang(X):
    return 0.5 * np.sum(X**4 - 16 * X**2 + 5 * X, axis=1)


# --------------------------------------------------------------------------- #
# Metadata
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class BenchmarkFunction:
    """A benchmark function together with everything needed to optimise and
    score it: its search domain, its known global optimum, and a description.

    domain
        One ``(low, high)`` pair applied to every variable, or a tuple with one
        pair per variable for fixed-dimension functions.
    dims
        The dimensions the function is defined for; ``None`` means any d >= 2.
    f_opt
        The global minimum value. A dict maps dimension -> value when it does
        not follow a simple rule (Michalewicz).
    f_opt_per_dim
        If true the global minimum is ``f_opt * d`` (Styblinski-Tang).
    x_opt_coord
        For scalable functions whose minimiser is (c, c, ..., c), the value c.
    x_opt_points
        For fixed-dimension functions, every known global minimiser.
    """

    key: str
    name: str
    category: str
    func: object
    domain: tuple
    f_opt: float | dict
    formula: str
    description: str
    page: str
    dims: tuple[int, ...] | None = None
    f_opt_per_dim: bool = False
    x_opt_coord: float | None = None
    x_opt_points: tuple[tuple[float, ...], ...] = ()

    def __call__(self, X):
        return self.func(np.atleast_2d(np.asarray(X, dtype=float)))

    @property
    def scalable(self):
        return self.dims is None

    @property
    def url(self):
        return SFU_URL + self.page

    def supports(self, d):
        return d >= 2 if self.dims is None else d in self.dims

    def _check(self, d):
        if not self.supports(d):
            allowed = "any d >= 2" if self.dims is None else f"d in {self.dims}"
            raise ValueError(f"{self.name} is defined for {allowed}, not d={d}")

    def bounds(self, d):
        """Return (lower, upper) arrays of length d."""
        self._check(d)
        if np.ndim(self.domain) == 1:
            low, high = self.domain
            return np.full(d, float(low)), np.full(d, float(high))
        pairs = np.asarray(self.domain, dtype=float)
        return pairs[:, 0].copy(), pairs[:, 1].copy()

    def f_star(self, d):
        """Global minimum value in dimension d."""
        self._check(d)
        if isinstance(self.f_opt, dict):
            return self.f_opt[d]
        return self.f_opt * d if self.f_opt_per_dim else float(self.f_opt)

    def x_star(self, d):
        """Known global minimiser(s) as an array of shape (k, d), or None."""
        self._check(d)
        if self.x_opt_coord is not None:
            return np.full((1, d), self.x_opt_coord)
        points = [p for p in self.x_opt_points if len(p) == d]
        return np.array(points) if points else None


FUNCTIONS = {
    f.key: f
    for f in [
        BenchmarkFunction(
            key="sphere",
            name="Sphere",
            category=BOWL,
            func=sphere,
            domain=(-5.12, 5.12),
            f_opt=0.0,
            x_opt_coord=0.0,
            formula=r"f(\mathbf{x}) = \sum_{i=1}^{d} x_i^2",
            description="Convex, unimodal and separable. The easiest case: it checks "
            "that an algorithm converges at all, and how fast.",
            page="spheref.html",
        ),
        BenchmarkFunction(
            key="zakharov",
            name="Zakharov",
            category=PLATE,
            func=zakharov,
            domain=(-5.0, 10.0),
            f_opt=0.0,
            x_opt_coord=0.0,
            formula=r"f(\mathbf{x}) = \sum_{i=1}^{d} x_i^2 + \Big(\sum_{i=1}^{d} 0.5\,i\,x_i\Big)^2"
            r" + \Big(\sum_{i=1}^{d} 0.5\,i\,x_i\Big)^4",
            description="Unimodal but non-separable: a flat plate around the optimum with "
            "steep quartic walls. Weighting by i couples all variables.",
            page="zakharov.html",
        ),
        BenchmarkFunction(
            key="rosenbrock",
            name="Rosenbrock",
            category=VALLEY,
            func=rosenbrock,
            domain=(-5.0, 10.0),
            f_opt=0.0,
            x_opt_coord=1.0,
            formula=r"f(\mathbf{x}) = \sum_{i=1}^{d-1} \big[100\,(x_{i+1} - x_i^2)^2 + (x_i - 1)^2\big]",
            description="The global minimum sits in a long, narrow, curved valley. Finding "
            "the valley is easy; following it to (1, ..., 1) is hard.",
            page="rosen.html",
        ),
        BenchmarkFunction(
            key="six_hump_camel",
            name="Six-Hump Camel",
            category=VALLEY,
            func=six_hump_camel,
            domain=((-3.0, 3.0), (-2.0, 2.0)),
            dims=(2,),
            f_opt=-1.0316284534898774,
            x_opt_points=(
                (0.0898420118174292, -0.7126564056224669),
                (-0.0898420118174292, 0.7126564056224669),
            ),
            formula=r"f(\mathbf{x}) = \Big(4 - 2.1\,x_1^2 + \frac{x_1^4}{3}\Big)x_1^2 + x_1 x_2"
            r" + (-4 + 4\,x_2^2)\,x_2^2",
            description="Six local minima, two of which are global and symmetric. Tests "
            "whether the search can tell near-equal basins apart.",
            page="camel6.html",
        ),
        BenchmarkFunction(
            key="michalewicz",
            name="Michalewicz",
            category=STEEP,
            func=michalewicz,
            domain=(0.0, np.pi),
            dims=(2, 5, 10),
            f_opt={2: -1.8013034100985528, 5: -4.687658179088148, 10: -9.660151715641344},
            x_opt_points=tuple(MICHALEWICZ_X_OPT[:d] for d in (2, 5, 10)),
            formula=r"f(\mathbf{x}) = -\sum_{i=1}^{d} \sin(x_i)\,\sin^{2m}\!\Big(\frac{i\,x_i^2}{\pi}\Big),"
            r"\quad m = 10",
            description="d! local minima separated by flat plateaus with steep, narrow "
            "ridges (m = 10). The plateaus give no gradient information at all.",
            page="michal.html",
        ),
        BenchmarkFunction(
            key="easom",
            name="Easom",
            category=STEEP,
            func=easom,
            domain=(-100.0, 100.0),
            dims=(2,),
            f_opt=-1.0,
            x_opt_points=((np.pi, np.pi),),
            formula=r"f(\mathbf{x}) = -\cos(x_1)\cos(x_2)\exp\!\big(-(x_1-\pi)^2 - (x_2-\pi)^2\big)",
            description="Flat almost everywhere, with a single tiny well at (pi, pi) that "
            "covers a minute fraction of the domain: a needle in a haystack.",
            page="easom.html",
        ),
        BenchmarkFunction(
            key="rastrigin",
            name="Rastrigin",
            category=MANY_LOCAL_MINIMA,
            func=rastrigin,
            domain=(-5.12, 5.12),
            f_opt=0.0,
            x_opt_coord=0.0,
            formula=r"f(\mathbf{x}) = 10d + \sum_{i=1}^{d} \big[x_i^2 - 10\cos(2\pi x_i)\big]",
            description="A bowl covered in a regular egg-crate of local minima (about 10ᵈ "
            "of them). Local search alone gets trapped almost immediately.",
            page="rastr.html",
        ),
        BenchmarkFunction(
            key="ackley",
            name="Ackley",
            category=MANY_LOCAL_MINIMA,
            func=ackley,
            domain=(-32.768, 32.768),
            f_opt=0.0,
            x_opt_coord=0.0,
            formula=r"f(\mathbf{x}) = -20\exp\!\Big(-0.2\sqrt{\tfrac{1}{d}\textstyle\sum x_i^2}\Big)"
            r" - \exp\!\Big(\tfrac{1}{d}\textstyle\sum \cos(2\pi x_i)\Big) + 20 + e",
            description="A nearly flat outer region full of small ripples, with a deep hole "
            "in the centre. Hill climbers stall on the flat outer plateau.",
            page="ackley.html",
        ),
        BenchmarkFunction(
            key="griewank",
            name="Griewank",
            category=MANY_LOCAL_MINIMA,
            func=griewank,
            domain=(-600.0, 600.0),
            f_opt=0.0,
            x_opt_coord=0.0,
            formula=r"f(\mathbf{x}) = \sum_{i=1}^{d} \frac{x_i^2}{4000}"
            r" - \prod_{i=1}^{d} \cos\!\Big(\frac{x_i}{\sqrt{i}}\Big) + 1",
            description="Looks like a smooth bowl from far away, but zooming in reveals a "
            "dense grid of local minima. The product term couples the variables.",
            page="griewank.html",
        ),
        BenchmarkFunction(
            key="schwefel",
            name="Schwefel",
            category=MANY_LOCAL_MINIMA,
            func=schwefel,
            domain=(-500.0, 500.0),
            f_opt=0.0,
            x_opt_coord=420.96874369616904,
            formula=r"f(\mathbf{x}) = 418.9829\,d - \sum_{i=1}^{d} x_i \sin\!\big(\sqrt{|x_i|}\big)",
            description="Deceptive: the second-best minimum is far from the global one, "
            "near the opposite corner of the domain, so the search is pulled the wrong way.",
            page="schwef.html",
        ),
        BenchmarkFunction(
            key="eggholder",
            name="Eggholder",
            category=MANY_LOCAL_MINIMA,
            func=eggholder,
            domain=(-512.0, 512.0),
            dims=(2,),
            f_opt=-959.6406627208507,
            x_opt_points=((512.0, 404.2318049938646),),
            formula=r"f(\mathbf{x}) = -(x_2+47)\sin\!\sqrt{\big|x_2 + \tfrac{x_1}{2} + 47\big|}"
            r" - x_1\sin\!\sqrt{\big|x_1 - (x_2+47)\big|}",
            description="Highly irregular with many deep local minima, and the global "
            "minimum lies exactly on the domain boundary (x1 = 512).",
            page="egg.html",
        ),
        BenchmarkFunction(
            key="styblinski_tang",
            name="Styblinski-Tang",
            category=OTHER,
            func=styblinski_tang,
            domain=(-5.0, 5.0),
            f_opt=-39.16616570377141,
            f_opt_per_dim=True,
            x_opt_coord=-2.9035340314007785,
            formula=r"f(\mathbf{x}) = \frac{1}{2}\sum_{i=1}^{d} \big(x_i^4 - 16\,x_i^2 + 5\,x_i\big)",
            description="Separable with 2^d local minima. The global one is at x_i = -2.9035, "
            "slightly deeper than the mirror-image basin at x_i = +2.7468.",
            page="stybtang.html",
        ),
    ]
}


def get_function(key):
    """Look a benchmark up by its key, e.g. ``get_function("rastrigin")``."""
    try:
        return FUNCTIONS[key]
    except KeyError:
        raise KeyError(f"unknown benchmark {key!r}; choose from {sorted(FUNCTIONS)}") from None
