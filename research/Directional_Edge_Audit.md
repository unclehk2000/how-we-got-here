# Directional Edge Audit — ARDL by Month, Byakugan Re-test, Direction Search

**Data:** NQ 1-min for 2018 and 2022 – Aug 2026 (1,311 sessions). ES and DXY are available from 2023 only.

**Rule used for every test:** each trade is measured from a price that existed at the moment all of the rule's inputs were known.

## 1. The original directional read, month by month

### 1a. ARDL return model

- Fit: full specification, walk-forward, refit monthly.
- Out-of-sample window: Jan 2025 – Aug 2026, 312 days.
- Trading rule: the sign of the forecast, held from 09:30 to the close.

| Month | n | Hit % | Long hit % | Strategy % | Long % | Short days | Edge vs long |
|---|---|---|---|---|---|---|---|
| 2025-01 | 17 | 29.4 | 41.2 | −6.5 | −2.1 | 6 | **−4.4** |
| 2025-02 | 19 | 52.6 | 57.9 | +2.4 | −1.9 | 5 | +4.3 |
| 2025-03 | 13 | 53.8 | 46.2 | +0.5 | −5.8 | 7 | +6.3 |
| 2025-04 | 21 | 57.1 | 47.6 | −0.2 | +15.1 | 8 | **−15.3** |
| 2025-05 | 21 | 57.1 | 61.9 | +1.1 | +2.6 | 9 | −1.5 |
| 2025-06 | 12 | 66.7 | 75.0 | +2.8 | +1.9 | 7 | +0.9 |
| 2025-07 | 18 | 55.6 | 55.6 | +2.0 | −0.7 | 8 | +2.7 |
| 2025-08 | 21 | 47.6 | 52.4 | −3.0 | +0.9 | 9 | **−4.0** |
| 2025-09 | 14 | 57.1 | 78.6 | +3.1 | +2.1 | 7 | +1.0 |
| 2025-10 | 23 | 47.8 | 43.5 | −4.4 | −2.4 | 7 | −2.0 |
| 2025-11 | 18 | 55.6 | 55.6 | +6.0 | −2.0 | 8 | +8.0 |
| 2025-12 | 7 | 71.4 | 57.1 | +0.7 | +0.3 | 3 | +0.4 |
| 2026-02 | 7 | 57.1 | 71.4 | +2.3 | +2.1 | 3 | +0.2 |
| 2026-03 | 16 | 50.0 | 50.0 | −0.6 | +1.9 | 6 | −2.5 |
| 2026-04 | 14 | 35.7 | 71.4 | +0.3 | +5.4 | 7 | **−5.1** |
| 2026-05 | 20 | 65.0 | 65.0 | +1.7 | +7.1 | 6 | **−5.4** |
| 2026-06 | 15 | 33.3 | 53.3 | −2.0 | −0.6 | 7 | −1.4 |
| 2026-07 | 22 | 63.6 | 40.9 | +5.1 | −6.3 | 9 | +11.4 |
| 2026-08 | 14 | 57.1 | 35.7 | +0.4 | +1.5 | 9 | −1.0 |

**Totals:** hit 52.9% against 54.5% for always-long. Strategy +11.6% against long +19.1%. The model beat long in 9 of 19 months.

**Months that hurt most:**
- **Apr 2025 (−15.3):** the model was short on 8 of 21 days through the tariff crash and the 9 April rebound.
- **Apr–May 2026 (−10.5 combined):** short into a rally on a third of the days.
- **Jan and Aug 2025:** smaller losses (−4.4, −4.0).

**Was there a point where it broke?** No. Month-to-month variation in the hit rate is what chance alone produces (heterogeneity χ² p = 0.79). The rolling 60-day hit rate wandered between 45% and 63% with no trend. The read did not degrade at some point, because it never had an edge to lose. The bad months are the ones where it shorted into rallies.

### 1b. Prior-day DXY term alone

This is the variant that looked best: 56.7% hit, +41.5% against +19.1% long.

| | Value |
|---|---|
| Days long | 286 of 312 |
| Days short | 26 |
| Edge vs long from Apr, Oct and Nov 2025 shorts (9 days) | **+25.3%** |
| Edge vs long, all other months | **−2.9%** |
| Edge vs long, 2026 (108 days) | −1.4% |

The coefficient flips sign by year: 2023 +0.016, 2024 −0.26, 2025 −0.36, 2026 −0.77. In practice this model is always-long plus 9 well-timed shorts in 2025, and it has added nothing in 2026.

## 2. Byakugan re-tested from a tradable entry

Replicated on 1,311 sessions. The original metric reproduces: in the 0.30–1.00% target zone with a confirmed sweep, the open→close accuracy is **76.7%** (published figure 76.5–81%).

**The problem:** that metric is measured from 09:30, but the sweep is only confirmed once price has already travelled to the AL level. The median distance already banked at the sweep is 0.49%, and the median sweep time is 10:10.

**Entry at the sweep level, held to the close (n = 180):**

| | Win | Mean | t |
|---|---|---|---|
| Original metric (open→close) | 76.7% | — | — |
| **Tradable (sweep→close)** | **47.8%** | −0.018% | −0.25 |
| Bullish target zone | 47.4% | +0.062% | |
| Bearish target zone | 48.1% | −0.077% | |

**By year (tradable win %):**

| 2018 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| 41 | 45 | 50 | 53 | 58 | 42 |

**Brackets** use your Stage 5 R-multiples of the 7–9 range, with a time stop at the close:

