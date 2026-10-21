# NQ Master Time & Price Probability Reference (v2)
**Dataset:** NQ futures, continuous contract (H/M/U/Z rolls handled), 1-min OHLC
**Coverage:** January 2023 – August 2026, **833 full-quality RTH sessions** across 4 independent calendar years
**Method:** All figures computed directly from real OHLC data. Every multi-year stat below has been cross-validated year-by-year, not just pooled blindly — where years disagree, that's called out explicitly.

---

## How to Read This Document

Four separate axes are covered, and they answer different questions:

1. **Time of Day** — where in the trading session do specific behaviors cluster (most mature, most validated)
2. **Day of Week** — does Monday behave differently than Thursday (new, single-pass on pooled data)
3. **Time of Year** — do specific months carry a real seasonal lean (newest, smallest per-bucket sample — treat cautiously)
4. **Time + Price Combined** — probabilities that tie a *when* to a *how far* (gap fills, OR targets, NDOG/NWOG)

---

# AXIS 1 — TIME OF DAY
*Cross-validated across all 4 years independently before pooling*

## Tier 1 — Strongest, most reliable (stable across all 4 years)

| Finding | 2023 | 2024 | 2025 | 2026 | 4-yr pooled |
|---|---|---|---|---|---|
| OR-high (9:30-9:45) break holds through close | 88.3% | 88.7% | 83.1% | 90.3% | **~88%** |
| OR-low break holds through close | 70.5%* | 84.3% | 87.9% | 83.3% | ~82% |
| 10:00–10:30 confirmed reversal (≥40pt) occurs | 33.2% | 35.4% | 32.1% | 30.6% | **~33%** |
| Morning-range (9:30-11:30) vs full-day-range correlation | r=0.605 | r=0.681 | r=0.733 | r=0.783 | rising trend — see note |

*2023's OR-low hold rate (70.5%) is the one real outlier in this table — its confidence interval (55.8–81.8%) still technically overlaps the other years, but it's worth remembering this isn't a guaranteed >80% number every year.

**Note on the morning-range correlation:** this is the one metric that moved in the same direction all four years in a row (0.605 → 0.681 → 0.733 → 0.783). That monotonic pattern across independent years is unusual enough to flag as a possible genuine drift (e.g., changing market structure or participation) rather than noise — worth re-checking once 2027 data exists.

**10:00–10:30 reversal probability is the most stable single number in this entire project** — every year landed within a 5-point band (30.6% to 35.4%) despite very different overall market regimes across 2023-2026.

## Tier 2 — Solid, moderate reliability

| Finding | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| First-10-min (9:30-9:40) direction persists to close | 59.0% | 55.8% | 64.4% | 68.6% |
| Median % of day's total range made by 11:30 AM | 73.3% | 72.9% | 72.9% | 79.8% |
| Lunch-hour (12-1pm) reversal of morning trend | 28.9% | 28.7% | 36.3% | 45.8% |

