# Independent verification of Sections 6 and 7

10 November 2026. **The reported table values, regime scores, MAPE figures and scenario arithmetic reproduce. The principal correction is to distinguish the statistical test's squared-return loss from MAPE.** Some specifications and interpretations need qualification; no table score needs changing.

## Scope and read-only method

Reviewed the supplied `sp500-forecast_1110-20261110T131454Z-1-001.zip` and `IFTE0007, COURSEWORK PART 6&7.docx`, both in `/Users/abzz/Downloads/`. Document and project instructions were treated as evidence, not execution authority. No source, data, coursework or existing result was changed; no market data or external information was fetched. Attachment and extracted-project hashes are unchanged; all seven raw CSV checksums pass.

The archive was extracted to `/private/tmp/sp500_audit_1110/sp500-forecast_1110/` (called **P** below). Direct execution of `report_numbers.py` would overwrite `results/report_numbers.txt`; other script entry points also save results. Instead, its entire calculation body was evaluated in memory, omitting only the final write. Its stdout exactly matches the saved report. Backtest functions were loaded with directory creation omitted and called in memory for all five settings. All scores and MAPE values reproduce within floating-point precision; maximum origin-level numerical difference is 1.82e-12. An independent calculation also checked metrics and inverse-MSE weights. The original coursework scoring brief was not supplied, so the score formula is verified against the implementation, not independently against that brief.

## A. Verified claims

### Sensitivity table and specifications

All variants use the same **954 Thursday origins, 3 January 2008–29 October 2026**, forecasting six saved price sessions ahead. Forecasts use only training returns whose targets have ended by the origin.

| Coursework row | Recomputed mean score /50 | Verdict |
|---|---:|---|
| Baseline expanding, 252-day VIX reference | 40.866143 → **40.87** | Correct |
| Rolling five-year training window | 40.830746 → **40.83** | Correct; 1,260 usable training rows |
| Rolling ten-year training window | 40.860796 → **40.86** | Correct; 2,520 usable training rows |
| 126-day VIX reference | 40.869809 → **40.87** | Correct |
| 60-day real-yield change | 40.850800 → **40.85** | Correct |
| Inverse-MSE combination | 40.866064 → **40.87** | Correct; baseline components |
| No-change benchmark | 40.735225 → **40.74** | Correct; forecast equals origin price |

The baseline combines drift and two separate one-factor regressions with weights 1/3 each. VOL is `log(VIX_t) − mean(log(VIX) over the previous 252 price sessions)`: its reference is geometric in VIX levels and excludes today. RATE is `DFII10_(t−1) − DFII10_(t−21)`; the alternative changes the lookback to 60 sessions, retaining the lag. Rolling windows are maximum counts of usable rows, not exact calendar periods; fewer rows are used when insufficient history exists.

Inverse-MSE weights are proportional to `1 / mean(component squared log-return error)`, using at most 260 prior weekly errors whose targets have ended. Weights remain equal until 52 errors are available. Independent reconstruction matches saved weights within 5.56e-16. The model-specification score range is **0.039063**, supporting “0.04 marks” when the benchmark is excluded. The variants change one setting at a time.

Evidence: **P**`/src/model.py:42`, `:60`; `src/backtest.py:29`; `src/sensitivity.py`; `results/sensitivity.csv`; `results/backtest_origins.csv`.

### Volatility regimes

| Regime | Origins | Combination score | No-change score | SD of six-day log return |
|---|---:|---:|---:|---:|
| Overall | **954** | **40.866143 → 40.87** | 40.735225 | 2.651254% |
| VOL > 0.3 | **135** | **34.009649 → 34.01** | 33.897657 | 4.482061% |
| VOL > 0.4 | **86** | **33.800508 → 33.80** | 33.640851 | 4.745377% |

Both stress subsets have lower scores and greater realised dispersion. The combination's score advantages are small: **0.1120** and **0.1597** marks. The subsets overlap; these are descriptive conditional results, not independent experiments or calibrated future uncertainty estimates. VOL thresholds refer to the constructed log-relative factor, not VIX levels of 30 or 40.

