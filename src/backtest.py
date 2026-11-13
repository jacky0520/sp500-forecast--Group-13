"""
backtest.py - time-ordered evaluation at weekly forecast origins.

Each origin is a Thursday close, mirroring the real task (Thu 12 Nov close -> Fri 20 Nov
close, 6 trading days). Parameters are re-estimated at every origin from data available
at that origin only. Errors are scored with the coursework's own marking rule.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_data, add_factors, forecast_at, H

OUT = Path(__file__).resolve().parents[1] / "results"
OUT.mkdir(exist_ok=True)
START = "2008-01-01"


def score(ape_pct):
    """Coursework accuracy score: 50 - min(50, 0.5 * E / 0.1)."""
    return 50 - np.minimum(50, 5 * ape_pct)


def run(vol_lookback=252, rate_change=20, window=None, start=START, h=H):
    df = add_factors(load_data(), vol_lookback=vol_lookback, rate_change=rate_change, h=h)
    origins = df.index[(df["date"] >= start) & (df["date"].dt.weekday == 3)]
    origins = [t for t in origins if t + h < len(df)]
    rows, hist = [], []          # hist: (target index, squared errors of m1, m2, m3)
    for t in origins:
        known = [e for (tt, e) in hist if tt <= t]     # only errors realised by t
        f = forecast_at(df, t, h=h, window=window)
        g = forecast_at(df, t, h=h, window=window, weights="inv_mse", hist=known)
        realised = float(df["px"].iloc[t + h])
        y = np.log(realised / f["p0"])
        # Naive trend rules (benchmarks only): the last h-day log return repeats or reverses
        past = float(np.log(df["px"].iloc[t] / df["px"].iloc[t - h]))
        rec = {**f, "target_date": df["date"].iloc[t + h], "A": realised, "y": y,
               "r_inv": g["r_hat"], "w1_inv": g["w1"], "w2_inv": g["w2"], "w3_inv": g["w3"],
               "mom": past, "rev": -past}
        rows.append(rec)
        hist.append((t + h, np.array([(y - f["m1"]) ** 2, (y - f["m2"]) ** 2, (y - f["m3"]) ** 2])))
    return pd.DataFrame(rows)


MODELS = {  # name: (column with the forecast log return, role)
    "No change (benchmark)": (None, "Benchmark 1"),
    "M1 drift": ("m1", "Benchmark 2 and component"),
    "Momentum: last 6 days repeat": ("mom", "Naive rule"),
    "Reversal: last 6 days reverse": ("rev", "Naive rule"),
    "M2 VOL": ("m2", "Component"),
    "M3 RATE": ("m3", "Component"),
    "Combination, equal weights": ("r_hat", "Submitted model"),
    "Combination, inverse-MSE": ("r_inv", "Alternative, not submitted"),
}


def summarise(bt):
    out = []
    for name, (col, role) in MODELS.items():
        r = 0.0 if col is None else bt[col]
        F = bt["p0"] * np.exp(r)
        ape = 100 * (F - bt["A"]).abs() / bt["A"]
        sse = ((bt["y"] - r) ** 2).sum()
        out.append({"model": name, "role": role, "MAPE_pct": ape.mean(), "median_APE_pct": ape.median(),
                    "mean_score": score(ape).mean(),
                    "R2_oos_vs_no_change_pct": 100 * (1 - sse / (bt["y"] ** 2).sum()),
                    "R2_oos_vs_drift_pct": 100 * (1 - sse / ((bt["y"] - bt["m1"]) ** 2).sum())})
    return pd.DataFrame(out)


if __name__ == "__main__":
    bt = run()
    bt.to_csv(OUT / "backtest_origins.csv", index=False)
    s = summarise(bt)
    s.to_csv(OUT / "backtest_summary.csv", index=False)
    print(f"{len(bt)} origins, {bt['date'].min().date()} to {bt['date'].max().date()}")
    print(s.round(3).to_string(index=False))