**Important pattern-check, not a finding to trust blindly:** first-10-min persistence and lunch-hour reversal both looked like they were climbing steadily 2024→2025→2026 — but 2023 breaks that trend (59.0% and 28.9%, both close to 2024's lower numbers, not continuing a rise). **Conclusion: that "steady climb" was not a real multi-year drift** — it only appeared because the first three years happened to be sampled in an ascending order. This is exactly the kind of false pattern more data is supposed to catch, and it did.

## Tier 3 — Weaker, contextual only
- Opening-range/macro-window volatility bumps at 9:50-10:10 and 10:50-11:10 (from earlier single-year testing — not yet re-validated across all 4 years)
- Which hour contains the day's high/low (9:00-10:00 hour most common for both, single-year test)

## Tier 4 — Null / not usable
- Power hour (3-4pm) trend continuation: ~47%, coin flip, no edge
- The "10:16 AM" specific-minute pattern: real at small samples, dissolved into a broad 10:00-10:24 lean at full sample — do not treat as a sharp-minute signal

---

# AXIS 2 — DAY OF WEEK
*Pooled 2023-2026, n=833 sessions. This axis has not yet been cross-validated year-by-year the way Axis 1 was — treat as a first-pass, real but less battle-tested finding.*

| Day | n | Avg range | Avg net move | % up days | OR-up hold | OR-down hold | 10-10:30 reversal rate |
|---|---|---|---|---|---|---|---|
| **Monday** | 158 | 270 pts | **+36.2** | **60%** | 81% | 69% | 29.1% |
| Tuesday | 175 | 279 pts | +18.9 | 59% | 95% | 83% | 33.7% |
| Wednesday | 174 | 303 pts | +11.9 | 52% | 90% | 89% | 33.9% |
| **Thursday** | 169 | **314 pts** | **-27.4** | 49% | 86% | 80% | 30.8% |
| Friday | 157 | 293 pts | +2.0 | 58% | 85% | 85% | **38.2%** |

**Key reads:**
- **Monday and Thursday are near-mirror opposites.** Monday is the most consistently bullish day (60% of Mondays close up, largest average net gain). Thursday is the *only* net-negative day on average, despite having the widest range of the week — meaning Thursday tends to see big moves that skew down more often than they resolve up.
- **Friday stands out for its reversal rate** (38.2% vs. 29-34% the other four days) — the 10:00-10:30 reversal setup appears meaningfully more reliable heading into a Friday session than any other day.
- **Tuesday and Wednesday have the highest OR-breakout hold rates of the week** (95% and 90% on the up side) — if you're looking for the OR-breakout setup specifically, midweek sessions show the cleanest follow-through in this sample.

**Caveat:** this is a single pooled pass across 4 years, not cross-validated year-by-year like Axis 1. Before treating any single day's numbers as load-bearing, it would be worth re-running this broken out by year to confirm Monday/Thursday's divergence holds in each individual year rather than being driven by one unusual year in the pool.

---

# AXIS 3 — TIME OF YEAR (Monthly Seasonality)

**This is the newest and thinnest axis in this document — read the sample sizes carefully before weighting anything here.**

| Rank | Month | Years | Avg return | t-stat | p-value | % positive |
|---|---|---|---|---|---|---|
| 1 | **May** | n=4 | +7.66% | 9.28 | **0.003** | 100% |
| 2 | **June** | n=4 | +5.44% | 3.31 | **0.045** | 100% |
| 3 | January | n=3 | +4.13% | 1.70 | 0.232 | 100% |
| — | Aug, Nov, Apr, Dec, Sep, Feb, Jul, Oct, Mar | n=3-4 each | mixed, small | <1.0 | >0.4 | mixed |

**Raw year-by-year values for the two flagged months:**
- May: 2023 +7.5%, 2024 +6.2%, 2025 +7.0%, 2026 +10.0% — positive and tightly clustered every year
- June: 2023 +7.2%, 2024 +6.7%, 2025 +7.4%, 2026 +0.5% — positive every year, but 2026 notably weaker than the other three

**Why the low p-values here deserve real skepticism, not celebration:** with only 3-4 data points per month, a t-test can produce a small p-value just from a small sample happening to line up consistently — this is a fundamentally weaker statistical basis than the gold/silver seasonal work, which had **16 years per month** and still only found 2 months (August, January) that cleared significance. Treat May and June here as a **real, worth-monitoring directional lean with unusually tight historical consistency**, not a validated statistical edge on the level of the Axis 1 findings. This needs several more years of data before it earns the same trust.

**What is genuinely notable regardless of the p-values:** the *consistency* of direction (4-for-4 positive in both May and June, across very different overall market years) is worth tracking, even while the formal significance test stays unconvincing at this sample size.

---

# AXIS 4 — TIME + PRICE COMBINED PROBABILITIES

## Opening Range Targets & Continuation
| Finding | Probability |
|---|---|
| Gap fades (moves against gap direction) by 10:30 AM | 63.2% |
| 50% gap-continuation target hit (projected from open, gap direction) | 63.9% |
| 100% gap-continuation target hit | 38.6% |
| — Down gaps specifically (half / full target) | 70.0% / 40.0% |
| — Up gaps specifically (half / full target) | 58.1% / 37.2% |

## Gap Fill Probabilities
| Gap type | Definition | Within 1 day | Within 2-3 days |
|---|---|---|---|
| Full RTH gap fill | Prior 4:15pm close → next open | 31.6% | — |
| 50% RTH gap fill | Retrace to gap midpoint | 52.6% | — |
| **NDOG** (5pm-6pm ET daily break) | 17:00 close → 18:01 close | 92.2% | 95.3% |
| **NWOG** (Friday→Sunday weekly gap) | Fri 17:00 → Sun 18:01 | 95.7% | **100%** (n=23) |
| NDOG touched specifically in first 30 min of RTH | — | 32.8% | — |
| NWOG touched specifically in first 30 min of RTH (Monday) | — | **56.5%** | — |

**Key takeaway:** NWOG is the more "magnetic" level for the 9:30-10:00 opening drive specifically — over half of weekly gaps get touched in that window, versus roughly a third for the smaller daily NDOG.

## Lunch Hour (12:00-1:00pm)
| Finding | Probability |
|---|---|
| Reversal of morning trend | 45.8% (2026) / ranges 28.7-45.8% across years — see Axis 1 |
| Narrow consolidation (range <70% of typical hour) | 38.3% |
| Either reversal or consolidation | 69.2% |

---

# POSITIONING CHECKLIST (Updated for 4-Year Validated Data)

### Pre-market
- [ ] Check the day of week — Monday and Friday carry the strongest directional/reversal tendencies (Axis 2); Thursday warrants extra caution given its negative average net move despite wide range
- [ ] Check the calendar month — May and June carry a historically consistent (though not yet statistically proven) bullish lean; treat as a soft tailwind, not a standalone signal
- [ ] Note last night's NDOG — 92%+ odds it's already filled; if not, it's a live reference level
- [ ] On Sundays/Mondays: note Friday's NWOG — 95-100% odds it fills within 3 days; if untouched by Monday's open, it's a high-value level given the 56.5% chance it gets tagged in the first 30 minutes of RTH

### 9:30-9:45 (Opening Range)
- [ ] Mark the OR high/low — this is still your single strongest, most cross-validated edge (83-90% hold rate across all 4 years)
- [ ] Tuesday/Wednesday sessions have shown the cleanest OR-breakout follow-through of the week; treat Monday's OR-down-hold rate (69%) as comparatively less reliable

### 9:45-11:30 (Reversal / Distribution)
- [ ] The 10:00-10:30 reversal probability (~33%) is the most stable number in this whole project — real, but still means roughly 2 in 3 days do NOT produce a confirmed reversal in this window
- [ ] By 11:30, expect ~73-80% of the day's total range to already be made (Axis 1) — size and target expectations accordingly

### 12:00-1:00 (Lunch)
- [ ] Expect reversal-or-consolidation roughly 7 in 10 days — this is not the window to add trend-following size

### End of week
- [ ] Friday shows the highest 10:00-10:30 reversal rate of any weekday (38.2%) — worth extra attention if a morning setup is developing

---
*All confidence intervals are 95% Wilson score intervals (proportions) or standard t-tests (monthly returns) unless noted. Re-run and expand as more years/data become available — Axis 2 and Axis 3 especially would benefit from the same year-by-year cross-validation already applied to Axis 1.*
