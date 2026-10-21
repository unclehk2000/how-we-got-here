# NQ Master Time & Price Probability Reference (v3)
**Dataset:** NQ futures, continuous contract (H/M/U/Z rolls handled), 1-min OHLC, full 24-hour electronic session
**Coverage:** January 2023 – August 2026, 833 full-quality RTH sessions, 4 independent calendar years
**New in v3:** electronic trading hours analysis, true day open, premarket dealing ranges, OR-based standard-deviation-style projections, consequent encroachment, weekly lookback, and a corrected 16-year NQ seasonal table (replacing the earlier weaker 3-4 year version)

---

# AXIS 5 — ELECTRONIC TRADING HOURS & PREMARKET STUDIES (NEW)

## 5.1 — Does the 7:00–9:00 AM ET Premarket Window Set the Day's High or Low?

Testing whether the day's ultimate extreme (7am–4:14pm ET combined) forms during the two-hour premarket window specifically, vs. during RTH itself. **n=833.**

| Question | Probability | 95% CI |
|---|---|---|
| Day's HIGH forms during 7-9am premarket | **20.6%** (172/833) | 18.0–23.5% |
| Day's LOW forms during 7-9am premarket | **24.2%** (202/833) | 21.5–27.3% |

**Full hour-by-hour breakdown of where the day's extreme actually forms (7am–5pm ET):**

| Hour | % contains day HIGH | % contains day LOW |
|---|---|---|
| 07:00 | 11.0% | 13.1% |
| 08:00 | 9.6% | 11.2% |
| **09:00** | 13.1% | 15.8% |
| 10:00 | 11.2% | 14.0% |
| 11:00 | 7.9% | 8.4% |
| 12:00 | 6.1% | 6.0% |
| 13:00 | 7.1% | 6.5% |
| 14:00 | 8.4% | 5.6% |
| **15:00** | **16.8%** | 12.2% |
| 16:00 | 8.8% | 7.1% |

**Read:** premarket (7-9am combined) accounts for roughly **1 in 5 daily highs and 1 in 4 daily lows** — genuinely significant, not negligible, but the single busiest individual hour for extremes is actually **9:00–10:00 AM** (the hour spanning the RTH open) for lows, and **3:00–4:00 PM** (the power hour) for highs. Premarket sets real, tradeable levels — it's not dominant, but it's far from irrelevant, and should be checked before the open rather than treated as noise.

## 5.2 — "True Day Open" (Midnight ET) vs. RTH 9:30 Open

Testing the ICT concept of a "true session open" at midnight ET against the conventional 9:30 RTH open, to see which better anchors the day's eventual direction. **n=828-830.**

| Finding | Result |
|---|---|
| Direction from midnight-open → 9:30-open matches direction from midnight-open → day's close | **67.0%** (555/828), CI: 63.8–70.1% |
| Day closes on the same side (up/down) of BOTH the midnight open and the RTH open | 84.6% (701/829), CI: 81.9–86.9% |
| Average distance between midnight open and 9:30 RTH open | 83.7 points |

**Read:** the midnight "true open" carries real, usable predictive information — where price sits relative to it by the 9:30 bell correctly anticipates the day's eventual close direction **67% of the time**, a genuinely useful edge on its own, and meaningfully better than a coin flip. Worth checking the midnight print alongside the standard 9:30 open, not instead of it — the two references usually agree (84.6% of days), but the 15.4% where they diverge are worth extra attention since that's exactly when the "official" open and the "true" open are telling different stories.

## 5.3 — Overnight Range: Consequent Encroachment (50% Retracement)

Testing whether price retraces to the midpoint of the full overnight range (prior day's 6pm ET close through the next day's 9:30am RTH open) at some point during that day's RTH session. **n=833.**

| Finding | Probability | 95% CI |
|---|---|---|
| Price retraces to the overnight range's 50% midpoint during RTH | **75.8%** (631/833) | 72.7–78.5% |

