# Project 27: Function Optimisation with a Genetic Algorithm and a Memetic Algorithm

AI310 / CS361 Artificial Intelligence, Fall 2026.

A Genetic Algorithm (GA) and a Memetic Algorithm (MA, a GA plus local search) that
search for the global minimum of 12 benchmark functions from the
[SFU Virtual Library of Simulation Experiments](https://www.sfu.ca/~ssurjano/optimization.html).

## Benchmark functions

| Category | Functions |
|---|---|
| Bowl-shaped | Sphere |
| Plate-shaped | Zakharov |
| Valley-shaped | Rosenbrock, Six-Hump Camel (2-D) |
| Steep ridges / drops | Michalewicz (d = 2, 5, 10), Easom (2-D) |
| Many local minima | Rastrigin, Ackley, Griewank, Schwefel, Eggholder (2-D) |
| Other | Styblinski-Tang |

The scalable functions accept any dimension d >= 2. Every function's known global
minimum is stored to full precision and checked by the tests.

## Setup

```bash
python -m venv .venv
```

```bash
.venv\Scripts\python -m pip install -r requirements.txt
```

## Demo app

Start the app, then open http://localhost:8501 in a browser:

```bash
.venv\Scripts\streamlit run app.py
```

It has four pages:

- **Watch a run** (opens first): pick a function, a dimension and GA or MA. The population is drawn on the 2-D landscape; press *Play generations* to watch it converge. Above 2-D, each individual is drawn as one line across its coordinates.
- **Explore landscapes**: a 3-D surface and a contour map of each function, with its formula, domain and known optimum.
- **GA vs MA**: both algorithms on the same seeds and budget, with a Wilcoxon verdict and one tray per seed.
- **Saved results**: the tables and figures from the full 30-run experiment.

The app works offline: its fonts are served from `static/fonts/`.

## Usage

Run the tests:

```bash
.venv\Scripts\python -m pytest
```

Run the GA once on 10-D Rastrigin and watch it converge:

```bash
.venv\Scripts\python -m experiments.run_one --algo ga --func rastrigin --dim 10
```

Run it 10 times (seeds 1-10) with custom settings and save a convergence plot:

```bash
.venv\Scripts\python -m experiments.run_one --algo ga --func rosenbrock --dim 10 --runs 10 --set selection=rank mutation=gaussian --plot conv.png
```

Run the Memetic Algorithm the same way (it also reports how much of the budget local search used):

```bash
.venv\Scripts\python -m experiments.run_one --algo ma --func rosenbrock --dim 10 --runs 10
```

Compare GA and MA on every benchmark with a Wilcoxon rank-sum test:

```bash
.venv\Scripts\python -m experiments.head_to_head --runs 10
```

Re-run the pilot study that chose the MA's local-search defaults (tables go to `experiments/results/pilot/`):

```bash
.venv\Scripts\python -m experiments.pilot_ma --round 2
```

Render the landscape gallery into `report/figures/`:

```bash
.venv\Scripts\python -m experiments.gallery
```

## Layout

```
evoopt/          core library
  benchmarks.py  the 12 benchmark functions and their known optima
  problem.py     Problem: a function + dimension + evaluation budget
  operators.py   selection, crossover and mutation operators
  ga.py          GeneticAlgorithm and its GAConfig
  local_search.py  Hooke-Jeeves pattern search, stochastic hill climbing
  ma.py          MemeticAlgorithm (GA + local search) and its MAConfig
  results.py     RunResult, the record every run returns
  baselines.py   random search and SciPy Differential Evolution
experiments/     scripts that produce figures and results
app.py           Streamlit entry point
app_pages/       the app's four pages and ui.py, their shared look and helpers
static/fonts/    Archivo and JetBrains Mono (SIL Open Font License)
.streamlit/      the app's theme
tests/           pytest suite
report/          report draft and figures
```
