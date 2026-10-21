# NQ Calendar Structure: Quarterly, Monthly & Day-of-Month
**Benchmark dataset:** 2023–2026, **833 RTH sessions**, held constant for all comparisons
**Purpose:** identify calendar-based characteristics in volatility and directional bias, with multiple-comparison correction where applicable

---

## HEADLINE FINDING

**The first half of the month is significantly more bullish than the second half.**

| Window | n | Avg range | Avg net % | % up days | p-value |
|---|---|---|---|---|---|
| **Days 1–15** | 426 | 301 pts | **+0.163%** | **60.3%** (CI 56–65) | **0.005** |
| Days 16–31 | 407 | 283 pts | −0.043% | 50.6% (CI 46–55) | 0.370 |

**Difference between halves: t=2.74, p=0.006.**

This is a ~10 percentage point gap in up-day frequency on a large sample, and the direct comparison test between the two halves clears significance comfortably. The first half of the month shows a real positive drift; the second half is a coin flip.

**Plausible mechanism:** retirement contributions, payroll-driven fund inflows, and systematic allocation flows concentrate early in the month. This is a widely-discussed effect and it shows up clearly here.

**Caveat worth stating:** 2023–2026 was net bullish overall, so some of this is the ambient uptrend. The meaningful part is the *asymmetry* — if the trend alone explained it, both halves would drift up roughly equally. They don't.

---

# PART 1 — QUARTERLY CHARACTERISTICS

| Quarter | n | Avg range | Avg net | % up days | Avg net % | t | p |
|---|---|---|---|---|---|---|---|
| Q1 | 208 | 282 | +7.4 | 53.4% | +0.077% | 1.06 | 0.290 |
| **Q2** | 241 | **318** | **+37.6** | **59.8%** | **+0.199%** | **2.38** | **0.018** |
| Q3 | 221 | 284 | −13.3 | 53.8% | −0.055% | −0.88 | 0.380 |
| Q4 | 163 | 277 | −5.3 | 54.6% | +0.002% | 0.02 | 0.983 |

**Q2 is the only quarter with a statistically significant directional bias** (p=0.018) — and it's also the widest-range quarter (318 pts avg). Both the biggest moves and the clearest upward drift land in April–June.

**Q3 and Q4 are directionally flat.** Neither comes close to significance. Q4 in particular is almost perfectly neutral (avg net +0.002%), which cuts against the common "Santa rally / strong Q4" assumption — at least across these four years.

## Setup stability across quarters — OR (9:30–10:00) breakout

| Quarter | OR-up hold | OR-down hold |
|---|---|---|
| Q1 | 85.5% (53/62) | 68.5% (37/54) |
| Q2 | 78.4% (69/88) | 67.9% (36/53) |
| Q3 | 74.2% (46/62) | **74.3%** (52/70) |
| Q4 | **91.7%** (55/60) | 68.0% (34/50) |

**The OR breakout works in every quarter** — the range is 74–92% upside, 68–74% downside, with no quarter breaking down. Q4's 91.7% upside figure is the standout but rests on n=60, so treat the precision loosely.

Note that **Q3 is the only quarter where downside breaks match upside breaks** (74.3% vs 74.2%) — consistent with Q3 being the one quarter with a slightly negative drift.

---

# PART 2 — MONTHLY CHARACTERISTICS

| Month | n | Avg range | Avg net % | % up days | t | p | Sig |
|---|---|---|---|---|---|---|---|
| Jan | 61 | 245 | +0.166 | 52.5% | 1.36 | 0.179 | |
| Feb | 68 | 268 | +0.092 | 58.8% | 0.74 | 0.459 | |
| Mar | 79 | 322 | −0.006 | 49.4% | −0.04 | 0.965 | |
| Apr | 79 | **374** | +0.279 | 55.7% | 1.28 | 0.203 | |
| **May** | 85 | 255 | **+0.189** | **61.2%** | **2.52** | **0.014** | ** |
| Jun | 77 | 331 | +0.129 | 62.3% | 1.16 | 0.251 | |
| **Jul** | 83 | 306 | **−0.166** | 49.4% | −1.78 | 0.079 | * |
| Aug | 80 | 298 | +0.036 | 53.8% | 0.29 | 0.769 | |
| Sep | 58 | 236 | −0.022 | 60.3% | −0.22 | 0.829 | |
| Oct | 68 | 274 | −0.061 | 50.0% | −0.52 | 0.602 | |
| Nov | 57 | 288 | +0.092 | 59.6% | 0.72 | 0.475 | |
| Dec | 38 | 264 | −0.022 | 55.3% | −0.14 | 0.890 | |

## Volatility ranking (avg daily range)

| Rank | Month | Range | | Rank | Month | Range |
|---|---|---|---|---|---|---|
| 1 | **April** | 374 | | 7 | October | 274 |
| 2 | June | 331 | | 8 | February | 268 |
| 3 | March | 322 | | 9 | December | 264 |
| 4 | July | 306 | | 10 | May | 255 |
| 5 | August | 298 | | 11 | January | 245 |
| 6 | November | 288 | | 12 | **September** | 236 |

**April is the most volatile month by a clear margin** (374 vs 331 for second place) — 58% wider than the quietest month, September.

**Volatility and direction are decoupled at the monthly level.** May is the *only* significantly bullish month (p=0.014) yet ranks 10th of 12 in volatility. April is the widest month but statistically directionless (p=0.203). Range tells you how much is available, not which way it goes — the same conclusion reached in the midterm-year analysis.

## Important conflict with the 16-year seasonal data

The 16-year NQ seasonal table (2010–2025) identified **July and November** as the only statistically significant months, with **July positive in 15 of 16 years**.