**Read:** this is one of the stronger, more dependable findings in this whole document — **roughly 3 in 4 trading days see price return to the midpoint of the overnight dealing range** at some point during the regular session. This gives real teeth to the "consequent encroachment" concept — the overnight range's 50% level is a genuinely high-probability magnet, not just a theoretical construct.

## 5.4 — Weekly Lookback: Does Price Trade Back Into the Prior Week's Range?

Testing whether each week's RTH price action trades back to touch the immediately prior week's high or low. **n=179 weeks.**

| Finding | Probability | 95% CI |
|---|---|---|
| Current week trades back into prior week's HIGH | **63.7%** (114/179) | 56.4–70.4% |
| Current week trades back into prior week's LOW | **38.0%** (68/179) | 31.2–45.3% |

**Read:** there's a real asymmetry here — prior week's **highs** get revisited nearly twice as often as prior week's **lows** (63.7% vs. 38.0%). Given NQ's overall uptrending character across most of this 2023-2026 sample, that skew makes directional sense (price more often grinds back up to test a prior high than back down to retest a prior low) — this stat would be worth re-checking specifically during any extended downtrending stretch to see if the asymmetry flips.

---

# AXIS 6 — OPENING RANGE (9:30–10:00 AM) AS A STATISTICAL PROJECTION TOOL

**Note: the Opening Range is defined as 9:30–10:00 AM ET (30 minutes), not 9:30–9:45 as used in earlier drafts of this document. All figures below reflect the corrected window.**

## 6.1 — Breakout Hold Rate (corrected)

| Finding | Probability | 95% CI |
|---|---|---|
| OR-high (9:30-10:00) break holds through the close | **82.0%** (223/272) | 77.0–86.1% |
| OR-low (9:30-10:00) break holds through the close | **70.0%** (159/227) | 63.8–75.6% |

This is meaningfully lower than the 9:30–9:45 version referenced elsewhere in this project — a wider 30-minute window absorbs more of the morning's early volatility into the range itself, so a genuine breakout beyond it is a somewhat stronger signal that happens less often, and holds slightly less reliably once it occurs, particularly on the downside (70.0% vs. the high side's 82.0%).

## 6.2 — OR Range as a Projection Unit

Testing whether the Opening Range can be used the way a standard deviation is used elsewhere — as a repeatable unit of measurement, projected as multiples (1x, 1.5x, 2x) beyond the OR high/low to forecast further targets for the rest of the session. **n=833.**

| Projection | Upside hit rate | Downside hit rate |
|---|---|---|
| **1.0x OR beyond the extreme** | 28.7% (239/833), CI 25.7–31.9% | 28.6% (238/833), CI 25.6–31.7% |
| **1.5x OR beyond the extreme** | 15.6% (130/833), CI 13.3–18.2% | 17.8% (148/833), CI 15.3–20.5% |
| **2.0x OR beyond the extreme** | 9.0% (75/833), CI 7.2–11.1% | 11.8% (98/833), CI 9.8–14.1% |

**Read:** with the corrected 30-minute window, this still behaves like a real decay curve — each additional half-to-full multiple of the OR range roughly halves the probability of the target being reached. Practically: **1x the OR range beyond its own high/low is reached a little under 3 times in 10 sessions**, **1.5x roughly 1 in 6**, and **2x is a genuine stretch target, hit only ~1 in 10 sessions**. These are meaningfully lower hit rates than the (incorrect) 9:30–9:45 version suggested — the wider 30-minute window captures more of the morning's early volatility inside the range itself, so breakouts beyond it are somewhat rarer and the multiple-based targets sit further from what's typically left in the day.

---

# AXIS 7 — TIME OF YEAR: CORRECTED 16-YEAR NQ SEASONAL TABLE

**This replaces the earlier 3-4 year NQ monthly seasonal test in v2, which was flagged there as too thin a sample to trust.** This version uses 16 full years (2010–2025) of NQ Dec-contract monthly total returns — the same rigor applied to the gold/silver seasonal work.

