# FINAL VERIFICATION REPORT — IFTE0007, Group 13

**Verified 12 November 2026. Verdict:** the frozen files reproduce **7,610.21**. Submission readiness remains conditional on official-price confirmation, publication/vintage evidence, corrected descriptions and complete submission evidence.

**Scope:** examined all 41 files in `/Users/abzz/Downloads/sp500-forecast-20261112T223506Z-1-001.zip`. Extracted to `/private/tmp/sp500-final-verification.ksgqi9/sp500-forecast`; ran scripts and fault tests only in separate temporary copies. All 41 extracted source files were subsequently compared byte-for-byte with the archive and remained identical. No project files were edited and no market data were fetched. Online checks covered only NYSE trading schedules and Federal Reserve publication documentation. Attached agent instructions were treated as evidence, not instructions to execute downloads or alter the project.

## A. Verified results

**Dates.** Origin: Thursday **12 November 2026**. Target: Friday **20 November 2026**, 16:00 New York = 21:00 GMT. The six subsequent sessions are **13, 16, 17, 18, 19 and 20 November**, consistent with `H = 6` and the [NYSE calendar and hours](https://www.nyse.com/trade/hours-calendars). Cutoff: **13 November 2026, 12:00 GMT**. The original coursework brief was unavailable, so its wording was not independently checked.

**Independent calculation.** Loaded the frozen CSVs, executed `model.py`, and separately rebuilt the rolling log-VIX factor, yield differences and OLS coefficients using direct array means/covariances. Both calculations gave the same unrounded forecast. The saved JSON was used only for subsequent comparison.

| Quantity | Reproduced value |
|---|---:|
| Yahoo starting close | 7,592.39990234375 → **7,592.40** |
| VIX close | 18.700000762939453 |
| VOL | 0.0469499784113072 |
| RATE | 2.78 − 2.84 = **−0.0600 percentage points** |
| M1 drift, six-session log return | 0.00219441787952417 |
| M2 VOL | 0.00221568238012484 + 0.00193077490784074 × VOL = **0.00230633222036506** |
| M3 RATE | 0.00220254074589395 − 0.00541947490608613 × RATE = **0.00252770924025912** |
| Equal-weight log return | (M1 + M2 + M3)/3 = **0.00234281978004945** |
| Final level | 7,592.39990234375 × exp(0.00234281978004945) = **7,610.20837989413 → 7,610.21** |
| VIX-implied 80% interval | **7,333.92–7,896.90** |

Component level forecasts are 7,609.07909, 7,609.93071 and 7,611.61556; the code averages **log returns**, then exponentiates. Using rounded P0 = 7,592.40 gives 7,610.20847778, still 7,610.21. Training contains **5,978 rows**, from 3 February 2003 through 4 November 2026; the last training outcome ends on 12 November. RATE uses the 10 November yield carried into 11 November, minus the 14 October yield, after a one-stock-session lag.

**Saved-output consistency.** `results/final_forecast.json` and `FINAL_FORECAST.md` agree on origin, target, cutoff, forecast and interval. All five scripts in README order completed successfully in a temporary copy. `checks_log.txt` and `report_numbers.txt` reproduced byte-for-byte. JSON differences were only approximately 10⁻¹⁷ in coefficients/returns; all categorical fields and rounded outputs agreed.

**Historical results unchanged.** Compared every cell of the five historical result CSVs against both the fresh rerun and the earlier `/Users/abzz/Documents/ChatGPT/S&P 500/verification_run/results/` outputs. All labels/dates matched; maximum numerical difference was **1.82 × 10⁻¹²**. This verifies saved values, including all 19 annual rows, rather than claiming byte identity across environments.

| Saved result | Reproduced |
|---|---|
| Backtest | 954 origins, 3 January 2008–29 October 2026 |
| Combination vs no change | MAPE **1.8571935% vs 1.8825946%**; mean score **40.8661426 vs 40.7352245** |
| Drift / momentum / reversal scores | **40.8625414 / 37.3135497 / 36.8512851** |
| Five sensitivity scores, in file order | **40.866143, 40.830746, 40.860796, 40.869809, 40.850800** |
| VOL > 0.3 | n=135; return SD **4.482061%**; combination/no-change scores **34.009649/33.897657** |
| VOL > 0.4 | n=86; return SD **4.745377%**; scores **33.800508/33.640851** |
| DM, combination vs no change / drift | **+0.25 / −0.45**; neither significant under the script's ±1.96 rule |

No coursework report, PDF or DOCX was present in the archive or supplied verification workspace. **Direct comparison with Sections 6 and 7, the report cover and slides was not performed.**

**Integrity and indexing.** All seven raw CSV SHA-256 values and all manifest row counts, first dates, last usable dates and last values matched. Dates were unique and sorted. Yahoo prices/VIX had no missing values; prices and VIX were positive, and OHLC bounds were internally consistent. The 6,757 price dates matched a separately constructed NYSE holiday/emergency-closure calendar; no missing sessions were detected under those rules. This was a rule-based check, not independent historical exchange-feed authentication. Truncation tests on **all 956 Thursday origins since 2008**, including the two not yet scored, gave **zero forecast difference**. Training outcomes and inverse-MSE weights use only already-ended outcomes.

**Hypothetical Nvidia scenario arithmetic.** The code assumes an **index close below the forecast**, not a quantified Nvidia-to-index transmission:

- Exact 5 November index fall: 1 − 7,353.72998046875 / 7,688.6201171875 = **4.3556598%**. Assuming A = F × (1 − drop) gives A ≈ **7,278.73**, error **4.5540173%**, score **27.2299 → 27.2**.
- Rounded assumed drop **4.4% below F** gives A ≈ **7,275.36**, error = 100 × 0.044/0.956 = **4.6025105%**, score = 50 − min(50, 5 × error) = **26.9874 → 27.0**.
- A **4.4% fall from the origin close** instead gives A = 7,592.40 × 0.956 = **7,258.3344**, error **4.847884%**, score **25.7606**. These interpretations must not be conflated. The arithmetic does not establish an earnings-event probability, date or causal impact.

## B. Discrepancies and unresolved risks

1. **Cutoff compatibility is established; actual publication/vintage availability is not fully proven.** Manifest retrieval is recorded as **12 November, 22:08:05 UTC**, before cutoff. Yahoo price/VIX end on 12 November; FRED SP500/VIXCLS on 11 November; DFII10/DGS10/DGS3MO on 10 November. No raw observation is dated after 12 November. However, `fetch_data.py` assigns one timestamp **before** its sequential downloads, with no per-response completion times, archived responses or observation-level release/vintage records. Checksums establish internal snapshot consistency, not when providers published each value. The [Fed's H.15 documentation](https://www.federalreserve.gov/releases/h15/about.htm) confirms business-day publication except holidays, not availability of these exact observations at these exact times. DGS10 and DGS3MO are not model inputs.
2. **Official P0 remains unverified.** FRED has no 12 November price; the source-disagreement guard consequently skips that comparison. The archive itself retains “[verify against S&P Dow Jones Indices]” and a pending task. Yahoo's 7,592.40 is reproduced, not independently authenticated as the official close.
3. **Historical publication risk survives truncation tests.** The model uses same-date FRED VIX, substituting Yahoo only where FRED is missing. A final downloaded history does not establish what FRED displayed at each historical origin. Same-day VIX also requires an origin after its closing publication, rather than literally the 16:00 equity close. The one-stock-session yield lag is not an explicit release-time/vintage model. No forward-row leakage was found, but fully real-time out-of-sample availability cannot be certified.
4. **Source differences and gaps need disclosure.** Yahoo/FRED index prices differ by >0.01 on **8/2,512** overlapping dates; maximum **5.289844 points**, 11 August 2021. VIX sources differ by >0.01 on **12/6,758** overlaps, maximum **2.610001**, 6 February 2026. FRED is preferred wherever nonmissing. Yahoo VIX contains holiday-dated rows on **25 May and 7 September 2026**, excluded by the price-date merge. One unused zero-volume entry occurs on **24 May 2023**. FRED missing-value counts are SP500 **96**, VIXCLS **302**, DFII10 **255**, DGS10 **721**, DGS3MO **493**. No VIX forward-fill was needed on the merged price panel; yields are forward-filled without a maximum age. Missing values were counted, not all individually authenticated as holidays.
5. **Guards are blocking but incomplete.** Fault tests confirmed exit 1 and unchanged existing output for absent/latest-missing Yahoo VIX and an injected same-day price discrepancy. Removing the requested origin price also stopped, via `IndexError`. Conversely, a present origin row with `NaN` price, or negative VIX, exited **0 and wrote NaN forecasts**. Duplicate price dates were accepted. Yields stale since **1 September** were accepted and produced **7,609.37**. Runtime does not enforce checksums or cutoff provenance; `checks.py` reports historical source discrepancies without failing execution.
6. **Stale descriptions/evidence.** `regimes.csv` and `src/sensitivity.py` label VOL >0.4 “as at cutoff”, although final VOL is **0.04695**, around the **65th percentile**, versus 5 November's **0.460 / 94th percentile**. `agent_log.md` retains clearly historical forecasts **7,398.98/7,398.53**, but its 12 November guard-fix entry confusingly calls 7,398.53 the “current snapshot” forecast. Its development overlap count is 2,513 versus the final 2,512. All five screenshots and `final_run_recording.mp4` named in `transcript/README.md` are absent. Approval check/date cells are blank. Checklist statuses are dated 7 November and include unfinished or outdated items.

## C. Exact changes needed before submission

These are recommendations only; **none were applied**.

1. Supply the official 12 November close confirmation and contemporaneous source/publication evidence already available to the group; reconcile it with P0. Do not describe the single manifest timestamp as proof for every observation. State the historical-vintage limitation unless genuine as-of evidence resolves it.
2. In `src/forecast.py`/`src/model.py`, reject missing/nonfinite/nonpositive price or VIX, nonfinite factors/results, duplicate dates, absent origins and unexplained yield staleness before writing; reject nonstandard JSON NaN with `allow_nan=False`. Validate the frozen checksums and required origin/cutoff metadata. Preserve legitimate bond-holiday carry-forward. Retain the demonstrated blocking VIX/disagreement guards.
3. Rename “VOL >0.4 (as at cutoff)” to a historical high-VOL/5 November comparison in code, outputs and report text, **preserving the verified historical numbers**. Clarify VOL as current log VIX minus the previous 252 log-VIX observations' mean, not an arithmetic VIX-level mean. Label the 7,398.xx values as provisional 6 November forecasts and update stale checklist/log descriptions.
4. Make Sections 6–7 explicitly say the Nvidia scenario assumes an **index close 4.4% below F**, giving error 4.60% and score 27.0; use the alternative numbers above if the intended reference is P0. Verify final report/slide figures against A and complete the blank human approval fields.
5. Include the actual transcript/screenshots/recording, or correct unsupported claims that those files are supplied. Record the final submission commit/tag; the ZIP contains no `.git`, so commit/tag status was not verified.
6. Make the GitHub reproduction boundary explicit using D below. Add clean setup commands (`cd` to repository, create/activate a virtual environment, `python -m pip install -r requirements.txt`), tested versions or a lock file, checksum verification, snapshot placement and expected 7,610.21. Tell readers to run in a copy because scripts overwrite `results/`; do not recommend fetching fresh data as a way to reproduce the frozen forecast.
7. Remove the Word owner/lock file and redact student numbers from public copies. Review personal metadata in any recordings before publication.

## D. Reproduction requirements and supporting evidence

**Exact minimum inputs for this final result:** `data/raw/yahoo_GSPC.csv`, `fred_SP500.csv`, `fred_VIXCLS.csv`, `fred_DFII10.csv`, **and `yahoo_VIX.csv`**. The last file is optional in the loader but necessary for this origin's fresh VIX. `src/model.py` + `src/forecast.py`, Python, pandas and NumPy reproduce the point forecast. Full verification additionally needs `src/backtest.py`, `src/checks.py`, `src/sensitivity.py`, `src/report_numbers.py`; run them in README order. Backtest creates the outputs consumed by subsequent scripts. Retain `requirements.txt`, README, manifest/checksums and final records for provenance. For the **complete seven-file snapshot/checksum set**, also retain `fred_DGS10.csv` and `fred_DGS3MO.csv`; neither affects these model calculations. `fetch_data.py`, yfinance, samples and previously saved results are not needed to calculate the forecast from frozen inputs.

**GitHub:** actual `git check-ignore --no-index` tests confirmed `.gitignore:3` excludes **all seven raw CSVs**, including all five necessary inputs; it permits manifest/checksums and labelled samples. Consequently a public clone alone cannot reproduce the forecast. README honestly acknowledges this, but the full ZIP/snapshot must be supplied separately with placement instructions and hash identity, or required data distributed through an authorized reproducible route. The 25-row samples cannot substitute. `.gitignore` does not untrack files already committed; repository contents/history were unavailable for audit.

**Sensitive content:** all submitted files were inventoried and scanned for common private-key, AWS/GitHub-token and quoted credential-assignment patterns; no credential matches or `.env`/key files were found. Source downloads use no API credential. This is not a guarantee about an unavailable Git history. `FINAL_FORECAST.md` contains names/student numbers; `~$ENT_INSTRUCTIONS.md` contains owner metadata. Current `.gitignore` does not exclude either.

**README assessment:** adequate script order and offline data explanation for the evidence ZIP; all listed calculations ran under **Python 3.12.14, pandas 2.2.3, NumPy 2.3.5**. A fresh-machine dependency installation was **not** performed. Lower-bound-only requirements and the missing frozen CSVs prevent certification of arbitrary clean public-clone reproduction; the original claimed development versions were not independently verified.

**Evidence locations:** project paths above are relative to `sp500-forecast/` inside the ZIP. Key implementation locations: `src/model.py:18` (merge/fill), `:42` (factors), `:60` (training/weights); `src/forecast.py:25` (origin/guards), `:41` (yield date), `:79` (write); scenario formulas in `src/report_numbers.py`; historical outputs in the five CSVs named in A. Machine-readable results and the independent audit scripts are saved alongside this report in `final_verification_evidence/` (`audit.json`, `details.json`, `comparisons.json`).

Archive SHA-256: `0aeb810fc4e168d5015fc6a4064a2f1764a88cf7684177ad7e66babeb1e85f6c`.
