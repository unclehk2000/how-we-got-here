# NQ Time & Price Probability Reference Sheet
**Dataset:** NQ futures (NQH→NQM→NQU, contract rolls handled), 1-min OHLC, Feb 13 – Jul 31, 2026, ET
**Sample size:** 107–111 full RTH sessions (varies slightly by test — noted per row)
**Method:** All numbers below are computed directly from real OHLC data, not estimated or eyeballed, unless marked otherwise.

---

## TIER 1 — Strongest, most reliable findings
(Tight confidence intervals, large effect size, held up across resampling)

| Finding | Probability | 95% CI | n |
|---|---|---|---|
| Opening Range (9:30–9:45) breakout **up** holds through close | **92.3%** | 75.9–97.9% | 26 |
| Opening Range (9:30–9:45) breakout **down** holds through close | **78.9%** | 56.7–91.5% | 19 |
| First 10-min direction (9:30–9:40) matches full-day close direction | **67.3%** | 57.9–75.4% | 107 |
| — when first 10-min is UP | 72.5% | — | 51 |
| — when first 10-min is DOWN | 62.5% | — | 56 |
| Morning range (9:30–11:30) correlates with full-day range | **r = 0.774** | — | 107 |
| Median % of day's total range already made by 11:30 AM | **79.3%** | — | 107 |
| Gap fades (moves against gap direction) by 10:30 AM | **63.2%** | — | 19 |

---

## TIER 2 — Solid, usable, moderate sample
| Finding | Probability | 95% CI | n |
|---|---|---|---|
| 50% gap-continuation target hit (measured from open, gap direction) | **63.9%** | 53.1–73.4% | 83 |
| 100% (equal-size) gap-continuation target hit | **38.6%** | 28.8–49.3% | 83 |
| — DOWN gaps: half target / full target | 70.0% / 40.0% | — | 40 |
| — UP gaps: half target / full target | 58.1% / 37.2% | — | 43 |
| 50% gap-fill probability (retrace to midpoint of gap) | **52.6%** | — | 19 |
| Full gap-fill probability (retrace to full prior close) | **31.6%** | — | 19–20 |
| Lunch hour (12–1pm): reversal OR consolidation occurs | **69.2%** | 59.9–77.1% | 107 |
| — reversal of morning trend specifically | 45.8% | 36.7–55.2% | 107 |
| — narrow consolidation specifically | 38.3% | 29.7–47.8% | 107 |
| Large-vol first 30-min → wider day (513 vs 412 pt avg) | directional lean | — | 107 |
| Large morning range → large afternoon range (clustering, not reversion) | 315 vs 191 pt avg | — | ~70 |

---

## TIER 3 — Real but weak / regressed with more data
| Finding | Probability | 95% CI | n |
|---|---|---|---|
| 10:00–10:30 AM: confirmed reversal (≥40pt) occurs somewhere in window | **30.6%** | 22.8–39.7% | 111 |
| — of those, lands in 10:15–10:21 sub-window | 35.3% of reversals (~11% of all days) | — | 34 |
| — direction split | 16 tops / 18 bottoms (~even) | — | 34 |
| Day's session LOW forms in the 9:00–10:00 hour | 37.4% (most common hour) | — | 107 |
| Day's session HIGH forms in the 9:00–10:00 hour | 23.4% (most common hour) | — | 107 |
| Thursday = widest avg daily range (496 pts) | descriptive only | — | 21/day |

## TIER 4 — Null / not usable
- **Power hour (3–4 PM) trend continuation:** 46.7% — essentially a coin flip, no edge
- **Lunch hour = single quietest hour of day:** only 16.8% — lunch is *subdued*, not usually the quietest hour outright
- **"10:16 AM" as a specific minute:** was 64% of reversals at n=14, regressed to 35% at n=111 — treat as **debunked as a sharp-minute pattern**, real only as a soft 10:00–10:24 lean

---

## NDOG / NWOG — Overnight & Weekly Gap Fill Rates

**Definition used:** gap = price at 17:00 ET (close of last bar before the daily break) vs. price at 18:01 ET (close of the first bar after reopen). Fill = first later bar that re-enters the gap zone **after** price has genuinely left it (avoids false "instant fill" from adjacent-bar overlap).

**NDOG (New Day Opening Gap)** = the daily 5:00–6:00 PM ET maintenance-break gap. **n=64 real gaps ≥10pts.**

| Window | Fill probability | 95% CI |
|---|---|---|
| Within 1 trading day | **92.2%** (59/64) | 83.0–96.6% |
| Within 2 trading days | **95.3%** (61/64) | 87.1–98.4% |
| Within 3 trading days | 95.3% (unchanged) | 87.1–98.4% |
| Left zone, never refilled | 4.7% (3/64) | — |

