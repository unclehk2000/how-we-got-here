# MODEL 1 — "DOMAIN EXPANSION"
### The London Expansion Model
**Built and refined against 868–873 NQ trading days (2023–2026) · Money management intentionally excluded**

---

## Scoping Note: This Model Is London-Specific

Earlier testing compared opening-block breakout reliability across all five trading sessions:

| Session | Baseline opening-block hold rate |
|---|---|
| **London (02:00–02:30 ET)** | **79.5%** |
| NY PM (13:30–14:00 ET) | 69.6% |
| Asia (20:00–20:30 ET) | 68.8% |
| NY AM (09:30–10:00 ET) | 60.8% |
| NY Lunch (11:30–12:00 ET) | 59.3% |

London was the clear standout even before any deeper refinement. Everything that follows was built and validated **exclusively against the London Opening Range**. This is deliberately a London-only model. Asia and NY PM remain plausible candidates for a similarly refined model, but that work hasn't been done — treat their baseline numbers above as reference only, not as validated setups under this framework.

**Why this name:** a Domain Expansion is a technique that forces the entire battlefield onto your terms — total, overwhelming control of the space. That's what a genuine London expansion is: rare in the sense that most sessions don't hand you a clean one-sided move, but decisive once it's confirmed.

---

## Definitions

- **LOR (London Opening Range):** 02:00–02:30 ET. High (H), Low (L), Range (R = H − L).
- **Anchor:** whichever extreme (H or L) formed **later** within the LOR is the "1" (recent) point; the other is the "0" (origin) point — matching the direction price was actually traveling through the range.
- **Octant position:** where the 02:30 close sits within the LOR, expressed 0 (at the low) to 1 (at the high).
- **Terminus:** the statistically most likely point where the expansion move actually ends, expressed as a multiple of R beyond the broken LOR boundary. This is the model's target — not a minimum threshold the move might clear, but the expected stopping point of the move itself.

---

## Stage 1 — Preparation

Expansion is a transitional state, not a persistent one at the daily level — it follows Retracement 42% of the time and Reversal 22%, but almost never follows itself (13%). At the London-session level specifically, don't assume yesterday's clean expansion increases today's odds; treat each day's LOR independently.

---

## Stage 2 — Opportunity Discovery: Octant Read

Divide the LOR into eighths. The 02:30 close position predicts the eventual breakout direction with a strong, monotonic gradient:

| Octant | Breaks UP | Breaks DOWN |
|---|---|---|
| 0.000–0.125 | 9.5% | 90.5% |
| 0.125–0.250 | 10.2% | 89.8% |
| 0.375–0.500 | 50.0% | 50.0% |
| 0.625–0.750 | 70.4% | 29.6% |
| 0.750–0.875 | 80.0% | 20.0% |
| 0.875–1.000 | 95.0% | 5.0% |

**Threshold to use: octant ≥0.625 (bullish) / ≤0.375 (bearish).** A full sweep across cutoffs from 0.625 to 0.95 showed the eventual hit rate stays flat the entire way — tightening the threshold further only shrinks the tradeable sample without improving reliability. Use the inclusive threshold.

---

## Stage 3 — Trade Planning: Timing and Confirmation

**Act in the 02:30–02:50 window, not later.** Of all clean one-sided breakouts, 66% confirm within this window, at the highest hold rate of any timing bucket (84.5%). A commonly assumed "kill zone" further out (02:50–03:10) is actually weaker — only 22.3% of breakouts fire there, at a lower 70.8% hold rate. Waiting rewards you with a worse setup, not a better-confirmed one.

**Multiple tests of the LOR boundary do not improve reliability.** Single-touch setups (one wick test of the boundary before the break) hit their eventual extension outcome more reliably than multi-touch setups (2+ tests). Don't wait for repeated tests as a filter — it costs entry price for no benefit.

**Ruled out — the 20-day trailing range "wider than normal" confirmation is inverted from the naive assumption.** A LOR **narrower** than its own 20-day trailing average produces a more reliable breakout (84.6%) than a wider one (74.5%). Favor tight LORs, not wide ones, if using this as a secondary filter at all.

