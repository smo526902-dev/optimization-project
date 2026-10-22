# Pairwise comparisons (Wilcoxon rank-sum test, alpha = 0.05)

"+": the first algorithm has significantly lower final errors; "-": significantly higher; "=": no significant difference. Following the CEC convention, errors below 1e-08 count as 0 before testing.

| Function | d | MA vs GA | GA vs RS | MA vs RS | MA vs DE |
|---|---|---|---|---|---|
| Sphere | 2 | = (p = 1.0e+00) | + (p = 2.9e-11) | + (p = 2.9e-11) | = (p = 1.0e+00) |
| Sphere | 10 | = (p = 1.0e+00) | + (p = 2.9e-11) | + (p = 2.9e-11) | = (p = 1.0e+00) |
| Sphere | 30 | = (p = 1.0e+00) | + (p = 2.9e-11) | + (p = 2.9e-11) | = (p = 1.0e+00) |
| Zakharov | 2 | = (p = 1.0e+00) | + (p = 2.9e-11) | + (p = 2.9e-11) | = (p = 1.0e+00) |
| Zakharov | 10 | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 2.9e-11) | = (p = 1.0e+00) |
| Zakharov | 30 | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 2.9e-11) |
| Rosenbrock | 2 | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 2.9e-11) | = (p = 1.0e+00) |
| Rosenbrock | 10 | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 2.9e-11) | = (p = 7.0e-01) |
| Rosenbrock | 30 | + (p = 1.4e-10) | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 2.9e-11) |
| Six-Hump Camel | 2 | = (p = 1.0e+00) | + (p = 2.9e-11) | + (p = 2.9e-11) | = (p = 1.0e+00) |
| Michalewicz | 2 | = (p = 1.0e+00) | + (p = 2.9e-11) | + (p = 2.9e-11) | = (p = 1.0e+00) |
| Michalewicz | 5 | = (p = 5.3e-01) | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 1.4e-02) |
| Michalewicz | 10 | = (p = 3.8e-01) | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 1.3e-06) |
| Easom | 2 | + (p = 2.7e-02) | + (p = 2.9e-11) | + (p = 2.9e-11) | = (p = 7.6e-02) |
| Rastrigin | 2 | = (p = 2.7e-01) | + (p = 2.9e-11) | + (p = 2.9e-11) | = (p = 6.6e-01) |
| Rastrigin | 10 | = (p = 7.6e-02) | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 1.0e-07) |
| Rastrigin | 30 | + (p = 6.1e-06) | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 2.9e-11) |
| Ackley | 2 | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 2.9e-11) | - (p = 6.6e-05) |
| Ackley | 10 | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 2.9e-11) | = (p = 6.6e-01) |
| Ackley | 30 | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 2.9e-11) |
| Griewank | 2 | + (p = 3.3e-02) | + (p = 2.9e-11) | + (p = 2.9e-11) | = (p = 4.1e-01) |
| Griewank | 10 | + (p = 5.2e-03) | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 2.2e-03) |
| Griewank | 30 | + (p = 3.7e-06) | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 4.6e-02) |
| Schwefel | 2 | + (p = 4.5e-03) | = (p = 7.6e-02) | + (p = 1.1e-06) | = (p = 5.1e-01) |
| Schwefel | 10 | + (p = 1.8e-06) | + (p = 2.9e-11) | + (p = 2.9e-11) | - (p = 2.3e-10) |
| Schwefel | 30 | + (p = 7.3e-07) | + (p = 2.9e-11) | + (p = 2.9e-11) | + (p = 2.9e-11) |
| Eggholder | 2 | = (p = 2.7e-01) | = (p = 6.6e-01) | = (p = 1.8e-01) | = (p = 2.2e-01) |
| Styblinski-Tang | 2 | = (p = 9.5e-01) | + (p = 1.0e-07) | + (p = 1.0e-07) | = (p = 5.1e-01) |
| Styblinski-Tang | 10 | + (p = 3.3e-03) | + (p = 4.6e-07) | + (p = 9.4e-11) | - (p = 5.3e-10) |
| Styblinski-Tang | 30 | = (p = 5.8e-02) | + (p = 2.9e-11) | + (p = 2.9e-11) | - (p = 2.9e-11) |

## Totals (wins / ties / losses of the first algorithm)

| Comparison | per problem | after Holm correction |
|---|---|---|
| MA vs GA | 17 / 13 / 0 | 12 / 18 / 0 |
| GA vs RS | 28 / 2 / 0 | 28 / 2 / 0 |
| MA vs RS | 29 / 1 / 0 | 29 / 1 / 0 |
| MA vs DE | 10 / 16 / 4 | 8 / 18 / 4 |
