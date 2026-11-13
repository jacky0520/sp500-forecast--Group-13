"""
model.py - factor construction and the combination forecast.

Everything here is a pure function of the frozen files in data/raw/.
A forecast made at origin day t only uses rows dated <= t, and only trains on
(t', return t'->t'+H) pairs whose outcome is fully known by t (t' + H <= t).
"""
from pathlib import Path
import numpy as np
import pandas as pd

H = 6                 # trading days from the 12 Nov close to the 20 Nov close
VOL_LOOKBACK = 252    # days in the VIX baseline mean
RATE_CHANGE = 20      # days in the real-yield change
RAW = Path(__file__).resolve().parents[1] / "data" / "raw"


def load_data(raw_dir=RAW):
    """Daily panel on S&P 500 trading days: price, VIX, 10y real yield."""
    px = pd.read_csv(raw_dir / "yahoo_GSPC.csv", parse_dates=["date"])[["date", "close"]]
    fred_px = pd.read_csv(raw_dir / "fred_SP500.csv", parse_dates=["date"])
    vix = pd.read_csv(raw_dir / "fred_VIXCLS.csv", parse_dates=["date"])
    ry = pd.read_csv(raw_dir / "fred_DFII10.csv", parse_dates=["date"])

    df = px.rename(columns={"close": "px"}).merge(fred_px, on="date", how="left")
    df = df.merge(vix, on="date", how="left").merge(ry, on="date", how="left")
    df = df.sort_values("date").reset_index(drop=True)
    # FRED posts VIX one day late: fill its missing latest closes from Yahoo ^VIX
    yv = raw_dir / "yahoo_VIX.csv"
    if yv.exists():
        v = pd.read_csv(yv, parse_dates=["date"])
        df = df.merge(v, on="date", how="left")
        df["VIXCLS"] = df["VIXCLS"].fillna(df.pop("vix_close"))
    # Bond market closes on some stock-market days (e.g. Veterans Day): carry the last
    # published yield forward. VIX gaps are carried the same way. No back-filling.
    df["vix_fresh"] = df["VIXCLS"].notna()      # False = value carried forward
    df["VIXCLS"] = df["VIXCLS"].ffill()
    df["DFII10"] = df["DFII10"].ffill()
    return df


def add_factors(df, vol_lookback=VOL_LOOKBACK, rate_change=RATE_CHANGE, h=H):
    df = df.copy()
    lv = np.log(df["VIXCLS"])
    # VOL_t: today's log VIX relative to its mean over the previous `vol_lookback` days
    df["VOL"] = lv - lv.shift(1).rolling(vol_lookback).mean()
    # RATE_t: 20-day change in the real yield, lagged one day for H.15 publication
    df["RATE"] = df["DFII10"].shift(1) - df["DFII10"].shift(1 + rate_change)
    # Target: H-day log return from t to t+H (NaN for the last H rows)
    df["y"] = np.log(df["px"].shift(-h)) - np.log(df["px"])
    return df


def _ols(x, y):
    X = np.column_stack([np.ones_like(x), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta  # [intercept, slope]


def forecast_at(df, t, h=H, window=None, weights="equal", hist=None):
    """
    Forecast made at the close of row t.
    window : None = expanding; int = rolling number of training rows
    weights: "equal" or "inv_mse" (needs hist: past squared errors per component)
    Returns a dict with every intermediate number, so the calculation is inspectable.
    """
    train = df.iloc[: t - h + 1]            # rows t' with t' + h <= t: outcome known at t
    train = train.dropna(subset=["y", "VOL", "RATE"])
    if window is not None:
        train = train.iloc[-window:]
    row = df.iloc[t]

    m1 = train["y"].mean()
    a2, b2 = _ols(train["VOL"].values, train["y"].values)
    a3, b3 = _ols(train["RATE"].values, train["y"].values)
    m2 = a2 + b2 * row["VOL"]
    m3 = a3 + b3 * row["RATE"]
    comps = np.array([m1, m2, m3])

    if weights == "equal" or hist is None or len(hist) < 52:
        w = np.ones(3) / 3
    else:  # inverse mean squared error over past origins (only errors already realised)
        mse = np.asarray(hist)[-260:].mean(axis=0)
        w = (1 / mse) / (1 / mse).sum()

    r_hat = float(comps @ w)
    p0 = float(row["px"])
    return {"date": row["date"], "p0": p0, "VOL": row["VOL"], "RATE": row["RATE"],
            "m1": m1, "a2": a2, "b2": b2, "m2": m2, "a3": a3, "b3": b3, "m3": m3,
            "w1": w[0], "w2": w[1], "w3": w[2], "r_hat": r_hat,
            "F": p0 * np.exp(r_hat), "n_train": len(train)}