---

## Stage 4 — Trade Execution: Boundary and Entry

Once direction is set (octant ≥0.625/≤0.375) and the breakout confirms within 02:30–02:50:

- **The opposite LOR boundary holds as support/ceiling through the rest of London without exception** across every configuration tested — use it as your stop reference.
- **Entry:** a PD array (your chosen lowest-timeframe confirmation tool — a gap, order block, or reclaim structure) forming at the LOR boundary itself, on the **first** clean touch-and-reject, inside the 02:30–02:50 window.

---

## Stage 5 — Trade Management: The Terminus (This IS the Target)

The core trade this model is built around: **enter during the 02:30–02:50 window based on the octant read, and target the statistically most likely termination point of the move — not a fixed minimum, the actual expected stopping point.**

### The distribution of where the move actually terminates
Measured across all 220 qualifying setups (octant confirmed, breakout fires in window), as a multiple of R beyond the broken LOR boundary:

| Statistic | Value |
|---|---|
| Median termination point | **1.84R** |
| Mean | 2.14R |
| 25th percentile | 1.06R |
| 75th percentile | 2.84R |
| 10th percentile | 0.64R |
| 90th percentile | 3.83R |

**This is a broad, right-skewed distribution — there is no single sharply dominant delineation.** The single largest bounded zone is **2.0–2.5R (14.1% of days)**, but the overall spread is wide enough that the median (1.84R) is the most defensible single number to trade toward, with the understanding that roughly a quarter of setups terminate before 1.06R and roughly a quarter run past 2.84R.

### The refinement: Asia-sweep-within-LOR changes where the move terminates

Checking whether Asia's high or low (in the anchor direction) gets taken out *within* the LOR window itself (02:00–02:30), before the breakout even confirms — this materially shifts the terminus:

| Condition | n | Median terminus | Interquartile range |
|---|---|---|---|
| **Asia's extreme swept during LOR formation** | 92 | **1.39R** | 0.92–2.35R |
| **Asia's extreme NOT swept during LOR** | 127 | **2.15R** | 1.39–3.02R |

**The mechanism makes sense: if the LOR already consumes Asia's liquidity while forming itself, less "unclaimed" liquidity remains to fuel the continuation, and the move terminates closer in. If Asia's extreme is still sitting untouched when the breakout begins, there's more liquidity left to run toward, and the move typically extends further before terminating.**

**Practical rule for setting the terminus target:**
- **If Asia's extreme was already swept during the LOR (02:00–02:30):** target **1.39R**, with realistic range 0.92R–2.35R.
- **If Asia's extreme is still outstanding when the breakout confirms:** target **2.15R**, with realistic range 1.39R–3.02R.
- **If Asia-sweep status is unclear or unavailable:** default to the unconditional median, **1.84R**.

---

## One-Page Summary — This IS the Trade

1. **This model applies to London only.**
2. Mark the LOR (02:00–02:30 ET), divide into octants.
3. At 02:30, read the octant position: **≥0.625 leans bullish, ≤0.375 leans bearish.**
4. **Act in the 02:30–02:50 window** — 66% of clean breakouts confirm here, at the highest hold rate (84.5%) of any window.
5. Entry: PD array at the LOR boundary on the **first** clean touch-and-reject.
6. Stop reference: the opposite LOR boundary.
7. **Check whether Asia's extreme was already swept within the LOR (02:00–02:30):**
   - **Swept → terminus target: 1.39R** beyond the broken boundary.
   - **Not swept → terminus target: 2.15R** beyond the broken boundary.
   - Unknown → default to **1.84R** (the unconditional median).
8. Ruled out as filters — do not add: NDOG/NWOG, true day open, "wider than average" LOR confirmation, or multiple boundary touches before entry.
9. Exit without assuming continuation into NY — a confirmed London breakout continues into NY AM only 48.8% of the time, a coin flip.

---
*All figures derived from 220 qualifying setups (octant confirmed, breakout confirming in the 02:30–02:50 window) unless otherwise noted. PD array matrix references are generic — apply your own confirmed structure-identification method at the marked levels.*
