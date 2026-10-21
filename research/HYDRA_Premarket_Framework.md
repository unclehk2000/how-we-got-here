# HYDRA — NQ Pre-Market Decision Heads

`hydra.py` runs during ETH (default freeze time 09:25 ET, which is 14:25 UK, or 13:25 UK in the DST-mismatch weeks, 25 Oct–1 Nov 2026). It prints six heads. Each head comes with its own walk-forward backtest, so every number on the screen can be traced back to history. Heads that fail their test are still printed, labelled as failed.

```
python hydra.py backtest  --data "hist/*.csv"                       # refit + validate every head -> hydra_model.json
python hydra.py premarket --data "recent/*.csv" --sofr 3.9 --div 0.7  # today's report, appended to hydra_log.csv
python hydra.py score     --data "recent/*.csv"                       # fill realised outcomes, print forward record
python hydra.py premarket --data ... --asof "2026-06-16 09:20"        # replay any past morning
```

**Morning data.** You need Barchart 1-min files for the traded contract that cover the last 5 sessions plus today's ETH. For the carry head, also add the same window for the next contract. Both Barchart formats load as-is, and timestamps are converted from CT to ET.

`hydra_model.json` is already fitted on 2018, 2022 and 2023–Aug 2026 (1,241 sessions), so `premarket` works straight away. Re-run `backtest` monthly, or whenever you add history.

## Backtest summary

The walk-forward is refit monthly on an expanding window. The out-of-sample period runs 2024-01-05 → 2026-08-20, n = 569 days.

| Head | Output | Backtest | Status |
|---|---|---|---|
| H1 Range | RTH range forecast (% and pts), P10/P90, bands at open ± k·F, tercile | OOS R² 0.32. Beats AR(3) (0.26) and the 20-day mean (0.16), Diebold-Mariano p < 0.01 for both. Realised/forecast median 0.95. P10–P90 covers 78.7% (target 80) | **Validated** |
| H1 bands | Touch odds at k = 0.25/0.5/0.75/1.0 × F, by tercile | Fixed 224-pt band touched on 27% of Low days, 52% of Mid, 66% of High (χ² p < 0.001) | **Validated** |
| H2 Day type | Trend-day rate (\|close−open\| ≥ 50% of range) | Low/Mid/High 46/49/44%, p = 0.61 | Not significant (descriptive only) |
| H3 Post-touch | After the first ±0.5F touch: closes on that side, reaches 1.0F, returns through the open, reaches the opposite 0.5F | 87.4 / 31.2 / 25.8 / 6.5% against a shuffled-bar random walk of 86.0 / 30.2 / 28.2 / 6.9%. All p ≥ 0.19 | No edge (expectation-setting only) |
| H4 Calendar | Weekday and event effects on range, upcoming events | FOMC +28% (t 3.4), Thu +12% (t 3.0), Wed +9% (t 2.0), NFP +10% (t 1.5), Mon −6% (t −1.5) | FOMC, Thu, Wed significant |
| H5 Direction | Sign of the RTH open→close move | OOS hit 50.1% vs always-long 53.7% (p 0.09), R² 0.01 | **Rejected** |
| H6 Carry | Expiring vs next contract: spread, implied carry, fair spread from SOFR − div, richness in pts/$, basis decay, roll/expiry status, volume share | Roll window (expiry − 8d → expiry, 131 days): range ×0.97, p = 0.48. \|return\| p = 0.84 | Calculator only. Predictive test pending data |

## H1 detail

The model is log RTH range % = c + three lags of log range + Δ log overnight range + |overnight move| + weekday + FOMC + NFP. Every input is known at the freeze time.

| Term | Coef | Effect on range | NW t |
|---|---|---|---|
| range lag 1 / 2 / 3 | 0.249 / 0.242 / 0.165 | — | 9.8 / 10.4 / 7.1 |
| Δ overnight range | 0.084 | — | 3.5 |
| \|overnight move\| % | 0.093 | +9.7% per 1% | 4.4 |
| FOMC | 0.251 | +28.5% | 3.4 |

