# NQ vs ES — Quantitative Test of the Framework
**SMT Divergence, IPDA Liquidity Draws, Dealing-Range Projections & Price Delivery States**

**Dataset:** NQ and ES, both 1-minute continuous contracts, **832 fully-paired trading days**, Jan 2023 – Aug 2026
**Method:** every concept below is drawn from the framework materials provided, restated in plain terms, then tested directly against real OHLC data — not asserted.

---

## READ THIS FIRST — What tested well and what didn't

1. **SMT divergence is the strongest, most validated finding in this entire document.** When NQ makes a fresh high or low within a trading day that ES fails to confirm, price retraces back through the pre-divergence level **88–95% of the time.** This is a real, powerful signal.
2. **The dealing-range standard-deviation framework (CBDR / Asian Range / Flout) works, but at meaningfully lower hit rates than you'd get from the Opening Range** approach already validated in the earlier NQ work. The 1x target lands 42–60% of the time depending on which range is used; 3x drops to 12–29%.
3. **The IPDA lookback liquidity concept is directionally real but asymmetric** — NQ trades into a prior 20/40/60-day high far more often (21–24%) than into a prior 20/40/60-day low (3–7%), a direct reflection of this being a bull-market sample.
4. **Price delivery breaks down almost exactly as the framework describes**, with one important quantified addition: consolidation is "sticky" (44% chance of staying consolidation) while expansion is not (only 13% chance of a second straight expansion day) — meaning **expansion is reliably a transitional state, not a persistent one.**

---

# PART 1 — SMT DIVERGENCE (NEW — NOT PREVIOUSLY TESTED)

## What was tested
Walking through each day's sessions in order (Asia → London → NY AM → NY Lunch → NY PM), tracking the running day-to-date high and low for both NQ and ES simultaneously. A divergence is flagged when one index prints a fresh day-to-date extreme that the other **fails to confirm**:

- **Bearish SMT:** NQ makes a new day-to-date high; ES does not
- **Bullish SMT:** NQ makes a new day-to-date low; ES does not

This is the direct quantitative analog of the "one index leads, the other doesn't confirm" relative-strength concept — applied here specifically as an intraday divergence tool between two closely correlated equity indices, which is a more precise test than the DXY-vs-basket version used earlier since NQ and ES move together far more tightly than NQ and DXY do.

## Results

