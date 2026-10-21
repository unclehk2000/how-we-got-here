# Kyōka Suigetsu — Task 2 Findings (NQ · ES · RTY daily, 2010–2026)

**Data:** Barchart daily bars for every quarterly contract H10–Z26 of NQ, ES and RTY, plus the spliced continuous series. Cleaned sample: 4,226 trading days per market (4 Jan 2010 – 9 Oct 2026).
**Method:**
- Every forecast uses only information available before the day starts.
- Out of sample means one of three things: a walk-forward refit each year on all prior years, train 2010–20 → test 2021–26, or the house split train 2018–24 → test 2025–26.
- Range accuracy is scored as the mean absolute error of the log range, so a 0.30 error means the typical miss is about ×1.35 either way.

---

## 1. Data check

| Check | Result |
|---|---|
| Flat or impossible bars after 2010 | none |
| Session | full trading day 18:00–17:00 ET. Open, high and low match the 1-minute NQ set to the tick on 90% of days; the other 10% are roll-window days where a different contract was chosen. Range ratio vs the 1-minute set: median 1.000 |
| Close | **settlement**, not the 17:00 last trade (median gap 11 NQ pts). It matches TradingView's "settlement as close" |
| NQ volume / OI | per-contract up to the Z24 file; from H25 on, Barchart returns the whole-market total. Fixed: total = the larger of (sum of per-contract files) and (aggregate file) |
| ES / RTY volume / OI | whole-market totals in every file (as the README says) |
| RTY 2012–17 | 28 extra rows on US holidays (ICE-era holiday sessions). Dropped so all three markets share the CME calendar. RTY volume before Aug 2017 is not usable |
| Carry series | ln(next ÷ front settlement) ÷ time between expiries tracks the rate cycle. NQ was −0.5 to −0.9%/yr in 2010–16 and +4.8% in 2023–24; ES and RTY sit lower because of higher dividends |

---

## 2. Kyōka's existing profiles on 16 years

**Weekday range.**
- Measure: median range ÷ prior ATR14, relative to all days.

| | Mon | Tue | Wed | Thu | Fri |
|---|---|---|---|---|---|
| NQ | 0.98 | 0.99 | 1.00 | **1.05** | 0.99 |
| ES | **0.94** | 0.98 | 0.99 | **1.06** | 1.03 |
| RTY | 1.00 | 1.00 | 1.00 | **1.04** | 0.98 |

- Thursday is the widest day in every market and both halves. It sits above the median in 12/17 years (NQ), 14/17 (ES) and 11/17 (RTY).
- The effect is real but tiny. Adding weekday multipliers to a trailing-median forecast changes the out-of-sample error by **+0.06% / +0.12% / −0.16%**.
- **Verdict:** keep the weekday card as a map; it is not a forecasting tool.

**Monthly seasonality (net %).**
- No month is significant after Bonferroni in any market.
- The spread of month means is no wider than shuffled data (p = 0.65 / 0.32 / 0.44).
- Rank correlation of month means between 2010–17 and 2018–26 is **negative** (−0.46 / −0.19 / −0.34).
- Long only in months that were positive in 2010–17 **lost to always-long in 2018–26** in all three markets:

| | Always-long | Seasonal-long |
|---|---|---|
| NQ | 154% | 109% |
| ES | 103% | 61% |
| RTY | 67% | 28% |

- Monthly *range* seasonality is just as unstable (rank corr −0.17 / −0.75 / −0.05).
- **Verdict:** this confirms the earlier result on twice the history. The month card stays a map with no edge claim.

**Day that sets the week's high / low.**
- Friday sets the week's high 37% of the time and Monday sets the low 35%.
- A null that keeps each week's real days but shuffles their order gives the same picture within about 2 pp: high on Friday 36.6%, low on Monday 35.2%.
- "High so far holds after Wednesday" is 47% actual vs 49% null.
- So it is the geometry of a 5-step path plus upward drift, not a weekday effect.
- **Verdict:** don't build a "weekday sets the extreme" feature.

---

## 3. What the new data adds

