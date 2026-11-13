# Agent instructions (Group 13)

Agent: Claude (Anthropic) in a Claude Code session, configured model `claude-opus-5-5`.

**How these were used.** The method was developed with the agent on 7 November 2026 (see `agent_log.md`).
This file is the instruction set the group approved on 7 November. For the final run on 12/13 November
it is pasted verbatim, as the first message of a new agent session, before any other prompt.
Screenshots of the session are saved in `transcript/`.

---

## Prompt to paste at the start of the final run

> You are the research agent for IFTE0007 Group 13.
>
> **Goal.** Recommend one point forecast, to two decimal places, of the official S&P 500 price-index close
> on Friday 20 November 2026 (16:00 New York), using the method in `src/model.py`: an equal-weight average
> of a drift forecast and two one-factor OLS forecasts (VOL from the VIX, RATE from the 10-year real yield).
>
> **Data boundary.** Use only the frozen files in `data/raw/`. They were downloaded before the information
> cutoff (Friday 13 November 2026, 12:00 London). The last usable index close is Thursday 12 November.
> Do not fetch prices or use any information published after the cutoff.
>
> **Permitted tools.** Read files; run Python in this repository. No live data, paid APIs or trading.
>
> **Steps.**
> 1. Inspect `data/raw/manifest.json` and confirm source URL, retrieval time, publication rule and last usable
>    observation for every series. Stop and report if the 12 November price or VIX is missing.
> 2. Run `python src/backtest.py`, `python src/checks.py`, `python src/sensitivity.py` and
>    `python src/report_numbers.py`. Report the combination's error against the no-change benchmark,
>    and any failed check.
> 3. Run `python src/forecast.py --origin 2026-11-12`. Show the baseline, factor values, coefficients,
>    weights, the date of the real-yield observation used, and the final calculation. If the input guard
>    stops the run, report why and do not continue.
> 4. Check the result independently: recompute F by hand from the numbers in `results/final_forecast.json`.
>    Compare the baseline with the official S&P close the group provides.
> 5. Give your recommendation and the reasons for it. Do not make a discretionary adjustment unless you
>    quantify and justify it; the group decides.
