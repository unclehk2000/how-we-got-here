# Kyōka Suigetsu — Task 3 findings (ES and RTY 1-minute)

**Data used:**
- ES 1-minute data, 2018–2022 (new, 21 files)
- ES 1-minute data, 2023–2026 (earlier upload)
- NQ 1-minute data, 2018–2026

RTY 1-minute data (2018–2026) was added in v13: see section 5.

**Method:** same as before. Models are fitted on 2018–24 and tested on 2025–26. All results use the full trading day, 18:00–17:00 ET.

**Result:** two changes in v12:
1. The live projection is refitted on NQ and ES together. It is as accurate as before, with twice the data behind it.
2. New: a calibrated chance that today's high or low is already in.

---

## 1. Data check

- **Format.** Barchart files with Central Time timestamps. Each file covers one front-month window.
  - Timestamps converted to ET by adding 1 hour.
  - Each file is cut at midnight CT, so the 20 roll trading days are split between the old and new contract.
  - On those days, the old-contract part (18:00–00:59 ET) was shifted by the previous day's settlement spread, taken from the task-2 per-contract files. The spread ranged from −13 to +31.5 pts.
- **Trading days.** Days follow the CME convention: a holiday session belongs to the next trading day. This is the same as Barchart's daily bars, and it affected 59 sessions per market over 2018–2026.
- **Check against Barchart daily.** The 1-minute high and low match Barchart exactly on almost every day:

  | Period | High matches | Low matches |
  |---|---|---|
  | 2018–22 | 99.3% | 99.5% |
  | 2023–26 | 99.6% | 99.5% |

- **Days whose range differs by more than 2%: 13**, all explainable:
  - 2018-12-05: market closed for President Bush's funeral.
  - 2020-03-09: limit-down open.
  - 2021-04-02: shortened Good Friday session.
  - 2019-05-16: a bad Barchart low.
  - Two expiry Fridays with partial data in the earlier file.
  - 2026-08-28: the last day in the data is incomplete.
- **Days kept for the intraday tests:** 2,099 for ES and 2,010 for NQ. These exclude the days above and the days that had a holiday session folded in.

## 2. Live projection: does ES need its own weights?

**Test set:** 2025–26.
**Measure:** mean absolute error of the log final range, averaged over the hour checkpoints 18:59–16:59.

| Test market | NQ weights (v11) | ES weights | Pooled NQ + ES | P25–P75 coverage (NQ / ES / pooled weights) | P10–P90 coverage (NQ / ES / pooled weights) |
|---|---|---|---|---|---|
| ES | 0.221 | 0.221 | 0.221 | 54 / 56 / 55% | 80 / 81 / 81% |
| NQ | 0.211 | 0.211 | 0.211 | 56 / 56 / 56% | 81 / 82 / 82% |

**ES, test 2025–26: error of the live projection by time of day.** Baselines are the typical day (0.388) and the expected range alone (0.310).

| Time (ET) | 08:59 | 09:59 | 10:59 | 12:59 | 14:59 |
|---|---|---|---|---|---|
| Error (MAE, log) | 0.252 | 0.234 | 0.191 | 0.144 | 0.062 |

- **ES needs no weights of its own:** the NQ fit transfers almost exactly.
- **v12 uses the pooled NQ + ES fit** (2018–2026, about 4,100 days). It is just as accurate, with twice the data behind it.
- **Days in profile:** the default stays at 30. The N used for the typical share of the day done by each hour barely matters from 30 up:

  | N | 10 | 20 | 30 | 45 | 60 | 90 |
  |---|---|---|---|---|---|---|
  | MAE | 0.230 | 0.227 | 0.226 | 0.226 | 0.226 | 0.226 |

## 3. New: chance the high / low is already in

**The question:** at any minute, what is the chance that today's high (or low) won't be beaten before 17:00 ET?

### Base rate: share of days with the high / low already in, by the end of each hour (NQ + ES, 2018–2026)

| Time (ET) | 18:59 | 02:59 | 08:59 | 09:59 | 10:59 | 12:59 | 14:59 | 15:59 |
|---|---|---|---|---|---|---|---|---|
| High in | 8% | 20% | 34% | 43% | 51% | 60% | 71% | 87% |
| Low in | 12% | 28% | 43% | 51% | 60% | 71% | 81% | 92% |

The low comes earlier than the high on most days. That is the upward drift of equity index futures.

### Models compared (train 2018–24, test 2025–26)

The score is the Brier score at every half-hour. Skill is the improvement on the base rate for that half-hour.

| Model | Parameters | NQ skill | ES skill |
|---|---|---|---|
| Position of price in today's range only | 44 | 20% | 19% |
| Logistic: range so far vs expected, plus position | 66 | 24.3% | 22.9% |
| **Random walk: P = 2Φ(d ÷ σ left) − 1** | **1 + profile** | **24.9%** | **22.9%** |
| Same, with σ from the live projection instead of the expected range | 1 + profile | 24.7% | 23.1% |