The DXY and NQ−ES terms from the ARDL document were tested and dropped. Out of sample, the NQ-only model gives R² 0.407 against 0.409 for the full model, so the tool needs only NQ files.

The R² here (0.32) is lower than the 0.42 in `ARDL_Equation_NQ_Test.md` for three reasons:
- The OOS window is longer and starts in 2024.
- The features freeze at 09:25 instead of 09:30.
- The training sample is larger and includes 2018 and 2022.

**Touch odds of open ± k·F**

| k | Any side | Both sides | Any, Low / Mid / High tercile |
|---|---|---|---|
| 0.25 | 99.5% | 31.8% | 99.5 / 100 / 98.9 |
| 0.50 | 78.2% | 5.1% | 81.6 / 77.2 / 75.8 |
| 0.75 | 47.6% | 0.4% | 54.2 / 50.3 / 38.4 |
| 1.00 | 25.1% | 0.2% | 26.8 / 30.7 / 17.9 |

Tercile cut-offs are F = 1.21% and 1.52%.

On High-tercile days the forecast overshoots: the median realised/forecast ratio is 0.875, against about 0.98 on Low and Mid days. The report therefore always prints the touch odds for the day's own tercile, not the pooled figure.

Reading the table: a ±0.5F level gets tagged on about 4 days in 5 but only 1 in 20 days tags both. A 1.0F extension is a 1-in-4 event, and a 1-in-6 event on High days.

## H3 note — earlier ladder figures retracted

`ladder.py` (written by another session in the same folder) sliced each day's bars by label on an index that was not in time order. Its post-touch figures are wrong. Rebuilt on bars sorted by time, the statistics match a random walk with the same day's volatility. Once the 0.5F level is touched, what follows carries no information beyond H1. Use H3 for sizing expectations, not as a signal.

## H6 carry calculator

Implied carry = ln(F_next/F_front) × 365 / days between expiries. Fair spread = F_front × (e^((SOFR−div)·Δt) − 1). Richness = spread − fair, in points and at $20/pt.

Replay check, 16 Jun 2026 09:20 ET:
- M26 30527.25, U26 30837.00.
- Spread +309.75 pts, implied carry 4.05%.
- At SOFR 3.65% and dividend 0.7%, the fair spread is 225 pts, so the market was rich by 84 pts ($1,688 per contract).
- U26 had 70% of the prior session's volume.

Implied carry from the overlapping 2026 files:

| Date | Implied carry |
|---|---|
| 13 Mar | 3.47% |
| 10–12 Jun | 3.90–3.93% |
| 15 Jun | 4.00% |
| 16 Jun | 4.21% |
| 17 Jun | 4.16% |

Implied carry has stayed about 0.5–1 pt above SOFR − div.

**Why carry can't be backdated yet:** there are only 7 days where both contracts overlap, which gives 2 weekly pairs. The test of whether a change in carry predicts next-week range runs automatically once there are 20 or more weekly pairs. That needs either of:
- Overlapping per-contract files for both contracts.
- A `--carry-hist` CSV of `date,front,next` daily settlements. Barchart per-contract daily history for H/M/U/Z since 2022 covers this in one download per contract.

## Forward record

Every `premarket` run appends a row to `hydra_log.csv`. `score` then adds the realised open/high/low/close, the realised/forecast ratio, whether the range fell inside P10–P90, and the band touches. It prints the live hit rates next to the backtest figures. This is the out-of-sample record that builds up from now on.

## Data caveats in the history

- On quarterly expiry Fridays the expiring contract settles at the 09:30 open and has no RTH. The continuous files keep the expiring contract until Sunday, so all 20 expiry Fridays from 2018 to 2025 are missing from the history. The per-contract 2026 files show that the next contract trades a full session on those days (20 Mar 2026: 405 bars in M26). These are gaps in the data, not market closures. On expiry day the report tells you to trade the next contract.
- The continuous files switch contract the Sunday after expiry and are not back-adjusted, so the first session after a switch has no valid overnight move and is excluded from fitting. The live run always uses one contract's own file, so it is unaffected.
- The year files end mid-December, so late-December sessions are missing. Half-days are flagged through `events.csv` and should be read with caution: the model is fitted on full sessions only.
