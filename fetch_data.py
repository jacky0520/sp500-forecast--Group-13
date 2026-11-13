"""
fetch_data.py  -  Download and freeze the raw data snapshot for the S&P 500 forecast.

Run on your own computer (Anaconda is fine):
    pip install yfinance pandas
    python fetch_data.py

Creates data/raw/ with one CSV per series plus data/raw/manifest.json, which records
source URL, retrieval time (UTC) and last usable observation for every series.
Run it again just before the information cutoff (Fri 13 Nov 2026, 12:00 London)
and then never touch data/raw/ again: that is the frozen snapshot.
"""
import json
import datetime as dt
from pathlib import Path

import pandas as pd

OUT = Path(__file__).parent / "data" / "raw"
OUT.mkdir(parents=True, exist_ok=True)

# FRED series (free CSV endpoint, no API key). All daily.
FRED = {
    "SP500":  "S&P 500 price index close (source: S&P Dow Jones Indices via FRED)",
    "VIXCLS": "CBOE VIX close",
    "DGS10":  "10-year Treasury constant-maturity yield, %",
    "DGS3MO": "3-month Treasury constant-maturity yield, %",
    "DFII10": "10-year TIPS real yield, %",
}
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"

# When each value becomes public (recorded in the manifest for publication-time discipline)
PUBLICATION = {
    "SP500":  "Official close at 16:00 New York on day t (S&P Dow Jones Indices); appears on FRED about one business day later",
    "VIXCLS": "Cboe VIX disseminated until 16:15 New York on day t; appears on FRED about one business day later",
    "DGS10":  "Federal Reserve H.15 value for day t; appears on FRED about one business day later",
    "DGS3MO": "Federal Reserve H.15 value for day t; appears on FRED about one business day later",
    "DFII10": "Federal Reserve H.15 value for day t; appears on FRED about one business day later",
}

manifest = {"retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "series": {}}

for sid, desc in FRED.items():
    url = FRED_URL.format(sid)
    df = pd.read_csv(url)
    df.columns = ["date", sid]
    df[sid] = pd.to_numeric(df[sid], errors="coerce")   # FRED uses "." for missing
    df.to_csv(OUT / f"fred_{sid}.csv", index=False)
    last = df.dropna().iloc[-1]
    manifest["series"][sid] = {"description": desc, "url": url, "publication": PUBLICATION[sid],
                               "rows": len(df),
                               "first_date": df["date"].iloc[0],
                               "last_usable_date": last["date"], "last_value": float(last[sid])}
    print(f"{sid:7s} last usable {last['date']}  value {last[sid]}")

# Working index series (Yahoo Finance ^GSPC): history from 2000 and the same-day latest close.
# FRED SP500 (official S&P DJI data) starts Nov 2016 and lags a day, so it is used as the check.
try:
    import yfinance as yf
    y = yf.download("^GSPC", start="2000-01-01", auto_adjust=False, progress=False)
    if isinstance(y.columns, pd.MultiIndex):
        y.columns = y.columns.get_level_values(0)
    y = y.reset_index()[["Date", "Open", "High", "Low", "Close", "Volume"]]
    y.columns = ["date", "open", "high", "low", "close", "volume"]
    y["date"] = pd.to_datetime(y["date"]).dt.strftime("%Y-%m-%d")
    y.to_csv(OUT / "yahoo_GSPC.csv", index=False)
    manifest["series"]["GSPC_yahoo"] = {
        "description": "S&P 500 OHLC from Yahoo Finance (working series; checked against FRED SP500)",
        "url": "https://finance.yahoo.com/quote/%5EGSPC/history",
        "publication": "Same evening as the 16:00 New York close", "rows": len(y),
        "first_date": y["date"].iloc[0], "last_usable_date": y["date"].iloc[-1],
        "last_value": float(y["close"].iloc[-1])}
    print(f"Yahoo   last usable {y['date'].iloc[-1]}  value {y['close'].iloc[-1]:.2f}")

    # VIX from Yahoo: FRED posts VIXCLS with a one-day delay, so the latest close
    # is taken from here when FRED does not have it yet.
    v = yf.download("^VIX", start="2000-01-01", auto_adjust=False, progress=False)
    if isinstance(v.columns, pd.MultiIndex):
        v.columns = v.columns.get_level_values(0)
    v = v.reset_index()[["Date", "Close"]]
    v.columns = ["date", "vix_close"]
    v["date"] = pd.to_datetime(v["date"]).dt.strftime("%Y-%m-%d")
    v.to_csv(OUT / "yahoo_VIX.csv", index=False)
    manifest["series"]["VIX_yahoo"] = {
        "description": "Cboe VIX close from Yahoo Finance (fills FRED's one-day lag)",
        "url": "https://finance.yahoo.com/quote/%5EVIX/history",
        "publication": "Same evening as the 16:15 New York VIX close", "rows": len(v),
        "first_date": v["date"].iloc[0], "last_usable_date": v["date"].iloc[-1],
        "last_value": float(v["vix_close"].iloc[-1])}
    print(f"VIX(Y)  last usable {v['date'].iloc[-1]}  value {v['vix_close'].iloc[-1]:.2f}")
except Exception as e:  # cross-check is optional
    print("Yahoo download skipped:", e)

with open(OUT / "manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)
print("\nSaved to", OUT.resolve())

# SHA-256 checksums: lets a marker confirm the ZIP files are the frozen snapshot
import hashlib
sums = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob("*.csv"))}
(OUT / "SHA256SUMS.txt").write_text("".join(f"{h}  {n}\n" for n, h in sums.items()))

# Labelled samples for the public repository (full vendor files are in the ZIP only)
SAMPLE = OUT.parent / "sample"
SAMPLE.mkdir(exist_ok=True)
for p in sorted(OUT.glob("*.csv")):
    d = pd.read_csv(p)
    pd.concat([d.head(5), d.tail(20)]).to_csv(SAMPLE / f"SAMPLE_{p.name}", index=False)
(SAMPLE / "README.md").write_text(
    "# SAMPLE FILES - NOT THE MODEL INPUTS\n\n"
    "Each `SAMPLE_*.csv` holds only the **first 5 rows and the last 20 rows** of the matching file in `data/raw/`.\n"
    "The rows in between are left out on purpose, so the dates jump (for example from January 2000 to the latest month).\n\n"
    "Why: S&P 500 and Yahoo Finance data may not be redistributed freely, so the public repository shows the\n"
    "format only. These samples **cannot reproduce the results**.\n\n"
    "The full frozen snapshot is in `data/raw/` inside the submitted evidence ZIP. `data/raw/SHA256SUMS.txt`\n"
    "lets anyone confirm that those files are the ones used.\n")
print("Checksums and labelled samples written")