| Divergence type | Occurrences | Retraces through pre-divergence level | Day closes reversed | Remainder consolidates |
|---|---|---|---|---|
| **Bearish SMT** (NQ new high, ES doesn't confirm) | 141 | **88.7%** (125/141), CI 82.4–92.9% | 51.8% (73/141) | 5.0% |
| **Bullish SMT** (NQ new low, ES doesn't confirm) | 163 | **94.5%** (154/163), CI 89.8–97.1% | 53.4% (87/163) | 4.3% |

## What this actually means

**The retracement rate is extremely strong and this is now the single best signal validated anywhere in this body of work — stronger than the London opening-block breakout (79.5%), stronger than the OR breakout (82%/70%), stronger than everything in the v1–v5 documents.** When NQ pushes to a new intraday extreme without ES confirming, price comes back through that pre-divergence level roughly 9 times out of 10.

**Be precise about what this does and doesn't promise.** "Retraces through the pre-divergence level" is not the same as "reverses the whole day." The **day-close reversal rate is close to a coin flip** (51.8% / 53.4%). So the honest reading is: **SMT divergence reliably signals an imminent pullback/retracement, not necessarily a full trend reversal.** This is exactly consistent with the concept as described — a divergence is a warning that the current leg is exhausted, not a guarantee the whole day flips.

**Consolidation after divergence is rare (4–5%).** When NQ and ES disagree at an extreme, the market almost always *does* something with it (the 88–95% retrace) rather than going quiet.

## Practical read
This is the highest-conviction, most immediately actionable finding in this entire analysis. A concrete rule: **when NQ prints a fresh session/day high that ES does not confirm, expect price to trade back through the level NQ was at before making that high — with roughly 9-in-10 reliability.** Use it as a strong signal to take profit on a long into strength, or to look for a short-term fade — but temper the expectation of what happens *beyond* the retrace, since the follow-through into a full reversal is a genuine coin flip.

---

# PART 2 — IPDA LOOKBACK LIQUIDITY DRAWS

## What was tested
The concept described treats prior 20-day, 40-day, and 60-day highs/lows as the algorithm's reference points for "liquidity" — price is drawn toward the nearest unswept extreme in that lookback window before considering the next one out. Tested directly: on any given day, does NQ's RTH range trade into or through the prior N-day high or low?

## Results

| Lookback | Trades into/through prior HIGH | Trades into/through prior LOW |
|---|---|---|
| 20-day | **24.1%** (196/812), CI 21.3–27.2% | 7.1% (58/812), CI 5.6–9.1% |
| 40-day | 22.2% (176/792), CI 19.5–25.2% | 4.0% (32/792), CI 2.9–5.6% |
| 60-day | 21.1% (163/772), CI 18.4–24.1% | 2.7% (21/772), CI 1.8–4.1% |

## What this means

**The high-side and low-side numbers are dramatically asymmetric — roughly 3x to 8x more likely to sweep a prior high than a prior low, and the gap widens as the lookback lengthens.** This is a direct, mechanical fingerprint of the 2023–2026 bull market: in a trending-up regime, price is constantly making fresh highs and rarely revisiting old lows, so the "draw on liquidity" concept manifests almost entirely on the upside.

**This is not evidence against the concept — it's evidence the concept is regime-sensitive**, exactly as flagged in the earlier 2022 bear-market comparison work. In a genuine downtrend, expect this table to invert (more low-side sweeps, fewer high-side ones), the same way the OR breakout asymmetry and the weekly-level-revisit asymmetry both flipped when tested against 2022.

**All three lookback windows behave similarly, with a mild decay as the window lengthens** (24.1% → 22.2% → 21.1% on the high side). Longer lookbacks are somewhat less likely to be swept on any given day, which makes sense — a 60-day high is a bigger, "harder" level than a 20-day high.

## A methodology note worth being honest about
An early version of this test tried to measure "median days between sweeps," but that metric turned out to be circular — because the lookback window itself resets after every sweep, of course consecutive sweeps look close together. That version was discarded; the hit-rate table above is the valid measurement.

---

# PART 3 — DEALING RANGE STANDARD DEVIATION PROJECTIONS (CBDR / Asian Range / Flout)

## What was tested, and an important adaptation
The framework specifies using the 4:00–8:00 PM ET range (Central Bank Dealers Range) as the primary basis for standard-deviation projections, falling back to the 8:00 PM–Midnight Asian Range if the CBDR is too narrow, and falling back further to the combined 4:00 PM–Midnight "Flout" range if neither qualifies — with specific minimum-pip thresholds given for FX pairs.

**As you flagged, those FX pip thresholds don't have an established equivalent for index futures.** Rather than guess at an arbitrary point threshold, the median range size was used as the qualifying cutoff (CBDR median = 60pts, Asian median = 45pts) — a reasonable, data-driven adaptation of the same "is this range big enough to be useful" logic, though it's worth being clear this is an adaptation, not a direct transfer of the original rule.

## Results — 1x/2x/3x range projected as a target, checked against the NY AM + NY PM kill zones

| Basis | Days used | 1x target hit (up/down) | 2x target hit | 3x target hit |
|---|---|---|---|---|
| CBDR | 325 | 41.8% / 41.5% | 24.9% / 25.8% | 11.4% / 15.1% |
| Asian Range | 140 | 53.6% / 49.3% | 33.6% / 30.0% | 20.0% / 15.7% |
| **Flout** | 185 | **59.5% / 58.4%** | **42.7% / 42.2%** | **29.2% / 26.5%** |

## What this means

**The Flout (the combined, wider range) produces the highest hit rates at every multiple** — which makes sense mechanically: it's already capturing more of the pre-session price action, so smaller additional multiples are needed to reach a given absolute distance. This mirrors a general truth about range-projection tools already seen in the OR work: a wider base range produces higher-probability, closer-in targets.

**Compare directly to the already-validated Opening Range projection method** (9:30–10:00 ET, tested across 833 NQ sessions in the earlier work): 1x/1.5x/2x hit rates there were 28.7%/15.6%/9.0%. **The CBDR-based projections here are actually similar to or somewhat weaker than the OR method**, while the Flout-based ones run noticeably higher. This suggests the specific evening-session dealing range chosen matters less than simply having a wide enough base range — the Flout's advantage looks like it's mostly a size effect, not a special property of that particular time window.

**Honest limitation:** because the model specifies switching between CBDR/Asian/Flout based on which is "favorable," the three samples above (325 / 140 / 185 days) are three different, non-overlapping subsets of days — they can't be compared as if testing the same days under three conditions. This is a real constraint of testing the model as specified, not a flaw in the test.

---

# PART 4 — PRICE DELIVERY: EXPANSION, RETRACEMENT, REVERSAL, CONSOLIDATION

## What was tested
Each RTH day was classified into one of four states using its range relative to a trailing 20-day average and its net directional move:
- **Expansion:** range >125% of trailing average AND move is strongly directional (>55% of the range in one direction)
- **Consolidation:** range <75% of trailing average
- **Reversal:** closes opposite direction from the prior day, with range at or above average
- **Retracement:** everything else — a two-sided day that doesn't meet the other three criteria

## Frequency (n=812 days)

| State | Frequency |
|---|---|
| Retracement | **41.7%** |
| Consolidation | 29.7% |
| Reversal | 15.0% |
| Expansion | 13.5% |

**Retracement is the modal, default state of the market — more common than the other three combined states are individually, and nearly as common as consolidation and reversal put together.** True expansion days — the big, clean directional moves the framework specifically hunts for — are the rarest state, at 13.5%, roughly 1 day in 7.

## Transition probabilities — what tends to follow each state

| From → | Retracement | Consolidation | Reversal | Expansion |
|---|---|---|---|---|
| **Expansion →** | 42% | 22% | 24% | 13% |
| **Retracement →** | 45% | 27% | 16% | 12% |
| **Reversal →** | 46% | 17% | 15% | 22% |
| **Consolidation →** | 35% | **44%** | 10% | 11% |

## What this means

**Consolidation is the only genuinely "sticky" state** — a consolidation day is followed by another consolidation day 44% of the time, meaningfully more often than any other state repeats itself. Consolidation ranges tend to persist once established, which matches the framework's own description of ranges needing to fully form before a genuine expansion breaks out of them.

**Expansion is reliably transitional, not persistent — only a 13% chance of back-to-back expansion days.** After a big directional day, the most likely next state is retracement (42%), then roughly even odds of consolidation (22%) or reversal (24%). **This is a direct, quantified confirmation of the "don't hold for the daily close, trade the session expansion" logic** — chasing a second consecutive expansion day in the same direction is the lowest-probability outcome of the four.

**Reversal days have the highest follow-through into a *new* expansion** (22%, the highest of any row) — consistent with a reversal often being the actual start of a fresh directional leg, not just a one-day blip.

**Practical sequencing implied by this table:** the most probable multi-day path is **Expansion → Retracement → Consolidation → (eventually) a new Expansion or Reversal breaks the range.** This lines up closely with the framework's own descriptive logic, now with real transition percentages attached to it rather than a qualitative claim.

---

# PART 5 — HOW THESE FOUR PIECES FIT TOGETHER

Put in the order you'd actually use them in a session:

1. **Start with IPDA context:** is price sitting near an unswept 20/40/60-day high or low? In this bull-market sample, the high side is the much more active draw (21–24% vs 3–7%) — know which liquidity pool is realistically in play before the session starts.
2. **Mark the dealing range** (CBDR, or Asian if CBDR is narrow, or the combined Flout if both are narrow) and project 1x/2x/3x for session targets — understanding the Flout-based targets have run the highest hit rate in this sample.
3. **During NY AM and NY PM, watch for SMT divergence between NQ and ES.** This is the strongest, most reliable signal in the entire analysis (88–95% retrace rate) — if NQ pushes to a fresh extreme ES doesn't confirm, expect a retracement back through the pre-divergence level with very high confidence, while treating a full-day reversal as a genuine coin flip on top of that.
4. **Read the day's evolving character against the four delivery states.** After an expansion move, the base rate says retracement or consolidation is coming (64% combined), not a second expansion (13%) — plan exits and re-entries accordingly rather than assuming the trend continues unchecked.

---
*All confidence intervals are 95% Wilson score intervals. SMT divergence, IPDA, and dealing-range tests exclude the 19 dates affected by NQ or ES contract rolls. Price-delivery classification uses a trailing 20-day adaptive average rather than a fixed threshold, to remain regime-sensitive across the sample.*
