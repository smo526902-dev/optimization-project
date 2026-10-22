# Ablation studies

Each study changes one design choice and keeps every other setting at its default. The first row of each table is the default configuration. Each cell: median final error (success rate). ▲ / ▼: significantly better / worse than the default (Wilcoxon rank-sum, alpha = 0.05).

## local search

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| Hooke-Jeeves (default) | 3.98e+00 (0%) | 1.76e-02 (0%) | 1.23e-08 (100%) | 4.93e-02 (0%) | 4.74e+02 (0%) |
| hill climbing | 2.03e+01 (0%) ▼ | 7.57e+00 (0%) ▼ | 1.16e+00 (33%) ▼ | 2.73e-01 (0%) | 6.91e+02 (0%) |

## learning

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| Lamarckian (default) | 3.98e+00 (0%) | 1.76e-02 (0%) | 1.23e-08 (100%) | 4.93e-02 (0%) | 4.74e+02 (0%) |
| Baldwinian | 1.56e+01 (0%) ▼ | 6.89e+01 (0%) ▼ | 3.37e+00 (0%) ▼ | 1.17e+00 (0%) ▼ | 8.12e+02 (0%) |

## ls rate

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| 0.05 (default) | 3.98e+00 (0%) | 1.76e-02 (0%) | 1.23e-08 (100%) | 4.93e-02 (0%) | 4.74e+02 (0%) |
| 0.0 | 9.97e-01 (33%) ▲ | 2.42e-04 (0%) ▲ | 1.15e-08 (100%) | 3.49e-02 (0%) | 4.74e+02 (0%) |
| 0.02 | 2.98e+00 (0%) | 3.10e-03 (0%) | 1.23e-08 (100%) | 2.96e-02 (0%) | 6.51e+02 (0%) ▼ |
| 0.1 | 2.98e+00 (0%) ▲ | 1.57e-01 (0%) | 1.23e-08 (100%) | 5.91e-02 (0%) | 2.37e+02 (0%) |
| 0.2 | 3.98e+00 (0%) | 4.82e-01 (0%) | 1.15e-07 (100%) ▼ | 5.91e-02 (0%) | 2.37e+02 (0%) ▲ |

## selection

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| tournament (default) | 4.40e+00 (0%) | 1.08e+01 (0%) | 8.27e-01 (0%) | 2.53e-01 (0%) | 5.97e+02 (0%) |
| roulette | 1.32e+01 (0%) ▼ | 1.40e+02 (0%) ▼ | 2.71e+00 (0%) ▼ | 9.78e-01 (0%) ▼ | 7.20e+02 (0%) |
| rank | 1.47e+01 (0%) ▼ | 2.37e+01 (0%) | 3.49e+00 (0%) ▼ | 1.09e+00 (0%) ▼ | 6.09e+02 (0%) |

## crossover

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| sbx (default) | 4.40e+00 (0%) | 1.08e+01 (0%) | 8.27e-01 (0%) | 2.53e-01 (0%) | 5.97e+02 (0%) |
| blx | 6.78e+00 (0%) ▼ | 7.48e+00 (0%) | 5.09e-01 (0%) | 5.64e-01 (0%) ▼ | 4.76e+02 (0%) |
| arithmetic | 3.57e+00 (0%) | 9.03e+00 (0%) | 1.02e-01 (0%) ▲ | 5.01e-01 (0%) ▼ | 7.21e+02 (0%) |

## mutation

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| GA polynomial (default) | 4.40e+00 (0%) | 1.08e+01 (0%) | 8.27e-01 (0%) | 2.53e-01 (0%) | 5.97e+02 (0%) |
| GA gaussian | 2.81e+00 (0%) | 9.09e+00 (0%) | 9.89e-01 (0%) | 5.64e-01 (0%) ▼ | 3.63e+02 (0%) |
| GA uniform | 3.35e+00 (0%) | 2.57e+01 (0%) ▼ | 3.22e+00 (0%) ▼ | 8.92e-01 (0%) ▼ | 3.26e+01 (0%) ▲ |
| MA polynomial | 3.98e+00 (0%) | 1.76e-02 (0%) ▲ | 1.23e-08 (100%) ▲ | 4.93e-02 (0%) ▲ | 4.74e+02 (0%) ▲ |
| MA gaussian | 1.99e+00 (33%) | 1.54e-02 (33%) ▲ | 1.52e-08 (100%) ▲ | 1.11e-01 (0%) ▲ | 1.18e+02 (33%) ▲ |
| MA uniform | 2.84e-14 (100%) ▲ | 8.89e-03 (0%) ▲ | 1.36e-08 (100%) ▲ | 9.86e-03 (0%) ▲ | 1.18e+02 (33%) ▲ |

## pop size

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| 100 (default) | 4.40e+00 (0%) | 1.08e+01 (0%) | 8.27e-01 (0%) | 2.53e-01 (0%) | 5.97e+02 (0%) |
| 20 | 1.11e-02 (0%) ▲ | 6.94e+00 (0%) | 1.06e-02 (0%) ▲ | 5.13e-02 (0%) ▲ | 4.74e+02 (0%) ▲ |
| 50 | 2.38e-01 (0%) ▲ | 5.71e+00 (0%) | 6.41e-02 (0%) ▲ | 1.32e-01 (0%) ▲ | 3.55e+02 (0%) ▲ |
| 200 | 9.78e+00 (0%) ▼ | 5.49e+01 (0%) | 2.67e+00 (0%) ▼ | 1.12e+00 (0%) ▼ | 6.05e+02 (0%) |

## mutation rate

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| 1/d (default) | 4.40e+00 (0%) | 1.08e+01 (0%) | 8.27e-01 (0%) | 2.53e-01 (0%) | 5.97e+02 (0%) |
| 0.5/d | 3.04e+00 (0%) | 3.48e+01 (0%) | 4.76e-01 (0%) ▲ | 3.80e-01 (0%) | 5.94e+02 (0%) |
| 2/d | 8.26e+00 (0%) ▼ | 1.52e+01 (0%) ▼ | 1.94e+00 (0%) ▼ | 7.18e-01 (0%) ▼ | 4.87e+02 (0%) |
| 5/d | 1.75e+01 (0%) ▼ | 8.47e+01 (0%) ▼ | 4.61e+00 (0%) ▼ | 1.51e+00 (0%) ▼ | 7.39e+02 (0%) |