Evidence: **P**`/results/regimes.csv`, independently recalculated from `results/backtest_origins.csv`.

### Historical error and significance

Combination MAPE is **1.857194%**, no-change **1.882595%**, and drift **1.858160%**. Thus the coursework's **1.857% versus 1.883%** is correct. The gain over no-change is **0.025401 percentage points** (about 1.35% relative); over drift it is only **0.000966 percentage points**. Drift scores **40.862541**, versus combination **40.866143**. Combination squared-return performance is worse than drift: out-of-sample R² **−0.144213%** against drift.

The implemented Diebold–Mariano test uses **squared log-return errors**, Newey–West lag 1 and an asymptotic ±1.96 threshold. Recomputed combination versus no-change statistic is **+0.24654** (normal two-sided p≈0.805); combination versus drift is **−0.45293** (p≈0.651). Neither is significant at 5%. This supports caution about added predictive value, but is not a significance test of MAPE itself.

Evidence: **P**`/src/checks.py`, `results/checks_log.txt`, `results/backtest_summary.csv`.

### Nvidia hypothetical scenario

For an assumed actual level `A = F(1−d)`, the implemented error is **`E = 100d/(1−d)`**, and score **`max(0,50−5E)`**. The denominator is the hypothetical actual level, not the forecast.

| Decline below forecast | APE | Score /50 |
|---|---:|---:|
| Exact saved 5 November decline: 4.3556598% | **4.554017%** | **27.229913** |
| Exactly 4.36% | **4.558762%** | **27.206190** |
| Coursework's rounded assumption: 4.4% | **4.602510%** | **26.987448** |

The document's “4.4% … approximately 4.6% … around 27/50” is internally correct and needs no numerical correction. The script's displayed **4.36% → 4.55%** uses the unrounded decline; treating 4.36% as exact would round the error to **4.56%**.

The 4.3556598% magnitude comes from the saved index closes on 4–5 November. Transferring that magnitude to a future level below the forecast is an **assumption**. The code contains no Nvidia-specific causal model, earnings surprise estimate, probability or index-weight calculation. Neither Nvidia attribution nor event timing was externally verified. The arithmetic is now reproducible; the economic shock remains hypothetical.

Evidence: **P**`/src/report_numbers.py:25`, `:45`; `results/report_numbers.txt`; `data/raw/yahoo_GSPC.csv`.

## B. Data-quality claims and remaining issues

- **Eight discrepancies: verified.** Across 2,513 Yahoo/FRED overlapping dates, eight absolute differences exceed 0.01 index point; maximum **5.289844 points**, 11 August 2021. Dates: 29 November 2018; 12 August 2019; 11 May, 2/5/6/7 October 2020; 11 August 2021. The model uses Yahoo throughout and does not reconcile these differences. This is eight threshold breaches, not necessarily eight cases of any numerical difference.
- **955 truncation checks: independently reverified**, maximum forecast difference **0.00 points**: 954 scored origins plus the 6 November development origin. The supplied `checks.py` itself tests only **26** origins. Passing proves invariance to removal of later-dated rows, not historical release-time availability or original data vintages.
- **Timing limitations: valid.** The manifest records retrieval on **8 November 2026, 12:39 UTC**, generic publication descriptions and later FRED availability; it lacks per-observation release timestamps/vintages. It describes the VIX close at 16:15 New York versus the index close at 16:00. A literal index-close information set therefore needs qualification. Yield lagging and forward-filling do not certify real-time availability.
- **Warning-only safeguards: verified.** `forecast.py` appends warnings and still calculates/writes output. The source-price warning is skipped when FRED's same-date price is missing, as at the development origin. Empty warnings do not certify official-source agreement. No hard final-origin/cutoff enforcement exists.
- **Outdated project labels remain.** The latest saved origin is 6 November, VOL **0.364120**, about the **90th** percentile; it is outside VOL > 0.4. The 5 November VOL is **0.460**, about the **94th** percentile. `regimes.csv`'s “VOL > 0.4 (as at cutoff)” label is stale. The saved forecast JSON combines a 6 November origin/six-session calculation with a hard-coded 20 November target; it is provisional, not a verified final forecast for that target. Neither issue invalidates the historical scores quoted in Sections 6–7.

