# Pairwise comparisons (Wilcoxon rank-sum test, alpha = 0.05)

"+": the first algorithm has significantly lower final errors; "-": significantly higher; "=": no significant difference.

| Function | d | MA vs GA | GA vs RS | MA vs RS | MA vs DE |
|---|---|---|---|---|---|
| Sphere | 2 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | = (p = 1.0e+00) |
| Sphere | 10 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |
| Sphere | 30 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |
| Zakharov | 2 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | = (p = 1.0e+00) |
| Zakharov | 10 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |
| Zakharov | 30 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |
| Rosenbrock | 2 | = (p = 8.3e-01) | + (p = 5.0e-02) | = (p = 2.8e-01) | - (p = 5.0e-02) |
| Rosenbrock | 10 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |
| Rosenbrock | 30 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |
| Six-Hump Camel | 2 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | = (p = 1.0e+00) |
| Michalewicz | 2 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | = (p = 1.0e+00) |
| Michalewicz | 5 | = (p = 5.1e-01) | + (p = 5.0e-02) | + (p = 5.0e-02) | - (p = 5.0e-02) |
| Michalewicz | 10 | - (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |
| Easom | 2 | = (p = 3.8e-01) | = (p = 5.1e-01) | = (p = 5.1e-01) | = (p = 5.1e-01) |
| Rastrigin | 2 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | = (p = 1.9e-01) |
| Rastrigin | 10 | = (p = 5.1e-01) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |
| Rastrigin | 30 | = (p = 5.1e-01) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |
| Ackley | 2 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | = (p = 5.1e-01) |
| Ackley | 10 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |
| Ackley | 30 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |
| Griewank | 2 | = (p = 5.1e-01) | + (p = 5.0e-02) | + (p = 5.0e-02) | = (p = 5.1e-01) |
| Griewank | 10 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |
| Griewank | 30 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |
| Schwefel | 2 | = (p = 2.8e-01) | = (p = 5.1e-01) | = (p = 5.1e-01) | = (p = 1.9e-01) |
| Schwefel | 10 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |
| Schwefel | 30 | - (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |
| Eggholder | 2 | = (p = 5.1e-01) | = (p = 5.1e-01) | = (p = 5.1e-01) | = (p = 5.1e-01) |
| Styblinski-Tang | 2 | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) | = (p = 1.0e+00) |
| Styblinski-Tang | 10 | = (p = 2.8e-01) | + (p = 5.0e-02) | + (p = 5.0e-02) | = (p = 5.1e-01) |
| Styblinski-Tang | 30 | = (p = 8.3e-01) | + (p = 5.0e-02) | + (p = 5.0e-02) | + (p = 5.0e-02) |

## Totals (wins / ties / losses of the first algorithm)

| Comparison | per problem | after Holm correction |
|---|---|---|
| MA vs GA | 18 / 10 / 2 | 0 / 30 / 0 |
| GA vs RS | 27 / 3 / 0 | 0 / 30 / 0 |
| MA vs RS | 26 / 4 / 0 | 0 / 30 / 0 |
| MA vs DE | 16 / 12 / 2 | 0 / 30 / 0 |