| Rank | Month | Avg return | t-stat | p-value | % positive years | Cohen's d | Significance |
|---|---|---|---|---|---|---|---|
| 1 | **July** | +292.0 | 2.91 | **0.011** | **94%** | 0.73 | ** |
| 2 | **November** | +301.5 | 2.29 | **0.037** | 75% | 0.57 | ** |
| 3 | May | +251.2 | 1.72 | 0.106 | 62% | 0.43 | not significant |
| 4 | June | +233.1 | 1.54 | 0.144 | 56% | 0.39 | not significant |
| 5 | October | +154.3 | 1.25 | 0.231 | 62% | 0.31 | not significant |
| — | Sep, Jan, Aug, Mar, Feb, Dec, Apr | small/negative | <1.0 | >0.4 | mixed | weak | not significant |

**Important correction from v2:** the earlier 4-year test (2023–2026 only) flagged **May and June** as the standout months. With the full 16-year sample now available, that read doesn't hold up as the strongest finding — **May and June are still positive on average but fail to clear statistical significance** (p=0.106 and p=0.144). Instead, **July and November are the two genuinely significant months** (p<0.05 both), with **July standing out sharply — positive in 15 of 16 years (94%)**, the single most consistent monthly seasonal pattern found anywhere in this entire project, gold/silver included.

**Why this matters methodologically:** this is a direct, concrete demonstration of exactly the risk flagged in v2 — a small sample (n=3-4) produced a seemingly clean, low-p-value result (May/June) that a much larger sample (n=16) does not support as the top finding. May and June aren't wrong, exactly — they're just weaker than they looked, and July/November were hiding underneath a thin sample the whole time. This is the reason multi-year, high-n testing matters more than an appealing pattern at low n.

---

# UPDATED POSITIONING CHECKLIST (v3 additions)

### Overnight / Premarket (before 9:30)
- [ ] Note the overnight range (prior 6pm close → current premarket) — there's a **75.8% chance price revisits its 50% midpoint** at some point during today's RTH session; this is one of the strongest, most dependable levels in the entire framework
- [ ] Check price relative to the midnight ET "true open" — where price sits versus this level by 9:30 correctly anticipates the day's close direction **67% of the time**
- [ ] The 7-9am premarket window has a genuine ~21-24% chance of containing the day's eventual high or low — don't dismiss premarket price action as noise, but don't over-weight it either; RTH's own 9-10am and 3-4pm hours are still more likely to contain the extreme

### 9:30-10:00 (Opening Range) — now with projection targets
- [ ] Once the OR (9:30-10:00) is set, use it as a projection unit: **~29% odds of reaching 1x the OR range beyond its own high/low**, **~16-18% odds at 1.5x**, **~9-12% odds at 2x** — scale target expectations accordingly rather than guessing at arbitrary point levels

### Weekly context
- [ ] At the start of each week, mark the prior week's high and low — expect the **high to get revisited ~64% of the time**, the **low only ~38%** (asymmetry consistent with the broader uptrend across this dataset; re-check this ratio if the market enters a sustained downtrend)

### Time of year
- [ ] **July and November carry the only two statistically significant monthly seasonal tendencies found in the full 16-year NQ dataset** — July in particular has been positive in 15 of the last 16 years. Treat both as a real, historically-earned tailwind, not just a heatmap pattern.
- [ ] May and June, despite looking attractive in shorter samples, do not clear statistical significance across the full history — treat any bullish May/June bias as a mild lean at most

---
*All confidence intervals are 95% Wilson score intervals (proportions) or standard t-tests (monthly returns). Axis 5 and 6 are new single-pass results on the pooled 4-year dataset — not yet cross-validated year-by-year the way Axis 1 was in v2; treat with the same caution as Axis 2/3 until re-tested individually per year.*
