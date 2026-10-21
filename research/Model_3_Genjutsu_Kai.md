# MODEL 3 — "GENJUTSU KAI"
### The Reversal Model — SMT Divergence, NY AM Only
**Built on 824–873 NQ/ES paired trading days (2023–2026) · Money management intentionally excluded**

---

## Why This Name
"Kai" means release — specifically, the technique used to break a genjutsu, an illusion cast over the battlefield. That's precisely what an SMT divergence is: the current move is revealed to be an illusion the moment a correlated instrument refuses to confirm it, and price snaps back through the level as the illusion breaks.

---

## Scoping Note: This Model Is NY AM-Specific

**This model is scoped to New York AM (09:30–11:00 ET) specifically** — the highest-volatility session tested anywhere in this framework (188pts average range, more than double every other session). That's the primary justification for the scope: the largest available move gives the best magnitude-to-risk profile, even accounting for the point below.

**One honest correction to state plainly before proceeding:** on the raw session-level SMT divergence retrace-through rate, London actually tested slightly higher than NY AM:

| Session | Bear divergence retrace | Bull divergence retrace |
|---|---|---|
| London | 96.8% | 94.1% |
| **NY AM** | **87.9%** | **93.1%** |

NY AM is not the highest-*reliability* session for this specific signal — it's the highest-*magnitude* session. The two are different things. Scoping to NY AM is a legitimate choice on that basis (bigger moves can outweigh a few points of lower confirmation rate), but this document won't overstate the case — NY AM wins on opportunity size, not on raw hit rate.

Everything below applies to NY AM only. London and NY Lunch divergence behavior is no longer part of this model's scope.

---

## Definitions

- **Session-level divergence:** tracked across the running NY AM high/low specifically, compared against ES over the same window.
- **OR-level divergence:** tracked bar-by-bar within the 9:30–10:00 Opening Range — a finer-grained version of the same mechanism, entirely contained within the NY AM window this model is now scoped to.

---

## Stage 1 — Preparation

Reversal is a fairly rare daily state (15.0% of days classified this way) — SMT divergence is the tool that flags a reversal-in-progress in real time, rather than only being identifiable after the fact. Because this model is scoped to NY AM, every divergence you're watching for happens inside a single two-hour window — there's no need to track other sessions for this model specifically.

---

## Stage 2 — Opportunity Discovery

### Session-level NY AM divergence
Track NQ's running NY AM high/low against ES's over the same window (09:30–11:00 ET). A divergence forms when NQ prints a fresh NY AM extreme that ES doesn't confirm.

| | n | Retrace-through rate |
|---|---|---|
| Bearish (NQ fresh high, ES no confirm) | 58 | **87.9%** |
| Bullish (NQ fresh low, ES no confirm) | 87 | **93.1%** |

### OR-level divergence (the sharper, earlier-firing version, fully inside NY AM)
Track NQ against ES **bar-by-bar** starting at 9:30, watching for the moment one index prints a fresh running high/low the other doesn't confirm.

| | n | Retraces in 9:50–10:10 | Retraces by end of day |
|---|---|---|---|
| Bearish (NQ fresh high, ES no confirm) | 403 | 73.7% | 97.3% |
| Bullish (NQ fresh low, ES no confirm) | 389 | 78.9% | 97.9% |

**Critical timing fact: nearly all OR-level divergences form and confirm by 9:41** — 243 instances at 09:31 alone, dropping steadily through 09:41. This means you typically have 9–19 minutes of lead time before the 9:50–10:10 window (where the retrace is most reliable) even opens. You are positioned ahead of the window, not reacting inside it.

**Ruled out — tested and does not add value:** the 8:30 AM candle's directional read, and NQ/ES agreement at 8:30, were both tested directly as potential filters. Neither moved the retrace probability at all (76.7% vs 75.7%; 77.3% vs 75.9% — statistically identical in both comparisons). Do not build the 8:30 print into this model.

---

## Stage 3 — Trade Planning: What the Signal Actually Promises

**Be precise, because two very different outcomes get conflated if you're not careful:**

| What you're trading for | Reliability |
|---|---|
| Price retraces back through the level NQ was at *before* the divergent extreme | **73.7–93.1%** within NY AM, depending on which version of the signal — the real edge |
| The full session closes reversed from the original direction | **~50–54%**, a coin flip |

**Plan the primary objective around the retracement.** Treat a full reversal as a bonus outcome, not the base case.

No PD array is required to *identify* the setup — the divergence itself, purely from comparing NQ's and ES's extremes, is the signal. A PD array (your chosen lowest-timeframe confirmation tool) is for precise entry timing once the divergence is already flagged.

---

## Stage 4 — Trade Execution

- **Trigger:** within the 09:30–11:00 ET window, NQ prints a fresh high (or low) — at either the session level or, bar-by-bar, within the 9:30–10:00 OR — that ES does not confirm.
- **Entry:** on confirmation the retracement is beginning — a close back inside the prior range is a reasonable, simple trigger; a PD array formation at that reclaim adds precision.
- **Primary target:** the pre-divergence level.

---

## Stage 5 — Trade Management: Using the RTH Gap as a Staged Target System

If NQ also has an open RTH gap that day (today's 9:30 open vs. prior RTH close), and the divergence is resolving in the same direction as that gap, the gap's own octant structure gives validated staged targets beyond the primary pre-divergence level:

| RTH gap octant (fraction of the gap filled) | Standalone touch rate during RTH |
|---|---|
| 1/8 | 92.2% |
| 2/8 | 86.1% |
| 3/8 | 80.5% |
| **4/8 (50% fill)** | **76.1%** |
| 5/8 | 72.2% |
| 6/8 | 65.2% |
| 7/8 | 60.8% |
| **8/8 (full gap fill)** | **57.8%** |

**How to use this:** once the divergence-based retracement reaches the pre-divergence level (your primary target), if there's still room toward an unfilled RTH gap in the same direction, the 50%-fill level (76.1% standalone reliability) is a reasonable secondary objective, and full gap fill (57.8%) is a legitimate stretch target — not a certainty, but a real, independently-validated level, not an arbitrary extension.

**Only hold beyond the staged targets if NY AM's broader character is actually confirming a bigger move** — check that the session, not just the immediate divergence, is showing real directional commitment before assuming continuation past the gap-fill levels. Don't assume it by default.

---

## One-Page Summary — This Is the Trade

1. **This model applies to NY AM (09:30–11:00 ET) only** — the highest-volatility session tested, though not the single highest-confirmation session for this signal specifically (London tested slightly higher on raw retrace rate; NY AM is scoped here for magnitude, not for a superior hit rate).
2. Track NQ against ES within the NY AM window, both at the session level (whole-window running extremes) and bar-by-bar within the 9:30–10:00 OR for earlier, sharper signals.
3. **OR-level divergences form fast** — watch 9:31–9:41 closely; most of the signal is already confirmed before the 9:50–10:10 execution window even opens.
4. Entry: PD array confirmation of the reclaim once the divergence is flagged, at either resolution.
5. **Primary target: the pre-divergence level.** This is the real trade — 73.7–93.1% within NY AM, not the ~50% coin-flip of a full reversal.
6. **If an RTH gap is open in the same direction:** use its octant structure as staged secondary targets — 50% fill (76.1%) and full fill (57.8%) are both independently validated levels.
7. **Ruled out:** the 8:30 AM candle, tested directly as a filter, adds nothing.
8. Don't assume continuation past your targets — confirm NY AM's broader session character first.

---
*All confidence intervals are 95% Wilson score intervals where applicable. PD array matrix references are generic — apply your own confirmed structure-identification method at the marked levels.*
