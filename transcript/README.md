# Final agent run - transcript

Evidence of the final run on 12 November 2026 (22:15-22:26 London, after the US close), required by the
brief ("a short run transcript or screenshots"). The screenshots are taken from the saved agent session.
The data download that preceded it (22:08 UTC) is also recorded in `data/raw/manifest.json`.

| File | What it shows |
|---|---|
| 01_fetch_data_output.png | `fetch_data.py` output (12 Nov, before the agent run): last usable date and value of every series |
| 02_prompt_(1).png, 02_prompt_(2).png | The instructions pasted verbatim from `AGENT_INSTRUCTIONS.md` at the start of the agent session |
| 03_forecast_output.png | `src/forecast.py` output: baseline, factors, coefficients, weights, real-yield date, final forecast |
| 04_checks.png | Results of the backtest and checks run by the agent |
| 05_recommendation.png | The agent's recheck and final recommendation |