This 4-year benchmark shows **July as the most *negative* month** (−0.166%, p=0.079) — the opposite sign.

**How to reconcile these honestly:** the 16-year sample is far more reliable for seasonality. Four years is not enough to establish a monthly pattern — this benchmark's July figure is drawn from just 83 sessions across 4 Julys. The correct read is that **the 16-year data is authoritative on seasonality, and this table is authoritative on the *volatility ranking and daily character* of the benchmark period**. Do not use the 4-year monthly direction column as a seasonal guide; it is included here for internal comparison, not forecasting.

This is the same lesson that already surfaced twice in this project (the 10:16 minute, the May/June seasonal claim): short samples produce confident-looking monthly signals that longer samples overturn.

---

# PART 3 — DAY OF MONTH

Testing all 31 calendar days for directional bias:

| Day | n | Avg range | Avg net % | % up | p | Raw sig |
|---|---|---|---|---|---|---|
| 2 | 27 | 324 | +0.488 | **74.1%** | 0.024 | ** |
| 11 | 30 | 286 | +0.355 | **73.3%** | 0.044 | ** |
| 14 | 29 | 262 | +0.332 | **72.4%** | 0.019 | ** |
| 13 | 32 | 276 | +0.304 | 65.6% | 0.062 | * |
| 18 | 27 | 271 | −0.278 | 40.7% | 0.167 | |
| 29 | 23 | 299 | −0.020 | 39.1% | 0.921 | |

*(full 31-day table computed; only notable rows shown)*

## The multiple-comparison check

| Metric | Result |
|---|---|
| Tests run | 31 |
| Bonferroni threshold | p < 0.0016 |
| Raw p<0.05 hits | 3 |
| **Expected by chance alone** | **~1.6** |
| **Surviving correction** | **0** |

**No calendar day survives correction.** Three days crossed the naive threshold, but 1.6 are expected purely by chance across 31 tests — so finding 3 is entirely unremarkable.

**Verdict: there is no tradeable day-of-month directional effect.** Days 2, 11, and 14 look impressive at 72–74% up rates, but each rests on fewer than 32 observations and none survives correction. Treating them as edges would be exactly the error this project has already caught twice.

## Trading-day-of-month (position within the month, not calendar date)

| TD | n | Avg range | Avg net % | % up | p |
|---|---|---|---|---|---|
| TD1 | 38 | 329 | +0.059 | 55.3% | 0.773 |
| TD2 | 38 | 294 | +0.295 | 65.8% | 0.056 |
| TD3 | 38 | 260 | +0.303 | 63.2% | 0.033 |
| TD9 | 38 | 268 | +0.341 | 65.8% | 0.020 |
| TD-1 (last) | 38 | 308 | +0.120 | 52.6% | 0.458 |
| TD-2 | 38 | 298 | −0.171 | 42.1% | 0.355 |

**Same caution applies** — TD3 and TD9 clear raw p<0.05, but with 17 tests run the expected chance hits are ~0.85, so 2 hits is only marginally above noise, and neither would survive correction.

**What is worth noting directionally:** TD2, TD3, TD5, TD6, TD7, TD9, TD10 all show positive average returns with 63–68% up rates, while TD11 and TD12 turn negative (44.7% up both). That's a consistent *shape* — early-month strength fading around the second week — which supports the month-half finding above even though no individual day is significant on its own.

**The month-half split is the statistically defensible version of this pattern.** Individual days are noise; the aggregated first-half vs second-half comparison (p=0.006, n=833) is real.

---

# PART 4 — MONTH-END AND QUARTER-END

| Window | n | Avg range | Avg net % | % up | p |
|---|---|---|---|---|---|
| Quarter-end (last 3 days of Mar/Jun/Sep/Dec) | 33 | 287 | +0.103 | 54.5% | 0.554 |
| Month-end (last 3 days, non-quarter months) | 81 | 298 | −0.035 | 45.7% | 0.767 |

**No month-end or quarter-end effect found.** Neither window shows a significant directional bias, and neither shows elevated volatility relative to the 833-session average (~295 pts). The commonly-cited "quarter-end rebalancing" effect does not appear in this data at the daily level.

---

# SUMMARY — WHAT'S ACTUALLY USABLE

### Real and statistically supported
1. **First half of month > second half** — 60.3% vs 50.6% up days, p=0.006. The strongest calendar finding here.
2. **Q2 directional bias** — only quarter clearing significance (p=0.018), also the widest-range quarter
3. **April is the most volatile month** (374 pts avg), September the quietest (236 pts) — a 58% spread useful for sizing and target expectations
4. **OR breakout is quarter-stable** — 74–92% upside, 68–74% downside, works in all four quarters

### Not usable
5. **Day-of-month effects** — zero survive multiple-comparison correction
6. **Trading-day-of-month effects** — same, though the aggregate shape supports finding #1
7. **Month-end / quarter-end** — no effect detected
8. **This benchmark's monthly direction column** — conflicts with the 16-year seasonal data; defer to the longer sample

### Methodological note
This analysis ran 31 day-of-month tests, 17 trading-day tests, and 12 monthly tests. Without correction, roughly 3 of those 60 would appear "significant" from chance alone — and roughly that many did. Correction was applied to the day-level tests, and the conclusion is that no daily calendar effect is real. The month-half finding survives precisely because it aggregates rather than slices.

---
*All confidence intervals are 95% Wilson score intervals; monthly and daily directional tests are one-sample t-tests on daily open-to-close percentage returns. Bonferroni correction applied to day-of-month family. Benchmark held constant at 833 sessions, Jan 2023 – Aug 2026.*