Avg NDOG size: ~30 pts. Fill timing varies widely — anywhere from a few minutes to several hundred minutes later; not exclusively an instant-fill phenomenon.

**NWOG (New Week Opening Gap)** = the Friday-close-to-Sunday-reopen weekly gap. **n=23 real gaps ≥10pts.**

| Window | Fill probability | 95% CI |
|---|---|---|
| Within 1 trading day | 95.7% (22/23) | 79.0–99.2% |
| **Within 2–3 trading days** | **100.0%** (23/23) | 85.7–100.0% |
| Left zone, never refilled | 0% | — |

Avg NWOG size: ~198 pts — much larger than NDOG, as expected from weekend risk accumulation. Every NWOG in this sample filled within 3 trading days; realistic true rate (given n=23) is more like 86–100%.

**Bottom line:** both gap types fill the large majority of the time, and NWOG specifically is close to a lock within 3 days. The more useful open question now is *how far price extends beyond the gap first*, and whether it makes a new high/low before returning — not yet tested.

---

## FIRST-HOUR FRAMEWORK (9:30–12:30 ET): Structure + Liquidity, Mapped to Your Actual Data

The general idea behind "Power of Three" is simple: a trading range typically moves through three phases — an initial **accumulation** (tight range, position-building), a **manipulation** move (a fake-out that runs one side's resting stops before reversing), and then the **distribution** move (the real directional trend for the session). The theory says the manipulation leg is designed to run "liquidity" — clusters of resting stop orders sitting just beyond an obvious high or low (buy-side liquidity above old highs, sell-side liquidity below old lows) — before price turns and moves the other way.

That's the general framework as commonly taught. Below is how it actually maps onto **your** validated numbers, phase by phase, so you're not trading the theory blind — you're trading the version of it your own data supports.

### Phase 1 — Accumulation: 9:30–9:45 (Opening Range)
- This is your Opening Range. Mark the high and low of this 15-minute window.
- **Data-backed:** a clean break of only one side of this range (not both) holds through the close **92.3%** of the time on the upside, **78.9%** on the downside. This is your strongest edge in the entire dataset — treat the OR itself as the accumulation zone.
- Don't take directional size yet. This window is for marking levels, not entering.

### Phase 2 — Manipulation / Liquidity Run: roughly 9:45–10:10
- **Data-backed:** the 9:50–10:10 stretch shows genuinely elevated range (157% of a typical 20-min window) — this is the most volatile 20 minutes of your whole session, confirmed independently of the "macro" framework.
- **Data-backed:** the first 10 minutes' direction (9:30–9:40) carries 67.3% persistence for the full day — but a move that immediately reverses *through* the OR boundary in this 9:45–10:10 window is a classic liquidity-run signature: price briefly runs stops beyond the OR high or low, then snaps back inside.
- **How to read it:** if price breaks the OR high, runs a bit further, then closes back inside the OR within this window — that's your manipulation leg. The buy-side liquidity above the OR high just got swept. Same logic in reverse for a break below the OR low sweeping sell-side liquidity.
- **Caution, stated plainly:** your dedicated 10:00–10:30 reversal test only found a confirmed reversal ~31% of the time, and the sharp "10:16 minute" story didn't survive more data. So don't force a reversal read here if price simply breaks and holds — that's the OR-breakout case above (92%/79%), not a liquidity run. The two setups look similar in the first few minutes; the distinguishing signal is whether price closes back inside the OR or holds beyond it.

### Phase 3 — Distribution: roughly 10:10–11:30
- **Data-backed:** by 11:30 AM, the median day has already made **79.3%** of its entire day's range (r=0.774 correlation between morning range and full-day range). This is your real distributional move — the trend that actually determines the character of the day.
- **Data-backed:** the 10:50–11:10 window shows a secondary, smaller volatility bump (118% of baseline) — a reasonable spot to look for continuation or a final push of the morning trend.
- If Phase 2 was a genuine liquidity sweep (price ran one side and reversed), Phase 3 is where that reversal is statistically expected to actually develop and extend.

### Phase 4 — Late morning / lunch approach: 11:30–12:30
- **Data-backed:** the 12:00–1:00 lunch hour sees a reversal or consolidation against the morning trend **69.2%** of the time. If you're holding a Phase 3 distribution move into lunch, expect it to stall or pull back — this is not the window to add size expecting clean continuation.
- Treat 12:30 as a natural point to reassess: has the day's range likely already been made (per the 79% stat), and is lunch-hour chop starting to show up?

### How to actually attack buy-side / sell-side liquidity, using only what's confirmed
1. Mark the OR (9:30–9:45) high and low.
2. Watch 9:45–10:10 for a break-and-reverse of either OR boundary (the liquidity sweep signature) vs. a break-and-hold (the OR-breakout signature). These require different responses — don't conflate them.
3. If it's a sweep: the higher-probability trade is fading back toward the opposite side of the OR, expecting the Phase 3 distribution move to follow through on the reversal.
4. If it's a hold: trust the OR-breakout stat (92%/79%) and expect continuation, not reversal.
5. Use the gap-fade tendency (63.2% of gaps fade by 10:30) as a confluence check — a gap day fading into the OR-reversal scenario is a stronger combined signal than either alone (not independently tested for interaction effect, but directionally consistent).
6. By 11:30, size down / take profit awareness — most of the day's range is statistically already spent.
7. Expect lunch-hour chop 12:00–1:00 regardless of how clean the morning trend looked.

**What's genuinely proven vs. what's framework/theory here, stated plainly:** the OR-breakout hold rates, the 9:50–10:10 and 10:50–11:10 volatility bumps, the morning-range/day-range correlation, and the lunch-hour reversal rate are all real, tested numbers from your data. The "liquidity sweep causes the reversal" causal story is the general framework's interpretation, not something this dataset can prove or disprove directly — what your data *can* confirm is that a break-and-reverse pattern in the 9:45–10:10 window coincides with elevated volatility and precedes the session's largest directional move (10:10–11:30). Treat the mechanism as a reasonable working theory, and the timing/volatility windows as the tested part.

---

# POSITIONING CHECKLIST

Use this top-down each morning. Stop and downgrade confidence at any step that fails.

### 1. Pre-market (before 9:30)
- [ ] Check for CPI / NFP on the calendar — if today is one, treat all Tier 1–3 stats as unreliable; this is event-driven, not pattern-driven, price action
- [ ] Note last night's NDOG (5pm-6pm ET gap) — 91%+ odds it's already filled by morning; if not, it's a live level to watch
- [ ] On Sundays/Mondays: note the NWOG from Friday's close — 91-96% odds it fills within 3 trading days; unfilled NWOGs are high-value reference levels
- [ ] Note the RTH gap: prior 4:15pm close vs. current pre-market price
- [ ] Note first-30-min pre-market volume trend if visible — elevated volume is a lean toward a wider day

### 2. First 15 minutes (9:30–9:45) — Opening Range
- [ ] Mark the OR high/low
- [ ] Note first-10-minute (9:30–9:40) directional bias — this has a **67% chance of holding for the full day**
- [ ] If gap ≥50pts: note direction, this sets your gap-fade/continuation framework for the morning

### 3. 9:45–10:30 — Confirmation window
- [ ] Did price cleanly break the OR high or OR low (not both)? If yes: **~80–92% odds it holds into the close** — this is your strongest single signal
- [ ] Is the gap fading (63% base rate) or continuing (37%)? Align with the OR break if possible
- [ ] Don't over-trade a specific reversal window — the 10:00–10:30 "reversal" edge is weak (~31%) and the old 10:16 minute pattern didn't hold up; don't anchor to a specific minute

### 4. By 11:30 AM — Range assessment
- [ ] Compare the range made so far to a typical full-day range — statistically, **~80% of the day's total range is already established by now**
- [ ] If the morning range was small, expect the afternoon to likely stay small too (volatility clusters, doesn't mean-revert intraday)
- [ ] If the morning range was large, expect a wider-than-average afternoon as well

### 5. 12:00–1:00 PM — Lunch hour
- [ ] Expect roughly **70% odds of either a pullback against the morning trend or a period of tight consolidation** — don't panic-exit a good position on lunch chop, but don't add size expecting trend continuation either
- [ ] This is a weak time to initiate new trend-following positions

### 6. Afternoon (1:00–3:00 PM)
- [ ] Statistically the quietest part of the day for making new session highs/lows — lower expectancy for breakout setups here

### 7. Power Hour (3:00–4:00 PM)
- [ ] No edge either way (47%, coin flip) — don't assume trend-day continuation into the close without other confirmation

### 8. Ongoing discipline
- [ ] Every stat above has a real confidence interval — treat Tier 1 as your primary logic, Tier 2 as supporting confluence (this includes NDOG/NWOG fill rates), Tier 3 as color/context only, and never trade off Tier 4 alone
- [ ] Re-test all of these periodically as you add more data — several numbers (the 10:16 cluster especially) already shifted meaningfully as the sample grew, and more will likely shift too

---
*Generated from NQ 1-min OHLC, Feb–Jul 2026, contract-roll-adjusted (NQH/NQM/NQU). All confidence intervals are 95% Wilson score intervals. Re-run and update as more data is imported.*
