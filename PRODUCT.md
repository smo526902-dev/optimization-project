# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Streamlit (Python), chosen by the team in the project plan, with Plotly for interactive charts. The app imports the project's own `evoopt` library; it runs locally from the project's `.venv` on the presenter's laptop.

## Users

- **Primary:** the examiners of the AI310/CS361 project discussion. They sit next to the presenter's laptop and may take the mouse to try their own settings, so every control must make sense without the team explaining it.
- **Also:** the six-person student team, who use it to demonstrate the project and to defend their design choices.

## Product Purpose

An interactive demonstrator for Project 27: a Genetic Algorithm (GA) and a Memetic Algorithm (MA = GA + local search) that search for the global minimum of 12 benchmark functions from the SFU Virtual Library. Success: in a few minutes, an examiner sees how each algorithm searches, why the MA beats the GA where it does, and that the claims rest on fair, reproducible experiments.

## Positioning

Every result shown comes from the team's own from-scratch implementation running live, under one evaluation budget enforced by a single counter (`Problem.evaluate`). The app can show exactly what a generic optimisation library cannot: the population moving over the real landscape generation by generation, and the local-search share of the budget.

## Operating Context

- Shown on a laptop screen at arm's length during a live discussion; no projector.
- Opens on a live single run: pick a function, watch the GA or MA population move over the 2-D landscape and converge.
- Other views: explore the 12 landscapes; race GA against MA over several seeds with a Wilcoxon verdict; browse the saved 30-run experiment tables and figures.
- Runs must finish in seconds so the conversation never waits on the app.

## Capabilities and Constraints

- Algorithms: GA (3 selection, 3 crossover, 3 mutation operators), MA (Hooke-Jeeves or hill climbing, Lamarckian or Baldwinian), plus random search and SciPy DE baselines.
- Budget: 10,000 x d function evaluations by default; local-search evaluations count against the same budget.
- Animation of the population is only meaningful in 2-D; higher dimensions show convergence only.
- Terminology to keep: function evaluations (FEs), error f - f*, success (error <= 1e-4), errors below 1e-8 count as 0 (CEC convention).

## Evidence on Hand

- Saved full experiment (30 seeds, 30 problems, 4 algorithms, 8 ablations): `experiments/results/full/tables/` and `report/figures/`.
- Headline results: MA beats GA on 17 of 30 problems and ties 13 with no losses; MA vs DE: 10 wins, 16 ties, 4 losses.
- No testimonials, users or external claims exist; none may be invented.

## Product Principles

1. Show the mechanism, not just the number: every result appears next to the search that produced it.
2. Honest by default: ties, losses and failures are shown as plainly as wins.
3. Fair comparison is visible: equal budgets and seeds are stated wherever two algorithms meet.
4. Clear without a narrator: labels, units and defaults explain themselves to an examiner trying it alone.
5. Fast enough for conversation: defaults run in seconds.
