"""
sensitivity.py - how much do the results depend on the key assumptions?

Re-runs the full backtest under alternative settings and reports the same metrics,
plus results by sub-period and in high-volatility regimes like the one at the cutoff.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backtest import run, summarise, score, OUT

variants = {
    "Base: expanding window, 252-day VIX mean": {},
    "Rolling 5-year training window": {"window": 1260},
    "Rolling 10-year training window": {"window": 2520},
    "126-day VIX mean": {"vol_lookback": 126},
    "60-day real-yield change": {"rate_change": 60},
}
rows = []
for name, kw in variants.items():
    s = summarise(run(**kw)).set_index("model")
    rows.append({"variant": name,
                 "combo_MAPE": s.loc["Combination, equal weights", "MAPE_pct"],
                 "no_change_MAPE": s.loc["No change (benchmark)", "MAPE_pct"],
                 "combo_score": s.loc["Combination, equal weights", "mean_score"],
                 "no_change_score": s.loc["No change (benchmark)", "mean_score"],
                 "inv_mse_score": s.loc["Combination, inverse-MSE", "mean_score"]})
sens = pd.DataFrame(rows)
sens.to_csv(OUT / "sensitivity.csv", index=False)
print(sens.round(3).to_string(index=False))

# Sub-periods and regimes for the base model
bt = pd.read_csv(OUT / "backtest_origins.csv", parse_dates=["date"])
bt["ape_rw"] = 100 * (bt["p0"] - bt["A"]).abs() / bt["A"]
bt["ape_combo"] = 100 * (bt["F"] - bt["A"]).abs() / bt["A"]
bt["year"] = bt["date"].dt.year
by_year = bt.groupby("year").agg(n=("y", "size"),
                                 score_no_change=("ape_rw", lambda e: score(e).mean()),
                                 score_combo=("ape_combo", lambda e: score(e).mean()))
by_year["combo_minus_no_change"] = by_year["score_combo"] - by_year["score_no_change"]
by_year.to_csv(OUT / "score_by_year.csv")
print("\n", by_year.round(3).to_string())

regimes = []
for label, mask in [("All origins", bt["VOL"] > -9), ("VOL > 0.3", bt["VOL"] > 0.3),
                    ("VOL > 0.4 (as at cutoff)", bt["VOL"] > 0.4)]:
    s = bt[mask]
    regimes.append({"regime": label, "n": len(s), "sd_6d_return_pct": 100 * s["y"].std(),
                    "score_no_change": score(s["ape_rw"]).mean(),
                    "score_combo": score(s["ape_combo"]).mean()})
reg = pd.DataFrame(regimes)
reg.to_csv(OUT / "regimes.csv", index=False)
print("\n", reg.round(3).to_string(index=False))
