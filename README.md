# S&P 500 forecast for 20 November 2026 - IFTE0007 Group 13

One point forecast of the official S&P 500 price-index close on Friday 20 November 2026
(16:00 New York), made with information available before Friday 13 November 2026, 12:00 London.

**Final forecast:** see `results/final_forecast.json` (the report cover holds the binding value).

## Method in one paragraph
The forecast is the 12 November close multiplied by exp(r̂), where r̂ is the equal-weight average of
three six-day return forecasts: the historical drift (M1), a one-factor regression on the VIX
relative to its one-year mean (M2, "VOL"), and a one-factor regression on the 20-day change in the
10-year real yield (M3, "RATE"). All coefficients are re-estimated by OLS at each origin using
only outcomes already known at that origin.

## Repository layout
| Path | Contents |
|---|---|
| `fetch_data.py` | Downloads and freezes the raw data (run once, before the cutoff) |
| `data/raw/` | Frozen snapshot + `manifest.json` (sources, retrieval time, last usable date) |
| `data/sample/` | Labelled sample rows of each raw file (public repository only; cannot reproduce results) |
| `src/model.py` | Factor definitions and the forecast function |
| `src/backtest.py` | Weekly rolling-origin backtest vs the no-change benchmark |
| `src/checks.py` | Source cross-check, look-ahead test, Diebold-Mariano test |
| `src/sensitivity.py` | Alternative windows, lookbacks, weights; results by year and regime |
| `src/forecast.py` | Final forecast with the full calculation and input guards |
| `src/report_numbers.py` | Every other number quoted in the report (5 Nov sell-off, regime, adverse scenario, failures) |
| `results/` | All outputs written by the scripts |
| `AGENT_INSTRUCTIONS.md` | Goal, boundary and tools given to the agent (pasted verbatim to start the final run) |
| `agent_log.md` | Agent decisions, tool calls, checks and corrections |
| `transcript/` | Screenshots of the final agent run |
| `checks/` | Independent checks: official S&P close for 12 Nov (screenshot); Codex re-run by a group member |
| `FINAL_FORECAST.md` | Final forecast record and group approval |

## Reproduce (no internet or AI account needed)
```bash
pip install -r requirements.txt
python src/backtest.py      # -> results/backtest_origins.csv, backtest_summary.csv
python src/checks.py        # -> results/checks_log.txt
python src/sensitivity.py   # -> results/sensitivity.csv, score_by_year.csv, regimes.csv
python src/report_numbers.py  # -> results/report_numbers.txt
python src/forecast.py --origin 2026-11-12   # -> results/final_forecast.json
```
`fetch_data.py` is only needed to rebuild the snapshot; the frozen files in `data/raw/` are the inputs.
From the public repository, first copy the seven CSV files from the evidence ZIP into `data/raw/` and check them
against `data/raw/SHA256SUMS.txt`. The scripts overwrite `results/`, so run them in a copy to compare with the saved
outputs. Expected result: 7,610.21.

## Software versions
Development run: Python 3.13.18, pandas 3.0.5, numpy 2.5.3 (agent sandbox, Linux).
Data download: Windows PC (PyCharm), Python 3.11.4, pandas 2.2.3, numpy 2.2.5, yfinance 1.8.0.

## Data files: ZIP vs public repository
- **Evidence ZIP (for the marker):** full frozen snapshot in `data/raw/`, which is enough to reproduce every number.
- **Public GitHub repository:** S&P 500 and Yahoo data may not be redistributed freely, so the full CSV files
  are excluded (`.gitignore`). `data/sample/SAMPLE_*.csv` are **labelled samples** (first 5 and last 20 rows)
  that show the format only and **cannot reproduce the results**. `data/raw/SHA256SUMS.txt` lets anyone check that the
  ZIP files are the same frozen snapshot.

## Data sources and terms
S&P 500 working series: Yahoo Finance ^GSPC (history from 2000 and the same-day latest close), checked
against the official S&P Dow Jones Indices close from FRED (SP500, available from November 2016).
VIX: FRED VIXCLS, with the latest day from Yahoo ^VIX. Real yield: FRED DFII10 (Federal Reserve H.15). S&P 500 data are the property of
S&P Dow Jones Indices and are included for academic reproduction only.