### 3.1 Expected range for today (anchored HAR) — the big one

- **Inputs:**
  - log range over the last 1, 5 and 22 days, each relative to the last 250 days' typical, which makes it regime-adaptive;
  - yesterday's up or down move;
  - whether yesterday was an inside day;
  - weekday;
  - monthly opex Friday;
  - turn of month;
  - pre- and post-holiday.
- **Walk-forward 2013–2026** (refit every year on all prior years):

| | Beats Kyōka "typical day" (median of last 30) | Pooled error vs typical | Beats ATR14 | P25–P75 band covers |
|---|---|---|---|---|
| NQ | 13 / 14 years | 0.313 vs 0.372 (**−16%**) | 12 / 14 | 49% |
| ES | 14 / 14 | 0.315 vs 0.393 (**−20%**) | 14 / 14 | 49% |
| RTY | 13 / 14 | 0.292 vs 0.335 (**−13%**) | 13 / 14 | 49% |

- In the house split (train 2018–24 → test 2025–26), R² of log range rises from 0.13 to 0.41 (NQ) and from 0.14 to 0.43 (ES).
- Refitting matters. A model trained only on 2010–17 under-forecast NQ by about 13% in 2025–26, anchored or not; ES (+4%) and RTY (+2%) barely drifted. Refitting each year keeps the bias near 0, and the production coefficients below use all of 2010–2026. Expect to refit them once a year.