| Stop / target | Expectancy | t |
|---|---|---|
| 0.5R / 1.0R | −0.074R | −1.51 |
| 1.0R / 2.0R | −0.053R | −0.59 |
| 1.25R / 2.25R | −0.023R | −0.22 |
| 1.0R / 1.0R | −0.012R | −0.16 |

When the price path after entry has no drift, no stop/target combination can create a positive expectancy (optional stopping), and that is what these numbers show.

**"No sweep → fade":** this is only known at the close. The tradable version is: no sweep by 12:00, fade from the 12:00 price. It gives 50.5% wins, mean +0.067%, t 1.37 (n = 202). Not significant.

**What Byakugan does deliver:** a map of levels that price is likely to reach. The tap rate is high, and the 7–9 range width predicts RTH range (r = 0.40). It does not deliver a directional edge from any point you could enter.

## 3. Search for a directional predictor

### 3a. Walk-forward regressions

21 specifications, refit monthly, out-of-sample 2023-01 → 2026-08 (2024+ for the ES/DXY terms):

- **09:30 features:** gap, overnight return, prior-day return, open position in the 7–9 range / prior-day range / overnight range, Byakugan bias, distance to the AL extremes, 5-day return, all combined.
- **10:00 features:** first-30-minute return, return from prior close to 10:00, position in the opening range.
- **Last-30-minute momentum:** three variants.
- **Cross-market:** NQ−ES gap divergence (SMT), DXY overnight move, DXY prior-day move.

**Result:** no specification beats always-long on hit rate, on P&L, or on out-of-sample R², which is ≤ 0 in every case. The best is the DXY prior-day term: t 1.51 vs long, against a Bonferroni threshold of 3.04.

Two signals are significantly **wrong-way** out of sample. The cause is that their sign flipped after 2022:

| Correlation with target | 2018 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| prev close→15:30 vs last 30 min | +0.15 | +0.12 | −0.04 | −0.03 | −0.03 | −0.03 |
| prior-day return vs open→close | −0.09 | −0.02 | +0.05 | +0.03 | **−0.33** | +0.04 |

Intraday momentum (Gao et al.) worked in the high-volatility bear years and disappeared in 2023–26. A model fitted on 2018/2022 carries that sign into a regime where it no longer holds.

### 3b. Fixed rules (no fitting), `direction_lab.py`, 2018–2026

| Signal | Trades | Win | Mean % | t | Years positive |
|---|---|---|---|---|---|
| Always long 09:30→close | 1,311 | 53.8 | +0.024 | 0.70 | 3/6 |
| Byakugan bias at open | 1,311 | 50.2 | −0.025 | −0.74 | 2/6 |
| Byakugan sweep entry | 180 | 47.8 | −0.018 | −0.25 | 1/6 (2023 flat) |
| Byakugan noon fade | 202 | 50.5 | +0.067 | 1.37 | 4/6 |
| Gap fade | 1,277 | 50.4 | +0.047 | 1.34 | 4/6 |
| **Follow first 30 min, 10:00→close** | 1,310 | 52.6 | +0.054 | 1.76 | **6/6** |
| Last-30 momentum | 1,280 | 50.0 | +0.006 | 0.66 | 3/6 |
| **Pre-FOMC: long 14:00 day before → 14:00 FOMC day** | 44 | **70.5** | **+0.447** | **3.00** | 5/6 |

The Bonferroni threshold for 7 signals is |t| > 2.69.

**Pre-FOMC drift** is the only signal that clears it. It is the published Lucca–Moench effect. Most of the move happens overnight (+0.29%), and the 13:30–14:00 window is also positive every year (t 2.19). The effect is fading, though:

| | Mean | Win |
|---|---|---|
| 2018–2024 (32 trades) | +0.65% | 81% |
| 2025–2026 (12 trades) | −0.08% | 42% |

**First-30-minute follow** is positive in all six years but small (about 11 pts at 20,000) and not significant (t 1.76). It is a candidate to track forward, not to trade on yet.

**Other effects, none significant:** turn-of-month (p 0.66), weekday, trend regime (prior close above vs below its 50-day mean, p 0.997), and the overnight vs RTH split.

## 4. Conclusion

From NQ, ES and DXY prices alone, daily direction cannot be predicted beyond the long drift. The original read had no month in which it worked and then stopped. Byakugan's directional numbers come from where they are measured, not from information. Of everything tested, one event effect survives (pre-FOMC), and it is weakening.

An edge needs information that is not already in the price. Candidates that can be tested with the same lab once the data exists:

| Source | Why it could carry direction | Data needed |
|---|---|---|
| Economic surprise on CPI/NFP/FOMC days | The sign of actual − consensus drives the post-release move | Release history with consensus |
| Dealer gamma / 0DTE positioning | Positive gamma pins and mean-reverts; negative gamma trends | Daily GEX or SPX/NDX option open interest |
| Order flow | Cumulative delta and absorption at levels | Tick or footprint data with bid/ask volume |
| Breadth | NYSE TICK/ADD extremes at the open | 1-min $TICK / $ADD |
| COT positioning | Weekly horizon (your octant framework) | Weekly COT, already in your framework |

`direction_lab.py` tests any new rule from a tradable entry. It reports results by year and by month, a month-heterogeneity test, the same trades taken long as a drift control, and the Bonferroni threshold for however many signals you ran. Add a rule as one function at the bottom of `SIGNALS`.
