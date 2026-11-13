# Agent run log (decisions, tool calls, checks, corrections)

Times are London time and approximate (within about 5 minutes). Each entry: what the agent did, why, and the tool output it relied on.

## 2026-11-07 (development run on a provisional snapshot)

| Time | Step | Tool | Input -> output | Decision / reason |
|---|---|---|---|---|
| 13:57 | Read the coursework brief | file reader | brief .docx -> rules, scoring, dates | Horizon = 6 trading days (12 Nov close -> 20 Nov close); accuracy loses 0.5 marks per 0.1% error |
| 14:00 | Tried to download data inside the agent sandbox | bash `curl` | FRED, Yahoo, S&P DJI -> HTTP 403 (sandbox allowlist) | Data must be fetched on a group member's PC: wrote `fetch_data.py`, group ran it |
| 14:05 | Proposed model | reasoning | -> two factors (VIX, real yield) + drift, equal-weight combination | Single predictors fail out of sample (Goyal & Welch 2008); equal-weight combination is a shrinkage device (Rapach et al. 2010) |
| 15:31 | Group ran `fetch_data.py` | Python (group PC) | -> 7 files + manifest; FRED last date 2026-11-05, Yahoo 2026-11-06 | Noted FRED publishes one day late: the final baseline must come from a same-day source |
| 15:35 | Inspected snapshot | bash | -> S&P fell 4.4% on 5 Nov; VIX 16.6 -> 28.2 | Current regime is high-volatility; flagged for scenario analysis |
| 15:40 | Rolling-origin backtest | `src/backtest.py` | 954 Thursday origins 2008-2026 -> combination MAPE 1.857% vs no-change 1.883% | Gain is small; most of it comes from the drift component |
| 15:42 | **Check 1: source cross-check** | `src/checks.py` | Yahoo vs FRED on 2,513 days -> 8 days differ by > 0.01 pt (max 5.29 pt, 2021-08-11) | **Correction:** the final baseline P0 must be verified against the official S&P close, not taken from Yahoo alone |
| 15:42 | **Check 2: look-ahead test** | `src/checks.py` | 26 origins re-run on truncated data -> max difference 0.00 pt | PASS: no future data enters any forecast |
| 15:42 | Check 3: Diebold-Mariano | `src/checks.py` | DM = +0.25 (combination vs no-change) | Not significant: reported honestly |
| 15:45 | Context search | web search | NBC (5 Nov): AI-stock sell-off, worst day since Apr 2025; Nvidia IR: Q3 call 17 Nov 17:00 ET; BLS: Oct CPI on 10 Nov | Nvidia earnings fall inside the forecast window: main adverse scenario |
| 15:48 | **Correction 2: stale VIX** | `src/forecast.py` guard | Origin 6 Nov: VIX carried forward from 5 Nov -> WARNING | Added Yahoo ^VIX to `fetch_data.py` and a fill in `model.py`. (The guard at this point only printed a warning; it was made blocking on 12 Nov, see below.) |
| 15:50 | Sensitivity | `src/sensitivity.py` | 5 variants -> combination score 40.83-40.87 vs 40.74 | Result does not depend on window or lookback choices |
| 16:05 | Requirement audit (group prompt: "did you read the requirements carefully?") | reading the brief line by line | -> missing: publication times, observed/calculated/judgement split, labelled alternatives, version record, labelled samples | Added to report, `fetch_data.py` (publication field, SHA-256, samples), `final_forecast.json` layout and an internal requirements checklist |
| 21:10 | **Correction 3: data-source roles** (group member queried the data table) | code vs report | Report said FRED was the history source; the code uses Yahoo (FRED SP500 starts Nov 2016) | Text, README and manifest descriptions corrected to match the code; numbers unchanged |
| 21:15 | Full audit of every claim in the report | re-ran all scripts; checked each number and citation | Results reproduce exactly; fixed 3 citations (Bates & Granger, Bollerslev et al., Fed calendar), an unverified release time, NBC attribution, 'top 10%' -> 93rd percentile, training start date | Report corrected; AI-use declaration item (5) |
| 21:55 | Extra benchmarks (group prompt: "can we compare with anything else?") | `src/backtest.py`, `src/checks.py` | Drift 40.86, momentum 37.31, reversal 36.85 vs combination 40.87; DM combination vs drift -0.45 | Drift added as benchmark 2; the combination ties it, reported openly. Futures-implied price rejected: no free intraday history to backtest |
| 12:39 (8 Nov) | **Fix verified on new data** (group re-ran `fetch_data.py`) | manifest, SHA256SUMS, `src/forecast.py` | Yahoo VIX for 6 Nov = 25.64 (FRED still showed 5 Nov's 28.18); all 7 checksums OK; guard raised no warning; provisional forecast 7,398.53 (was 7,398.98 on the stale VIX); backtest numbers unchanged | Correction 2 confirmed working. Re-check of reported numbers found the third-worst miss misstated (13.9%, Nov 2008, not 12.4%, Apr 2025); report fixed |
| 10 Nov | **Independent re-run with Codex** (group member) | Codex on the shared folder | Reproduced all backtest and sensitivity results; flagged that the adverse-scenario figures could not be verified from the files | Added `src/report_numbers.py` for every quoted number. It corrected three report figures: 93% -> 94% (VOL rank), 14.5% -> 14.4% (Feb 2020 miss, changed by the Yahoo VIX fill), +0.2-0.6% -> +0.3-0.7% (simple, not log, mean returns) |
| 12 Nov | **Correction 4: guard made blocking** (from the group member's Codex check) | `src/forecast.py` | Codex found the input guard printed warnings but still wrote a forecast | Guard now stops the run (exit code 1, no forecast written). Tested on the 8 Nov development snapshot: it passes (provisional F = 7,398.53, unchanged); with the Yahoo VIX file removed, the run stops. The output now also shows which day's real yield RATE uses |

## Final run - Thursday 12 November 2026 (London time)

| Time | Step | Tool | Input -> output | Decision / reason |
|---|---|---|---|---|
| 22:08 | Final data snapshot (group) | `fetch_data.py`, group PC | 7 files, all SHA-256 checksums OK. Last usable: Yahoo S&P 500 and VIX 12 Nov; FRED SP500 and VIXCLS 11 Nov; DFII10 10 Nov | All inputs published before the 13 Nov 12:00 cutoff |
| ~22:15-22:26 | **Final agent run** in a new session started from `AGENT_INSTRUCTIONS.md`; screenshots of the saved session in `transcript/` | Python: backtest, checks, sensitivity, report_numbers, forecast | Backtest unchanged (954 origins; combination 40.87 vs no change 40.74); checks pass; guard passed; **F = 7,610.21** (P0 = 7,592.40, VIX 18.70, VOL 0.047, RATE -0.060 using DFII10 of 10 Nov); 80% interval 7,333.92-7,896.90 | Agent recommended the model output with no discretionary adjustment |
| 22:30 | Independent re-run (development session) | same code (hashes verified) on the same snapshot | `final_forecast.json`, `checks_log.txt`, `report_numbers.txt` byte-identical; hand recomputation gives 7,610.21 | Result confirmed |
| 00:09 (13 Nov) | **Baseline check** (group member) | S&P Dow Jones Indices website | Official close "as of Nov 12, 2026" = 7,592.40, identical to the baseline (difference 0.00 points); screenshot in `checks/sp500_official_close_12nov.png` | Baseline confirmed; forecast stays 7,610.21 |
| 13 Nov (morning) | **Response to the final Codex verification** (group) | `checks/FINAL_VERIFICATION_REPORT.md` (run by a group member on the 22:35 copy of the repository) | Codex reproduced 7,610.21 with its own OLS code and all backtest, sensitivity and regime numbers. Open points it raised: official P0 unverified; approval cells blank; transcript files missing; 'VOL > 0.4 (as at cutoff)' label out of date; guard does not reject NaN or negative inputs; historical data vintages cannot be proven | Resolved: P0 checked against S&P DJI (00:09 row above); approvals recorded in `FINAL_FORECAST.md`; screenshots added to `transcript/`. Not changed: code and outputs stay as in the final run, so the label is left as is (the report no longer describes the cutoff as high-volatility), and the extra guard cases do not occur in the final inputs (Codex found no missing, negative or duplicate values). Vintage limit stated in report Section 7.2 |

Still to do before submission (17:00, 13 Nov):
- [x] Group approves in `FINAL_FORECAST.md`
- [ ] Commit to GitHub