How to read the random-walk model:
- **d** is the distance from the current price to today's high (or low).
- **σ left** = 0.655 × expected range × √(share of the day's variance still to come).
- From 09:30 ET onward the skill is 37–38% on both markets.

**Honest reading: this is geometry, not hidden edge.**
- A plain random-walk formula does as well as a fitted model with 66 coefficients.
- What Kyōka adds is the scale: the expected range sets how far price can still travel. With it, the probability is calibrated rather than a guess.
- It shows how much of a context row the high-in / low-in figures are; it is not a signal.

### Calibration: Pine logic run on every minute of 2025–26, NQ + ES (about 1.07 million bars)

| Predicted | 5 | 15 | 25 | 35 | 45 | 55 | 65 | 75 | 85 | 93 | 99 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Actual | 5 | 16 | 26 | 37 | 47 | 57 | 65 | 74 | 82 | 91 | 98 |

- **High side:** average predicted 35.1%, actual 35.4%.
- **Low side:** average predicted 42.8%, actual 43.8%.
- **Skill:** 24.9% on NQ and 23.1% on ES.

The formula needs no drift term. With an upward drift, price tends to sit nearer the high, and that alone produces the higher low-in rate.

### Worked examples

| Situation | High in | Low in |
|---|---|---|
| 02:00, range 30% of expected, price mid-range | 20% | 20% |
| 10:30, range 60% of expected, price 10% off the low | 77% | 11% |
| 14:00, range 100% of expected, price 25% off the high | 60% | 99% |

### Share of the day's variance still to come (NQ + ES, 2018–2026)

| End of hour (ET) | 18:59 | 00:59 | 03:59 | 06:59 | 08:59 | 09:59 | 10:59 | 11:59 | 12:59 | 13:59 | 14:59 | 15:59 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Still to come | 0.97 | 0.87 | 0.80 | 0.73 | 0.63 | 0.53 | 0.41 | 0.33 | 0.27 | 0.21 | 0.14 | 0.03 |

The profile is stable across periods. At 08:59 ET the share still to come was 0.59 / 0.65 / 0.71 / 0.66 in 2018–20 / 2021–22 / 2023–24 / 2025–26. The 2018–20 figure is lower because of the extra overnight volatility in 2020.

## 4. What changed in v12

- **New "HIGH / LOW IN" row** on the status card ("H/L in" on mobile):
  - The chance the high is already in and the chance the low is already in.
  - Plus **σ left**: one standard deviation of the move still to come before 17:00, in points.
  - Switched on by the new input "Chance the high / low is already in" in the Expected range group.
  - Needs an intraday chart of 60 minutes or lower.
- **Projection weights refitted** on NQ + ES 1-minute data, 2018–2026.
- The variance profile (VREM) and κ = 0.655 are stored as constants.
- **Nothing else changed.** Expected range, distributions, cards, alerts and layout are as in v11.

## 5. RTY 1-minute (v13)

**Data:** Barchart RTY 1-minute, QRH18 … QRZ26 (36 front-month files, Central Time), built exactly like ES 2018–22:
- CT → ET; 35 roll trade dates shifted by the prior day's settlement spread (−4.7 to +26.1 pts).
- 2,208 trade dates, 2 Jan 2018 – 9 Oct 2026; 60 holiday sessions folded into the next trade date.
- Against Barchart daily: high matches exactly on 99.0% / 98.7% of days (2018–22 / 2023–26), low on 98.1% / 98.2%. 14 days differ by more than 2% in range (a cluster of Mondays in Oct–Nov 2021, the 2020-03-09 limit-down open, 2019-05-16); the intraday tests drop them.
- **Days kept for the intraday tests: 2,128.**

**Test:** train 2018–24, test 2025–26 (430 RTY days), same measures as sections 2–3.

| Live projection, mean MAE over the 23 hourly checkpoints | NQ+ES weights (v12) | RTY's own | NQ+ES+RTY pooled |
|---|---|---|---|
| RTY | 0.216 | 0.214 | 0.215 |
| NQ | 0.211 | 0.211 | 0.211 |
| ES | 0.221 | 0.222 | 0.221 |

- **The projection weights transfer.** RTY's own weights are 1% better on RTY, inside the noise; pooling all three markets is neutral on NQ / ES and slightly better on RTY. **v13 uses the NQ + ES + RTY pooled fit** (about 6,200 days).
- **Kappa transfers:** 0.665 fitted on RTY vs 0.660 on NQ + ES (production stays 0.655).
- **The variance profile does not.** RTY gets more of its day done by midday, in every period:

| Share still to come at | 11:00 | 12:00 | 13:00 | 14:00 | 15:00 |
|---|---|---|---|---|---|
| NQ+ES 2018–20 / 21–22 / 23–24 / 25–26 | 0.40 / 0.41 / 0.44 / 0.43 | 0.33 / 0.33 / 0.35 / 0.34 | 0.27 / 0.27 / 0.28 / 0.28 | 0.22 / 0.20 / 0.21 / 0.16 | 0.16 / 0.12 / 0.13 / 0.11 |
| RTY 2018–20 / 21–22 / 23–24 / 25–26 | 0.37 / 0.38 / 0.33 / 0.39 | 0.28 / 0.30 / 0.26 / 0.31 | 0.22 / 0.24 / 0.21 / 0.25 | 0.17 / 0.18 / 0.16 / 0.15 | 0.11 / 0.09 / 0.08 / 0.08 |

**High / low already in, Pine logic run on every minute of RTY 2025–26 (580,000 bars):**

| Constants | Skill vs base rate | 09:30–16:00 | RTH calibration (predicted / actual %) |
|---|---|---|---|
| v12 (NQ+ES profile) | 24.7% | 39.5% | 30/36 · 50/59 · 70/79 |
| **v13 (RTY profile)** | **25.2%** | **40.7%** | 30/34 · 50/56 · 70/76 |

With the NQ / ES profile the chance reads too low on RTY in the afternoon, because it assumes more volatility is still to come than RTY usually has. RTY's own profile fixes most of that.

**What changed in v13:**
- Projection weights (PW / PC) refitted on NQ + ES + RTY, 2018–2026.
- New `VREMR`: RTY's variance profile, used when the model resolves to RTY (RTY / M2K on Auto, or Model = RTY). NQ, ES and everything else keep `VREM`, which is unchanged.
- Kappa unchanged (0.655). Nothing else changed.

## 6. Next

- **VIX / VXN:** dropped.
- **Refit once a year:** the daily model, the projection weights, kappa and both variance profiles.
