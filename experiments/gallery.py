"""Render every benchmark landscape in 2-D, as 3-D surfaces and as contour maps.

    python -m experiments.gallery

Writes report/figures/landscapes_3d.png and report/figures/landscapes_contour.png.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from evoopt import FUNCTIONS

OUT = Path(__file__).resolve().parent.parent / "report" / "figures"
METADATA = {"impeccable:prompt": "Drawn by experiments/gallery.py with matplotlib from evoopt.benchmarks; no image model involved.",
            "Source": "experiments/gallery.py"}

# Some landscapes are unreadable over the full search domain, so the figure
# shows a window around the optimum instead (the search still uses the full domain).
VIEW_WINDOW = {
    "rosenbrock": ((-2.0, 2.0), (-1.0, 3.0)),  # the curved valley
    "easom": ((-3.0, 9.0), (-3.0, 9.0)),  # the needle at (pi, pi)
    "griewank": ((-40.0, 40.0), (-40.0, 40.0)),  # the ripples hidden in the bowl
}


def grid(fn, resolution):
    if fn.key in VIEW_WINDOW:
        (x0, x1), (y0, y1) = VIEW_WINDOW[fn.key]
    else:
        lower, upper = fn.bounds(2)
        (x0, y0), (x1, y1) = lower, upper
    xs, ys = np.linspace(x0, x1, resolution), np.linspace(y0, y1, resolution)
    X1, X2 = np.meshgrid(xs, ys)
    Z = fn(np.column_stack([X1.ravel(), X2.ravel()])).reshape(X1.shape)
    return X1, X2, Z


def title(fn):
    zoom = "  (zoomed)" if fn.key in VIEW_WINDOW else ""
    return f"{fn.name}{zoom}\n{fn.category}"


def surfaces(path):
    fig = plt.figure(figsize=(16, 12))
    for k, fn in enumerate(FUNCTIONS.values(), start=1):
        ax = fig.add_subplot(3, 4, k, projection="3d")
        X1, X2, Z = grid(fn, 160)
        ax.plot_surface(X1, X2, Z, cmap="viridis", linewidth=0, antialiased=True, alpha=0.95)
        x_star = fn.x_star(2)
        ax.scatter(x_star[:, 0], x_star[:, 1], fn(x_star), color="red", s=30, depthshade=False)
        ax.set_title(title(fn), fontsize=10)
        ax.tick_params(labelsize=6)
    fig.suptitle("Benchmark landscapes in 2-D (red = global minimum)", fontsize=14)
    fig.tight_layout()
    fig.savefig(path, dpi=130, metadata=METADATA)
    plt.close(fig)


def contours(path):
    fig, axes = plt.subplots(3, 4, figsize=(16, 12))
    for ax, fn in zip(axes.ravel(), FUNCTIONS.values()):
        X1, X2, Z = grid(fn, 300)
        # Quantile levels spread the colours evenly, so both the deep basins and
        # the shallow ripples stay visible without a per-function log scale.
        levels = np.unique(np.quantile(Z, np.linspace(0, 1, 40)))
        ax.contourf(X1, X2, Z, levels=levels, cmap="viridis")
        x_star = fn.x_star(2)
        ax.plot(x_star[:, 0], x_star[:, 1], "r*", markersize=12, markeredgecolor="white")
        ax.set_title(title(fn), fontsize=10)
        ax.tick_params(labelsize=7)
        ax.set_aspect("auto")
    fig.suptitle("Benchmark landscapes in 2-D, contour view (red star = global minimum)", fontsize=14)
    fig.tight_layout()
    fig.savefig(path, dpi=130, metadata=METADATA)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    surfaces(OUT / "landscapes_3d.png")
    contours(OUT / "landscapes_contour.png")
    print(f"wrote {OUT / 'landscapes_3d.png'}")
    print(f"wrote {OUT / 'landscapes_contour.png'}")


if __name__ == "__main__":
    main()
