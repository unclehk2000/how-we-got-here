# MODEL 2B — "BANKAI"
> **Oct 2026 re-test:** the timing holds, but it is not specific to the midpoint. 45.6% of by-11:00 touches land in 09:31–09:41 (median 12 min), and a mirror level at the same distance on the other side of the open shows the same front-loading (44% in the first 10 min, median 14 min). By 11:00 the midpoint is reached 58.0% (train) / 54.5% (test), against 55.3% / 54.1% for the mirror. The prior-day-state dial does not survive the placebo. Bankai is kept as a **time map**: the open is when NQ travels furthest, fastest. See Model 2 "Re-test (Oct 2026)".

> **Carry note (Oct 2026):** inside the Bankai window only the long side into the midpoint stays positive out of sample (+0.023R by 11:00 in 2025–26; the short side is −0.073R). Re-entering on a reclaim after price goes through the midpoint, with a stop at the sweep extreme, loses (−0.19R pooled for longs). See Model 2 "Carry-charge use".

### NY AM Opening-Range Retracement — A Time-Bound Execution Program
**Split off from Shikai as a tighter, NY-AM-specific, time-bound version · Built on 531 meaningful-distance NQ trading days (2023–2026) · Money management intentionally excluded**

---

## Why This Name
Bankai is the second, fuller release — sharper and more demanding of precision than Shikai, and in the source material it typically carries a time limit. That's exactly what this model is: Shikai's core mechanism (retracement to the overnight midpoint), tightened into a specific window with a hard time boundary, rather than a loose all-day possibility.

---

## What This Model Is

Shikai treats the overnight-midpoint retracement as a general, all-day tool. This model is the deliberately narrower version: **the program starts at 9:30, is scoped entirely to NY AM, and has an explicit time terminus at 11:00 AM** — not just a price target, a time boundary the trade either resolves within or doesn't.

**Justification for the 11:00 cutoff:** of all meaningful-distance retracements that occur, 56.3% happen somewhere within the 9:30–11:00 window, and the overwhelming majority of the ones that are going to happen at all happen well before 11:00 — most within the first ten minutes after the open specifically (see Stage 3). Waiting past 11:00 is fishing in a much smaller pond.

---

## Stage 1 — Preparation

