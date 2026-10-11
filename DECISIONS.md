# Decisions (edit together at the standup)

Status: PROPOSED = suggested, not yet agreed. Change to AGREED after the team decides.

| # | Decision | Value | Status |
|---|---|---|---|
| 1 | Targets | 4 targets: price (`price actual`, EUR/MWh), demand (`total load actual`, MW), variable renewable (solar + wind onshore, MW), fossil (gas + hard coal + lignite + oil, MW). Work order: price first | PROPOSED |
| 2 | Time step | 1 hour | PROPOSED |
| 3 | Forecast horizon | next 24 hours | PROPOSED |
| 4 | Forecast issue time | once a day at 00:00 UTC (check which information is available at that time) | PROPOSED |
| 5 | Input window (LSTM) | last 168 hours | PROPOSED |
| 6 | Split (by date) | train 2015–2016, validation 2017, test 2018 (test untouched until the final run) | PROPOSED |
| 7 | Main metric | MAE per target, in its own unit (no combined number). Also report RMSE. No MAPE for targets that can be near zero | PROPOSED |
| 8 | Which mistake is worse? | price: too LOW at peak hours; demand: too LOW; renewable: too HIGH; fossil: both directions | PROPOSED |
| 9 | Baselines | last value; same hour yesterday (24h); same hour last week (168h) | PROPOSED |
| 10 | Models | 4 independent LSTMs (one per target) on one shared data pipeline | PROPOSED |
| 11 | Shared pipeline | same cleaning, same date split, same window construction, same leakage rules; scaler fitted on training data only, one per target | PROPOSED |
| 12 | Extra model (ask teaching crew first) | Gradient Boosting | PROPOSED |
| 13 | Known at forecast time | calendar features; past values; official day-ahead forecasts (load, solar, wind, price) | PROPOSED |
| 14 | NOT known at forecast time | actual weather / generation / load / price of the hours being forecast | PROPOSED |
| 15 | Missing values | short gaps (<=6h) interpolated; zeros in major plants treated as missing | PROPOSED |

## Questions for the teaching crew
- Our project forecasts 4 targets (one model each, 24h horizon). Is this accepted, or should we use price as the main target and the others as an extension?
- Can we add Gradient Boosting as an extra comparison next to the LSTM and the baselines?
- The guide asks for cross-validation. For time series, is a time-based validation (rolling windows) the right choice?

## Log (add a line for every important change)
- 2026-10-11: repo created, README and DECISIONS added.
