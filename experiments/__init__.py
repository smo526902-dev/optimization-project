"""Experiment scripts: run with ``python -m experiments.<name>``.

The algorithms only use element-wise numpy operations, never matrix algebra, so
each process is limited to one BLAS thread. Otherwise every parallel worker
reserves buffers for a full set of BLAS threads, which can exhaust memory on
Windows when many workers run at once. This runs before numpy is imported,
both in the main process and in every worker it spawns.
"""
import os

for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

# Parallel worker processes: leave a couple of cores free for the desktop.
WORKERS = max(1, min((os.cpu_count() or 2) - 2, 16))
