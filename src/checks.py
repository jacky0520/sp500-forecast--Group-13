"""
checks.py - independent checks on the data and the calculation.

1. Source cross-check: Yahoo ^GSPC close vs FRED SP500 (S&P Dow Jones Indices) close.
2. Look-ahead test: re-run sample origins on data physically truncated at the origin
   and confirm the forecast is identical to the full-sample backtest.
3. Forecast-accuracy test: Diebold-Mariano test of the combination vs no-change.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_data, add_factors, forecast_at, H

OUT = Path(__file__).resolve().parents[1] / "results"
OUT.mkdir(exist_ok=True)
lines = []
log = lambda s: (print(s), lines.append(s))

# 1. Source cross-check ------------------------------------------------------
raw = load_data()
both = raw.dropna(subset=["SP500"])
diff = (both["px"] - both["SP500"]).abs()
log(f"[1] Overlap {len(both)} days ({both['date'].min().date()} to {both['date'].max().date()})")
log(f"    max |Yahoo - FRED| = {diff.max():.4f} points; days with |diff| > 0.01: {(diff > 0.01).sum()}")
if (diff > 0.01).any():
    log(both.loc[diff > 0.01, ["date", "px", "SP500"]].to_string(index=False))

# 2. Look-ahead test ---------------------------------------------------------
full = add_factors(raw)
thursdays = full.index[(full["date"] >= "2008-01-01") & (full["date"].dt.weekday == 3)]
rng = np.random.default_rng(0)
sample = sorted(rng.choice(thursdays[:-2], size=25, replace=False).tolist()) + [len(full) - 1]
max_gap = 0.0
for t in sample:
    a = forecast_at(full, t)["F"]
    trunc = add_factors(raw.iloc[: t + 1].copy())   # rows after t do not exist
    b = forecast_at(trunc, t)["F"]
    max_gap = max(max_gap, abs(a - b))
log(f"[2] Look-ahead test on {len(sample)} origins: max forecast difference = {max_gap:.2e} points "
    f"-> {'PASS' if max_gap < 1e-6 else 'FAIL'}")

# 3. Diebold-Mariano (squared return errors, Newey-West variance, lag 1) -------
bt = pd.read_csv(OUT / "backtest_origins.csv")


def dm_stat(bench_err, model_err):
    d = bench_err ** 2 - model_err ** 2                 # > 0 means the model beats the benchmark
    n, dbar = len(d), d.mean()
    u = d - dbar
    var = (u @ u + 2 * (1 - 1 / 2) * (u[1:].values @ u[:-1].values)) / n
    return dbar / np.sqrt(var / n)


for name, col in [("Combination", "r_hat"), ("M1 drift", "m1"), ("M2 VOL", "m2"), ("M3 RATE", "m3")]:
    dm = dm_stat(bt["y"], bt["y"] - bt[col])
    log(f"[3] DM statistic, {name} vs no-change: {dm:+.2f} (|DM| > 1.96 = significant at 5%)")
dm = dm_stat(bt["y"] - bt["m1"], bt["y"] - bt["r_hat"])
log(f"[3] DM statistic, Combination vs drift (benchmark 2): {dm:+.2f}")

(OUT / "checks_log.txt").write_text("\n".join(lines) + "\n")
