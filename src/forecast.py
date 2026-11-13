"""
forecast.py - the final forecast from the frozen snapshot.

    python src/forecast.py                      # origin = last row in the snapshot
    python src/forecast.py --origin 2026-11-12  # explicit origin

Writes results/final_forecast.json and prints the full calculation.
If an input guard fails, it prints the reason and STOPS (exit code 1) without writing a forecast.
"""
import sys, json, argparse
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_data, add_factors, forecast_at, H, RAW

OUT = Path(__file__).resolve().parents[1] / "results"
OUT.mkdir(exist_ok=True)

ap = argparse.ArgumentParser()
ap.add_argument("--origin", default=None)
args = ap.parse_args()

df = add_factors(load_data())
t = len(df) - 1 if args.origin is None else int(df.index[df["date"] == args.origin][0])
row = df.iloc[t]

# Guards: the inputs at the origin must be observed that day, not carried forward
warnings = []
if not bool(row["vix_fresh"]):
    warnings.append("VIX at the origin is carried forward from an earlier day")
if not np.isnan(row["SP500"]) and abs(row["SP500"] - row["px"]) > 0.01:
    warnings.append(f"Yahoo close {row['px']:.2f} differs from FRED/S&P close {row['SP500']:.2f}")
if warnings:
    for w in warnings:
        print("STOPPED - input guard failed:", w)
    print("No forecast written. Fix the input (for example, re-run fetch_data.py) and run again.")
    sys.exit(1)

# Which day's real yield RATE actually uses (t-1, carried forward over bond holidays or publication lag)
ry = pd.read_csv(RAW / "fred_DFII10.csv", parse_dates=["date"]).dropna()
ry_date = ry.loc[ry["date"] <= df["date"].iloc[t - 1], "date"].max().date()

f = forecast_at(df, t)
vix = float(row["VIXCLS"])
sd = vix / 100 * np.sqrt(H / 252)                 # VIX-implied 6-day volatility
lo, hi = f["F"] * np.exp(-1.2816 * sd), f["F"] * np.exp(1.2816 * sd)

record = {
    "market": "S&P 500 price index", "unit": "index points",
    "target": "Official close, Friday 20 November 2026, 16:00 New York (21:00 UTC), S&P Dow Jones Indices",
    "information_cutoff": "Friday 13 November 2026, 12:00 London (12:00 UTC)",
    "origin_date": str(row["date"].date()), "horizon_trading_days": H,
    "observed": {
        "baseline_P0_close": round(f["p0"], 2),
        "VIX_close": vix,
        "DFII10_used_t_minus_1": float(df["DFII10"].iloc[t - 1]),
        "DFII10_observation_date": str(ry_date),
    },
    "calculated": {
        "VOL": float(f["VOL"]), "RATE": float(f["RATE"]),
        "M1_drift_6d_log_return": f["m1"],
        "M2_VOL": {"a2": f["a2"], "b2": f["b2"], "forecast": f["m2"]},
        "M3_RATE": {"a3": f["a3"], "b3": f["b3"], "forecast": f["m3"]},
        "combined_log_return": f["r_hat"], "training_rows": f["n_train"],
        "final_forecast": round(f["F"], 2),
    },
    "judgement": {
        "factors": "VOL (VIX vs 252-day mean) and RATE (20-day change in 10y real yield, lagged 1 day)",
        "weights": [f["w1"], f["w2"], f["w3"]],
        "training_window": "expanding, from 2003",
        "discretionary_adjustment_points": 0.0,
    },
    "final_forecast": round(f["F"], 2),
    "interval_80pct_vix_implied": [round(lo, 2), round(hi, 2)],
    "warnings": warnings,
}
(OUT / "final_forecast.json").write_text(json.dumps(record, indent=2, default=float))

print(f"Origin {record['origin_date']}  baseline P0 = {f['p0']:.2f}")
print(f"VOL = {f['VOL']:.4f}  RATE = {f['RATE']:.4f}  (VIX {vix:.2f}; real yield observed on {ry_date})")
print(f"M1 drift          = {100*f['m1']:+.3f}%")
print(f"M2 VOL : {f['a2']:+.5f} + {f['b2']:+.5f} x VOL  = {100*f['m2']:+.3f}%")
print(f"M3 RATE: {f['a3']:+.5f} + {f['b3']:+.5f} x RATE = {100*f['m3']:+.3f}%")
print(f"Combined (1/3 each) = {100*f['r_hat']:+.3f}%")
print(f"FINAL FORECAST F = {f['F']:.2f}   80% interval [{lo:.2f}, {hi:.2f}]")
