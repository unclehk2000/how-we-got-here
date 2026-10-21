# Premarket Fibonacci Model — Test Results vs. NQ and ES Benchmark

**Method:** For each trading day, the 7:00–9:00 AM ET range (high H, low L, range R) was marked. The Fibonacci anchor was set using whichever extreme formed **later** (closer to 9:00) as the "1" point and the other as the "0" — i.e., anchored to the actual chronological direction of the premarket move, not an assumed one. All levels (0.5 midpoint, 1.5 continuation, and negative "terminus" extensions) were derived from that anchor and tested against real RTH price action.

**Sample:** 831 NQ days, 832 ES days, 2023–2026, same underlying date set for both.

---

## PART 1 — BIAS RULES (6 & 7): Two Very Different Answers Depending on What You're Asking

The model states: if 9:30 opens below the 0.5 midpoint, stay bearish and aim for sell-side liquidity; if above, stay bullish and aim for buy-side liquidity.

**This rule gives a genuinely different answer depending on what "success" means, and that distinction matters enormously for how you'd actually trade it.**

| Question | NQ | ES |
|---|---|---|
| Does RTH **close** in the direction the bias predicted? | **51.1%** (CI 47.7–54.5) — a coin flip | **51.8%** (CI 48.4–55.2) — a coin flip |
| Does price **reach liquidity** in the predicted direction at any point during RTH? | **89–91%** (bear: 90.9%, bull: 88.4%) | **89–91%** (bear: 88.7%, bull: 91.4%) |

**Read this carefully — it's the single most important finding in this test.** The bias rule is close to useless for predicting where the day *closes* — essentially random. But it is **extremely reliable for predicting that price will touch the targeted liquidity pool at some point in the session** (beyond the 7–9am high or low, in the biased direction) — right around 89–91% in both instruments, independently confirmed.

**What this means practically:** this model is a **liquidity-tap tool, not a closing-direction tool.** Use it to anticipate that price will run to take out the premarket high or low in the biased direction — that's a real, strong edge (~90%). Do **not** use it to decide whether to hold a position into the close expecting the day to finish in that direction — that part of the claim doesn't hold up; it's a coin flip.

---

## PART 2 — FORECASTING RULE 1: The 1.5 Continuation Level

The model states: the 1.5 extension predicts the New York session's high or low, via order-flow continuation.

| Metric | NQ | ES |
|---|---|---|
| RTH reaches/exceeds the 1.5 level | **65.7%** (CI 62.4–68.9) | **63.1%** (CI 59.8–66.3) |
| Median actual extension beyond the range edge, when moving in that direction (in units of R) | **0.94R** | **0.88R** |
| The 1.5 level itself sits at | 0.50R beyond the edge | 0.50R beyond the edge |

**The 1.5 level works, and works consistently across both instruments — but it undersells how far price typically goes.** Nearly two-thirds of days reach it outright. More strikingly, on days where price *does* extend in the continuation direction, the **median** extension (0.94R) is almost double what the 1.5 level itself represents (0.50R beyond the range edge). 

**Practical read:** 1.5 functions well as a **first, conservative target** — reached about two-thirds of the time — rather than an ambitious stretch target. If you're using it as your sole profit objective, you're very likely leaving real, typical continuation on the table; a 2.0–2.5 extension would sit closer to the actual median day.

---

## PART 3 — FORECASTING RULE 2: The -1.5 "Terminus"

The model states: using the negative extensions, average price terminates around -1.5 when moving against the original bias.

| Metric | NQ | ES |
|---|---|---|
| Days where price moves counter to the bias at all (beyond the origin edge) | 71.0% | 70.7% |
| Median counter-move, when it happens (units of R beyond origin) | **1.24R** | **1.26R** |
| Unconditional probability RTH reaches the full -1.5 level | **31.0%** (CI 28.0–34.3) | **31.0%** (CI 28.0–34.2) |
| Of the days that DO move counter-direction, % reaching as far as -1.5 | 43.7% | 43.9% |

**This claim doesn't hold up as stated, and the two instruments agree almost to the decimal.** "Average price terminates at -1.5" implies -1.5 is roughly where the *typical* counter-move stops. The data says something different: the median counter-move (1.24–1.26R) falls *short* of 1.5R, and unconditionally, price only reaches the actual -1.5 level on **31% of all days** — meaning 69% of the time, either there's no meaningful counter-move at all, or it stops before reaching that far.

**Practical read:** -1.5 is a real, useful **outer boundary / stop-placement reference** — it's not a rare, once-in-a-while level (31% of all days reach it is substantial), but it materially overstates the "average" case. If you want a level that actually represents the typical adverse excursion, something closer to **-1.25** matches the median far better than -1.5 does. Use -1.5 as a legitimate worst-case/stop-region marker, not as your expected terminus.

---

## SUMMARY — What Survives Contact With Real Data

| Model component | Verdict |
|---|---|
| 0.5 bias predicts which liquidity gets tapped | ✅ **Strong, ~90%, confirmed in both instruments** |
| 0.5 bias predicts the day's close direction | ❌ Coin flip — don't use it this way |
| 1.5 predicts continuation occurring | ✅ Real, ~64–66% hit rate |
| 1.5 as the *expected* extension distance | ⚠️ Understates it — actual median move is ~2x further |
| -1.5 as the *average* terminus | ❌ Overstates it — median counter-move falls short of 1.5R |
| -1.5 as a real, reachable outer boundary | ✅ Legitimate — happens on 31% of all days |

**The model is directionally sound but needs two calibration corrections to match reality: treat 1.5 as a floor, not a ceiling, and treat -1.5 as an outer stop-boundary, not an "average" expectation — the real average counter-move sits closer to 1.25.** Both corrections held with remarkable consistency across NQ and ES independently, which is a good sign the underlying mechanic (premarket range projecting forward into the RTH session) is real, even where the specific multiples quoted needed adjustment.

---
*All confidence intervals are 95% Wilson score intervals. Fibonacci anchor determined chronologically (the later-forming extreme = 1, matching the direction price was actually traveling through 7–9am) rather than assumed.*