**What moves the expected range** (2010–2026 fit; multiplier on the day's range, t-stat in brackets):

| Driver | NQ | ES | RTY |
|---|---|---|---|
| Yesterday an inside day | ×1.13 (6.6) | ×1.13 (6.4) | ×1.10 (4.8) |
| Pre-holiday | ×0.88 (−3.6) | ×0.87 (−4.2) | ×0.89 (−3.7) |
| Post-holiday | ×1.11 (3.1) | ×1.15 (4.1) | ×1.09 (2.5) |
| Monthly opex Friday | ×0.93 (−2.2) | ×0.93 (−2.3) | ×0.92 (−2.8) |
| Turn of month (last + first 3 days) | ×1.04 (2.7) | ×1.06 (4.0) | ×1.06 (4.3) |
| Thursday (vs Monday) | ×1.07 (3.4) | ×1.12 (5.7) | ×1.04 (2.1) |
| Yesterday −1% | ×1.07 | ×1.07 | ×1.03 |
| Yesterday +1% | ×0.87 | ×0.84 | ×0.91 |

- The move effects apply on top of the change in yesterday's range.

**Tested and left out** (out-of-sample change in error, NQ / ES / RTY):

| Candidate | Result |
|---|---|
| Relative volume | −1.0% / −0.3% / +0.2%, and TradingView's continuous volume drops around the roll |
| OI change | +0.8% / 0.0% / +0.7% (worse) |
| Other markets' ranges | −0.7% / 0.0% / 0.0% |
| NR7 | 0 |
| Roll week | about 0 |

### 3.2 Live projection of the day's range

At each hour, the projection blends two estimates of where the day will finish:
- the range so far ÷ the typical share of the day done by that hour;
- the expected range from 3.1.

The HAR weight falls from 0.85 at 18:59 to 0.50 at 08:59, 0.34 at 09:59, 0.10 at 11:59 and 0 by 14:59. It is fitted on NQ 2018–24 and tested on 2025–26. ES 2023–26 uses NQ's weights unchanged.

| Known at (ET) | NQ projection | NQ share-only | NQ typical | ES projection | ES share-only | ES typical |
|---|---|---|---|---|---|---|
| 20:59 | **0.281** | 0.401 | 0.353 | **0.306** | 0.424 | 0.386 |
| 02:59 | **0.273** | 0.360 | 0.353 | **0.300** | 0.392 | 0.386 |
| 08:59 | **0.247** | 0.305 | 0.353 | **0.263** | 0.322 | 0.386 |
| 09:59 | **0.218** | 0.242 | 0.353 | **0.247** | 0.285 | 0.386 |
| 10:59 | **0.175** | 0.186 | 0.353 | **0.208** | 0.229 | 0.386 |
| 12:59 | **0.127** | 0.128 | 0.353 | **0.161** | 0.164 | 0.386 |

- The P25–P75 band covers 51–60% (NQ) and 45–53% (ES).
- At 08:59 the projection's miss is 30% smaller than the "typical day" figure Kyōka shows now (NQ: 0.247 vs 0.353).

### 3.3 Carry (task for the carry framework)

- Weekly change in carry moves with that week's return: correlation +0.06 to +0.55, because rates fall when stocks fall.
- Raw Δcarry → next-week range looks strong for ES (ρ −0.27 and −0.18).
- After controlling for the week's move and range, it mostly disappears:

| | 2010–17 | 2018–26 |
|---|---|---|
| NQ (t) | +0.3 | −1.1 |
| ES (t) | −1.5 | −2.1 |
| RTY (t) | 0.0 | −0.8 |

- Carry level → next-month return: ρ −0.03 / −0.05 / −0.10, not significant.
- **Verdict:** carry is a clean rates gauge, but it adds no volatility or direction information beyond price. ES is borderline and worth re-checking as the weekly log grows.

### 3.4 Direction (vs always-long)

- No calendar flag beats always-long.
- Turn-of-month days return the same as other days.
- Pre-holiday is positive but not significant.
- Opex Friday is negative for NQ in both halves (−0.04%, −0.18%/day), but that is one result out of 36 tests and doesn't survive correction.
- Across these tests, no calendar rule beat the carry-charge benchmark.

---

## 4. Upgrade spec for Kyōka Suigetsu

Built into Kyoka_Suigetsu.pine (v11).
- The indicator's forecast code was mirrored in Python and checked against the research model on 2010–2026 daily bars: 99.8% of days agree within 0.01 log.
- The CME holiday rules match the real calendar on every day except the unscheduled 5 Dec 2018 closure.

1. **Expected range (status card + clock).**
   - Replace "typical day" (median of the last 30) with the anchored-HAR expected range, shown in % and points with P25–P75.
   - Inputs come from TradingView's own daily bars: unadjusted for range %, back-adjusted for the return and the inside-day check.
   - Coefficients are fixed per market: NQ / MNQ, ES / MES and RTY / M2K, with a pooled set for anything else.
2. **Projected day range (live).**
   - Use the per-hour blend from 3.2, with a P25–P75 band.
   - Draw it at the session end of the clock, and add it to the status card with "pts still to go".
3. **Calendar line.**
   - Show today's active drivers with their multipliers: inside day, pre/post-holiday, opex Friday, turn of month, weekday.
   - Holidays come from the CME rules: New Year, MLK, Presidents, Good Friday, Memorial, Juneteenth (2022+), July 4, Labor, Thanksgiving, Christmas.
4. **Alerts.**
   - Add "expected range reached" and "projection above P75 of expected".
5. **Unchanged:** weekday card, month card, hour-of-high/low card and the range clock baseline. They are honest maps, and the tests above found nothing to add to them.

---

## Appendix — constants

**Expected range:**
- ln(range %) = L + const + Σ coefᵢ·xᵢ.
- L is the mean ln(range %) of the last 250 completed days.
- d1, d5 and d22 are the mean ln(range %) over the last 1, 5 and 22 days minus L.
- dn1 = max(−yesterday's return %, 0); up1 = max(yesterday's return %, 0).
- The rest are 0/1 flags.
- Median day = exp(… + q50); bands use q25 and q75.

| | const | d1 | d5 | d22 | dn1 | up1 | inside | tue | wed | thu | fri | opex | tom | pre_hol | post_hol | q10 | q25 | q50 | q75 | q90 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NQ | −0.016 | 0.217 | 0.487 | 0.204 | 0.064 | −0.136 | 0.124 | 0.007 | 0.041 | 0.066 | 0.024 | −0.068 | 0.042 | −0.126 | 0.107 | −0.486 | −0.269 | −0.013 | 0.250 | 0.492 |
| ES | −0.042 | 0.253 | 0.503 | 0.175 | 0.067 | −0.179 | 0.120 | 0.038 | 0.069 | 0.111 | 0.079 | −0.072 | 0.062 | −0.143 | 0.142 | −0.486 | −0.270 | −0.020 | 0.248 | 0.506 |
| RTY | 0.004 | 0.213 | 0.451 | 0.241 | 0.027 | −0.098 | 0.091 | 0.003 | 0.022 | 0.037 | 0.006 | −0.087 | 0.062 | −0.119 | 0.082 | −0.452 | −0.250 | −0.014 | 0.230 | 0.465 |
| Pooled | −0.018 | 0.231 | 0.482 | 0.202 | 0.047 | −0.129 | 0.112 | 0.015 | 0.043 | 0.070 | 0.035 | −0.076 | 0.055 | −0.128 | 0.112 | −0.475 | −0.263 | −0.016 | 0.245 | 0.491 |

**Live projection:**
- proj = ln(range so far) − ln(typical share by this hour).
- final = max(ln(range so far), proj + c + w·(expected − proj)).
- Fitted on NQ 2018–2026. Slot 0 = 18:00–18:59 ET, …, slot 22 = 16:00–16:59.

| slot | w25 | c25 | w50 | c50 | w75 | c75 |
|---|---|---|---|---|---|---|
| 0 | 0.850 | −0.244 | 0.846 | 0.006 | 0.854 | 0.263 |
| 1 | 0.834 | −0.249 | 0.818 | 0.007 | 0.823 | 0.249 |
| 2 | 0.780 | −0.249 | 0.798 | 0.006 | 0.774 | 0.251 |
| 3 | 0.747 | −0.244 | 0.756 | 0.014 | 0.737 | 0.254 |
| 4 | 0.719 | −0.239 | 0.733 | 0.014 | 0.730 | 0.256 |
| 5 | 0.696 | −0.241 | 0.719 | 0.013 | 0.728 | 0.256 |
| 6 | 0.689 | −0.232 | 0.702 | 0.015 | 0.714 | 0.258 |
| 7 | 0.658 | −0.231 | 0.686 | 0.011 | 0.714 | 0.257 |
| 8 | 0.635 | −0.231 | 0.672 | 0.008 | 0.693 | 0.257 |
| 9 | 0.592 | −0.232 | 0.639 | 0.005 | 0.664 | 0.255 |
| 10 | 0.583 | −0.225 | 0.600 | −0.001 | 0.645 | 0.252 |
| 11 | 0.557 | −0.225 | 0.591 | 0.005 | 0.649 | 0.254 |
| 12 | 0.525 | −0.225 | 0.576 | 0.007 | 0.646 | 0.257 |
| 13 | 0.498 | −0.224 | 0.548 | 0.004 | 0.638 | 0.248 |
| 14 | 0.413 | −0.208 | 0.504 | 0.004 | 0.579 | 0.248 |
| 15 | 0.236 | −0.184 | 0.344 | 0.005 | 0.408 | 0.221 |
| 16 | 0.114 | −0.135 | 0.212 | 0.004 | 0.304 | 0.193 |
| 17 | 0.053 | −0.096 | 0.101 | 0.002 | 0.231 | 0.172 |
| 18 | 0.027 | −0.065 | 0.048 | 0.002 | 0.179 | 0.155 |
| 19 | 0.018 | −0.031 | 0.006 | 0.002 | 0.127 | 0.129 |
| 20 | 0.000 | 0.000 | 0.000 | 0.000 | 0.044 | 0.085 |
| 21–22 | 0 | 0 | 0 | 0 | 0 | 0 |

**Worked example.** Monday 12 Oct 2026, from Friday's close:

| | Expected range | P25–P75 | Kyōka "typical" now |
|---|---|---|---|
| NQ | 1.33% ≈ **413 pts** | 319–537 | 407 |
| ES | 0.73% ≈ **58 pts** | 45–75 | 75 |
| RTY | 1.19% ≈ **34 pts** | 27–43 | 41 |

- NQ's Friday was an inside day, which lifts its expectation.
- ES and RTY come off two quieter days and an up Friday.
