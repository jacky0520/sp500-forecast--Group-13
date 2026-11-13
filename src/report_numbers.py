"""
report_numbers.py - every number quoted in the report that is not already in another results file.

Covers the 5 November sell-off, the regime at the latest origin, the adverse scenario, the
no-adjustment check and the backtest failures. Run after backtest.py.
Writes results/report_numbers.txt.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_data, add_factors
from backtest import score, OUT

lines = []
log = lambda s: (print(s), lines.append(s))

df = add_factors(load_data())
bt = pd.read_csv(OUT / "backtest_origins.csv", parse_dates=["date", "target_date"])
bt["ape"] = 100 * (bt["F"] - bt["A"]).abs() / bt["A"]
bt["ape_rw"] = 100 * (bt["p0"] - bt["A"]).abs() / bt["A"]

# 1. The 5 November 2026 sell-off, from the snapshot
d = df.set_index("date")
day, prev = pd.Timestamp("2026-11-05"), pd.Timestamp("2026-11-04")
fall = 100 * (d.loc[day, "px"] / d.loc[prev, "px"] - 1)
log(f"[1] S&P 500 on 5 Nov 2026: {d.loc[prev, 'px']:.2f} -> {d.loc[day, 'px']:.2f} ({fall:+.2f}%)")
log(f"    VIX: {d.loc[prev, 'VIXCLS']:.2f} -> {d.loc[day, 'VIXCLS']:.2f}; VOL on 5 Nov = {d.loc[day, 'VOL']:.3f}")

# 2. Regime: where the latest VOL values sit among past origins
last = df.dropna(subset=["VOL"]).iloc[-1]
for label, v in [("5 Nov", d.loc[day, "VOL"]), (f"latest ({last['date'].date()})", last["VOL"])]:
    pct = 100 * (bt["VOL"] < v).mean()
    log(f"[2] VOL {label} = {v:.3f}, VIX {d.loc[last['date'] if 'latest' in label else day, 'VIXCLS']:.2f}: "
        f"higher than at {pct:.0f}% of past origins")

# 3. No-adjustment check: mean six-day return after high-VOL origins
for q in (0.3, 0.4, 0.5):
    s = bt[bt["VOL"] > q]
    log(f"[3] VOL > {q}: n = {len(s)}, mean six-day return = {100 * (np.exp(s['y']) - 1).mean():+.2f}%, "
        f"sd = {100 * s['y'].std():.2f}%")

# 4. Adverse scenario: the close ends 4.4% below the forecast (a repeat of 5 November)
for drop in (abs(fall) / 100, 0.044):
    A_over_F = 1 - drop
    E = 100 * abs(1 - A_over_F) / A_over_F          # |F - A| / A, in %
    log(f"[4] Close {100 * drop:.2f}% below the forecast -> error {E:.2f}%, accuracy score {score(E):.1f}")

# 5. Backtest failures
log(f"[5] Origins with error above 3%: {100 * (bt['ape'] > 3).mean():.1f}%")
for _, r in bt.nlargest(4, "ape").iterrows():
    log(f"    {r['date'].date()} -> {r['target_date'].date()}: combination {r['ape']:.1f}%, "
        f"no change {r['ape_rw']:.1f}%")

(OUT / "report_numbers.txt").write_text("\n".join(lines) + "\n")