Mark the overnight range (prior 18:00 close through today's 9:30 open) and its midpoint. Check the distance from the 9:30 open to that midpoint — if under 0.15% of price, this is a low-conviction/trivial setup; the program below assumes a genuine, tradeable distance exists.

**Check yesterday's price-delivery state** — this meaningfully shifts the odds (see Stage 2).

---

## Stage 2 — The Four Structural Contexts (Yesterday's State)

Conditioning the touch-by-11am rate and typical duration on which of the four price-delivery states yesterday fell into:

| Yesterday's state | n | Touch-by-11am rate | Median duration to touch |
|---|---|---|---|
| **Consolidation** | 145 | **60.7%** (CI 52.6–68.3%) | 17.0 min |
| **Retracement** | 207 | **57.0%** (CI 50.2–63.6%) | **12.0 min — fastest** |
| Reversal | 74 | 51.4% (CI 40.2–62.4%) | 14.0 min |
| Expansion | 69 | 50.7% (CI 39.2–62.2%) | 17.0 min |

**Honest read on the separation:** the confidence intervals overlap substantially across all four — this is a real, directionally consistent lean, not a sharp, statistically bulletproof split. That said, the pattern is sensible and worth using as a weighting factor:

- **Best combination: yesterday was Retracement or Consolidation.** These two states show both the higher touch rates (57–61%) and — for Retracement specifically — the fastest resolution (12 minutes median). A grinding or range-bound prior day sets up a cleaner, quicker retracement today.
- **Weaker combination: yesterday was Expansion or Reversal.** Touch rates drop to roughly 51%, and when Expansion precedes it, the resolution takes longer (17 min median) despite the lower hit rate — a slower, less reliable setup.

**Practical use:** treat yesterday's state as a conviction dial, not a hard filter. Full size/conviction after Retracement or Consolidation days; reduced conviction after Expansion or Reversal days.

---

## Stage 3 — Entry Strategy: The Highest-Probability 10-Minute Window

A finer, minute-by-minute scan across the open refines this further than a simple 20-minute bucket. A sliding 10-minute window was tested at every possible start point in the first half hour:

| Window | Share of all touches |
|---|---|
| **09:31–09:41** | **41.8% — the single best window found** |
| 09:30–09:40 (raw, includes the literal open print) | 39.8% |
| 09:32–09:42 | 37.1% |
| 09:35–09:45 | 30.4% |
| 09:38–09:48 | 21.1% |

**Primary execution window: 09:31–09:41.** The edge does not sit further out from the open — it decays steadily starting at the open itself. A window that starts later (e.g., 09:41–09:51) was tested directly and captures only 16.7% of all touches, less than half of what 09:31–09:41 captures — skipping the first several minutes on the assumption they're low-value costs you the majority of the opportunity, not the noise. **09:31–09:41 is the practical optimum: it avoids the literal 9:30:00 open print for execution purposes while giving up essentially nothing of the edge** (41.8% vs. 39.8% for the raw open-inclusive window — statistically the same, slightly favoring the one-minute-delayed version).

Beyond 09:41, the opportunity thins sharply — treat 09:41–10:00 as a secondary, lower-probability zone, not a primary one.

---

## Stage 4 — How Long the Program Runs Before It Terminates

Measuring actual elapsed time from the 9:30 open to the touch, for every day where a touch occurred within the window:

| Statistic | Value |
|---|---|
| Median duration | **13.0 minutes** |
| Mean duration | 22.3 minutes |
| 25th percentile | 5.0 minutes |
| 75th percentile | 32.0 minutes |
| 90th percentile | 54.2 minutes |

**Duration distribution by 10-minute bin:**

| Bin | Share |
|---|---|
| **0–10 min** | **39.8%** |
| 10–20 min | 18.4% |
| 20–30 min | 10.7% |
| 30–40 min | 11.0% |
| 40–50 min | 7.4% |
| 50–90 min | ~12.5% combined |

**The single most likely outcome is resolution within the first 10 minutes of the open (39.8%) — nearly matching the 20-minute window finding above.** Median duration (13 minutes) confirms this is generally a fast-resolving setup, not a slow grind toward 11:00. The right tail exists (10% of successful setups take 54+ minutes) but is a minority outcome, not the expectation.

---

## Stage 5 — Trade Execution

1. **At 9:30, mark the overnight midpoint.** Confirm the open sits a meaningful distance from it (≥0.15% of price).
2. **Check yesterday's state.** Full conviction if Retracement or Consolidation; reduced conviction if Expansion or Reversal.
3. **Primary execution window: 09:31–09:41.** This ten-minute stretch captures 41.8% of all successful retracements — the highest concentration found anywhere in the session. Enter here on PD array confirmation of a stall/rejection in the direction of the fade.
4. **Secondary window: 09:41–10:00**, if the setup hasn't resolved yet — meaningfully weaker, but not negligible.
5. **Beyond 10:00, treat the setup as increasingly unlikely to resolve** — the opportunity has thinned substantially by this point.

---

## Stage 6 — Trade Management: The Time Terminus

- **Hard time boundary: 11:00 AM.** If the retracement hasn't resolved by then, the program is done — 43.7% of meaningful-distance setups simply never touch within the NY AM window at all, and continuing to hold past 11:00 is holding into a session (NY Lunch) with materially different, lower-conviction characteristics.
- **Expected duration if it's going to work: 13 minutes median, with a strong chance (39.8%) of resolving inside the first 10.** If nothing has happened by roughly the 30–40 minute mark (past the 75th percentile), the setup is behaving atypically — tighten management rather than assuming it will still arrive by 11:00.
- Once touched, remember the broader Shikai finding: **continuation-through vs. bounce-back from the level is a coin flip (48.6%/51.4%).** The touch itself is not your exit signal — require independent confirmation.

---

## One-Page Summary

1. **This is a time-bound program: starts at 9:30, hard terminus at 11:00 AM.**
2. Mark the overnight midpoint; confirm the open is a meaningful distance away (≥0.15%).
3. **Check yesterday's state:** full conviction after Retracement (57.0%, fastest at 12min median) or Consolidation (60.7%, highest hit rate); reduced conviction after Expansion or Reversal (~51% both).
4. **Highest-probability entry window: 09:31–09:41** — captures 41.8% of all successful retracements, the best of every window tested. A later window (09:41–09:51) was tested directly and captures less than half as much (16.7%) — don't skip the early minutes on the assumption they're untradeable noise.
5. **Secondary window: 09:41–10:00.** Beyond 10:00, the opportunity thins sharply.
6. **Expected duration: median 13 minutes, with 39.8% resolving in the first 10.** If nothing's happened by the 30–40 minute mark, the setup is running atypically.
7. At the touch, require independent confirmation before assuming direction — continuation vs. bounce is a coin flip.
8. If unresolved by 11:00, the program is over — don't carry it into NY Lunch.

---
*All confidence intervals are 95% Wilson score intervals. PD array matrix references are generic — apply your own confirmed structure-identification method at the marked levels.*