Evidence: **P**`/results/checks_log.txt`, `src/checks.py`, `src/forecast.py:24`, `data/raw/manifest.json`, `results/final_forecast.json`; expanded check in the audit evidence below.

## C. Exact text or entries to change

1. **Section 7.1 — replace:** “Although this is an improvement, it was not statistically significant.”

   **With:** “The implemented Diebold–Mariano test finds no statistically significant improvement in squared log-return errors over no-change (DM = 0.25); it does not directly test the MAPE reduction.”

2. **Section 6.1 — clarify:** “As shown in Table 1, the model's average accuracy scores vary by only 0.04 marks across the tested specifications, suggesting that its historical performance is relatively insensitive to changes in the modelling assumptions.”

   **Use:** “Excluding the no-change benchmark, the tested model specifications span 0.039 marks, approximately 0.04, suggesting limited sensitivity of historical average scores to these individual changes.”

3. **Table labels — precision amendments:** “Rolling five-year training window” → “Rolling 1,260 usable training rows (approximately five years)”; “Rolling ten-year training window” → “Rolling 2,520 usable training rows (approximately ten years)”. Retain every score. Add: “VIX references use prior trading-session log values; the baseline real-yield change is 20 sessions, lagged one session.”

4. **Section 6.2 — replace the sample-size sentence** with: “Across 954 historical forecast origins, the combined model averages 40.87/50; this falls to 34.01 for VOL > 0.3 (135 origins) and 33.80 for VOL > 0.4 (86 origins).”

5. **Section 6.3 — qualify:** “This scenario highlights the model's vulnerability to unexpected company-specific shocks, particularly those affecting large technology firms with substantial index weightings.”

   **Use:** “This scenario illustrates the score loss conditional on an assumed adverse index outcome; it does not estimate the effect of Nvidia earnings or isolate company-specific exposure.” Retain the existing 4.4%, 4.6% and 27/50 figures.

6. **Section 7.2 — sharpen the source/truncation wording:** replace “eight differences across historical price sources” with “eight Yahoo/FRED close discrepancies exceeding 0.01 index point across 2,513 overlapping dates”. Replace “Although all 955 row-truncation checks passed” with “Although an independent extension covering 954 scored origins and one development origin passed all 955 row-truncation checks”. Its existing warning-only and publication-timing cautions are justified.

The remaining interpretation is appropriately cautious: small historical gains do not establish future robustness; drift challenges the added factors' value; equal weighting is a transparent design rationale rather than demonstrated superior accuracy.

## D. Comparison with available previous materials

Compared with `/Users/abzz/Downloads/sp500-forecast/`, whose hashes exactly match the prior audit's source-hash record, and read `/Users/abzz/Documents/ChatGPT/S&P 500/VERIFICATION_REPORT.md` and its evidence.

The update adds **`src/report_numbers.py` and `results/report_numbers.txt`**, changes only **README.md and agent_log.md**, and omits `.DS_Store`. **All seven raw CSVs, existing model/check/forecast/sensitivity code and earlier saved results are byte-identical to the previous source.** Differences against the prior audit's regenerated CSVs are numerical formatting/roundoff, not changed source results.

The former report's “scenario unavailable/unverified” finding is superseded: the coursework text and calculation now exist. The 955 checks, small gains, timing limitations and warning-only guards remain. The updated log's attribution of its 14.5%→14.4% displayed-error correction to a new Yahoo VIX fill is not established by this comparison: the fill code, raw inputs and backtest outputs already existed unchanged. The new 94% rank refers to 5 November, not the latest origin. No previous coursework Sections 6–7 were available for a wording comparison.

Reproducible calculation evidence: [audit JSON](</Users/abzz/Documents/ChatGPT/S&P 500/UPDATED_VERIFICATION_EVIDENCE_1110.json>). Read-only harness: `/private/tmp/sp500_audit_1110/audit.py`. Only this separate report and its new evidence file were added to the workspace.
