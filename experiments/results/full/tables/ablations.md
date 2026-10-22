# Ablation studies

Each study changes one design choice and keeps every other setting at its default. The first row of each table is the default configuration. Each cell: median final error (success rate). ▲ / ▼: significantly better / worse than the default (Wilcoxon rank-sum, alpha = 0.05). Following the CEC convention, errors below 1e-08 count as 0. In the mutation study the MA rows are also compared with the default GA (the first row).

## local search

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| Hooke-Jeeves (default) | 0 (100%) | 0 (100%) | 0 (100%) | 2.46e-02 (20%) | 2.37e+02 (3%) |
| hill climbing | 0 (97%) | 6.69e-02 (0%) ▼ | 2.06e-08 (100%) ▼ | 5.78e-02 (0%) ▼ | 4.74e+02 (0%) ▼ |

## learning

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| Lamarckian (default) | 0 (100%) | 0 (100%) | 0 (100%) | 2.46e-02 (20%) | 2.37e+02 (3%) |
| Baldwinian | 3.34e-02 (0%) ▼ | 6.51e+00 (0%) ▼ | 1.27e-01 (0%) ▼ | 1.28e-01 (0%) ▼ | 4.74e+02 (0%) ▼ |

## ls rate

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| 0.05 (default) | 0 (100%) | 0 (100%) | 0 (100%) | 2.46e-02 (20%) | 2.37e+02 (3%) |
| 0.0 | 0 (100%) | 0 (100%) | 0 (100%) | 3.57e-02 (17%) | 3.55e+02 (0%) ▼ |
| 0.02 | 0 (100%) | 0 (100%) | 0 (100%) | 2.46e-02 (20%) | 3.55e+02 (3%) |
| 0.1 | 0 (100%) | 0 (83%) | 0 (100%) | 3.08e-02 (20%) | 2.37e+02 (7%) |
| 0.2 | 0 (97%) | 4.58e-07 (67%) ▼ | 0 (100%) | 2.70e-02 (20%) | 1.18e+02 (13%) ▲ |

## selection

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| tournament (default) | 0 (100%) | 4.27e+00 (0%) | 2.72e-05 (97%) | 6.89e-02 (0%) | 4.74e+02 (0%) |
| roulette | 2.85e-04 (10%) ▼ | 3.88e+00 (0%) | 2.63e-03 (0%) ▼ | 1.41e-01 (0%) ▼ | 4.74e+02 (0%) |
| rank | 1.48e-03 (0%) ▼ | 5.32e+00 (0%) | 1.01e-02 (0%) ▼ | 1.33e-01 (0%) ▼ | 4.74e+02 (0%) |

## crossover

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| sbx (default) | 0 (100%) | 4.27e+00 (0%) | 2.72e-05 (97%) | 6.89e-02 (0%) | 4.74e+02 (0%) |
| blx | 3.69e-02 (0%) ▼ | 6.79e+00 (0%) ▼ | 6.89e-02 (0%) ▼ | 2.35e-01 (0%) ▼ | 4.74e+02 (0%) |
| arithmetic | 1.34e-04 (33%) ▼ | 5.46e-01 (0%) ▲ | 4.06e-03 (0%) ▼ | 7.23e-02 (0%) | 3.55e+02 (0%) |

## mutation

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| GA polynomial (default) | 0 (100%) | 4.27e+00 (0%) | 2.72e-05 (97%) | 6.89e-02 (0%) | 4.74e+02 (0%) |
| GA gaussian | 2.11e-08 (100%) ▼ | 4.81e+00 (0%) | 5.46e-05 (83%) ▼ | 7.14e-02 (3%) | 4.74e+02 (0%) |
| GA uniform | 3.18e-07 (100%) ▼ | 2.84e+00 (0%) | 2.21e-04 (17%) ▼ | 8.00e-02 (0%) ▼ | 1.18e-06 (100%) ▲ |
| MA polynomial | 0 (100%) | 0 (100%) ▲ | 0 (100%) ▲ | 2.46e-02 (20%) ▲ | 2.37e+02 (3%) ▲ |
| MA gaussian | 0 (100%) | 0 (100%) ▲ | 0 (100%) ▲ | 2.21e-02 (7%) ▲ | 2.37e+02 (10%) ▲ |
| MA uniform | 0 (100%) | 0 (97%) ▲ | 1.22e-08 (100%) ▲ | 3.95e-02 (13%) ▲ | 0 (100%) ▲ |

## pop size

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| 100 (default) | 0 (100%) | 4.27e+00 (0%) | 2.72e-05 (97%) | 6.89e-02 (0%) | 4.74e+02 (0%) |
| 20 | 0 (100%) | 2.13e+00 (0%) ▲ | 6.21e-07 (100%) ▲ | 4.06e-02 (7%) ▲ | 4.74e+02 (0%) |
| 50 | 0 (100%) | 3.37e+00 (0%) | 9.65e-07 (100%) ▲ | 4.67e-02 (0%) ▲ | 4.74e+02 (0%) |
| 200 | 1.92e-06 (100%) ▼ | 5.09e+00 (0%) | 4.48e-04 (0%) ▼ | 7.06e-02 (0%) | 4.74e+02 (0%) |

## mutation rate

| Setting | Rastrigin 10-D | Rosenbrock 10-D | Ackley 10-D | Griewank 10-D | Schwefel 10-D |
|---|---|---|---|---|---|
| 1/d (default) | 0 (100%) | 4.27e+00 (0%) | 2.72e-05 (97%) | 6.89e-02 (0%) | 4.74e+02 (0%) |
| 0.5/d | 0 (100%) | 2.34e+00 (0%) | 2.35e-05 (100%) | 6.03e-02 (0%) | 4.74e+02 (0%) |
| 2/d | 2.20e-03 (0%) ▼ | 4.44e+00 (0%) | 1.46e-02 (0%) ▼ | 1.11e-01 (0%) ▼ | 3.55e+02 (0%) |
| 5/d | 6.50e+00 (0%) ▼ | 1.16e+01 (0%) ▼ | 2.18e+00 (0%) ▼ | 1.02e+00 (0%) ▼ | 4.92e+02 (0%) |
