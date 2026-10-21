# MODEL 5 — "BYAKUGAN"
### The 7–9AM Liquidity Draw Model (Refined)
**Built and refined across 824–832 NQ/ES trading days (2023–2026) · Money management intentionally excluded**

---

## Why This Name
Byakugan is a technique built entirely around seeing what's normally invisible — chakra points, structural weaknesses, things hidden at range. That's what this model does with the 7–9am premarket range: it doesn't predict the close by itself, it reveals *which* liquidity is genuinely in play and *how much conviction* is behind the move toward it — information the raw bias signal alone can't see.

---

## The Core Reframe — Read This First

Earlier testing of the basic version of this model produced two very different numbers depending on the question asked:

| Question | Raw accuracy |
|---|---|
| Does the 0.5 premarket-range midpoint predict the day's **close direction**? | **~51%** — a coin flip |
| Does it predict that price **taps the liquidity** in that direction at some point? | **~89–91%** — strong |

**This model exists to close that gap.** The raw bias is not a directional tool on its own. What follows is the refined version that converts the weak 51% into a genuinely usable signal, using two layers of conditioning discovered through direct testing: session-sweep context, and — the sharper layer — the *percentage distance* from the open to the relevant liquidity.

---

## Definitions

- **7–9AM Range:** the high (H) and low (L) of NQ (or ES) between 7:00–9:00 AM ET. Range = R = H − L.
- **Fibonacci anchor:** whichever extreme (H or L) formed **later** — closer to 9:00 — is anchored as the "1" point (the direction price was actually traveling). The other extreme is "0."
- **0.5 (midpoint):** (H+L)/2 — anchor-independent, always the true middle of the range.
- **1.5 (continuation level):** the recent extreme + 0.5R, in the direction of travel.
- **Terminus levels:** −0.5 and −1.5, measured beyond the *origin* extreme, opposite the direction of travel.
- **Asia session:** 20:00–00:00 ET (prior evening). **London session:** 02:00–05:00 ET.
- **AL extreme:** the combined Asia+London high (for a bullish bias) or low (for a bearish bias) — whichever is farther from the open in the biased direction.

---

## Stage 1 — Preparation

Before the session, mark:
- The 7–9AM range: H, L, midpoint.
- The Asia and London session extremes.
- The **raw bias**: if 9:30 opens below the midpoint → bearish; above → bullish.
- **Immediately check: has the AL extreme (the level in the bias direction) already been swept before 9:30?**

**This single check removes 42% of days from consideration entirely.** When the AL extreme is already taken out before the open, pooled bias accuracy on those days is **48.8%** — pure noise. **Do not trade the directional bias on these days by default.** (The liquidity-tap logic from the base model may still apply, but the directional conviction this refined model is built for does not.) **See the Directional Asymmetry section below — this rule needs to be applied unevenly by direction, not as a flat cutoff.**

---

## Directional Asymmetry — NQ's Carry-Driven Bullish Skew

NQ is a carry-charge market with a structural long-term upward drift. This isn't a background assumption — it shows up directly and consistently at every stage of this model, and it changes how the rules above should actually be applied.

### The baseline split
| | Accuracy | 95% CI |
|---|---|---|
| **Bullish bias days** | **56.6%** | 51.9–61.3% |
| **Bearish bias days** | **45.1%** | 40.2–50.0% |

The intervals barely touch. Bullish and bearish bias days are genuinely different populations, not noise around the same number — bullish sits meaningfully above a coin flip before any refinement is applied; bearish sits at or slightly below one.

### The stand-down rule (Stage 1) is doing most of its work on bearish days
| "Already swept pre-open" | Accuracy |
|---|---|
| Bullish | 55.2% (CI 48.3–61.9) — mediocre but not clearly harmful |
| **Bearish** | **39.9%** (CI 32.2–48.0) — a real anti-signal |

**Apply the pre-open stand-down rule strictly on bearish setups. On bullish setups it's optional — the day still resolves correctly more often than not even when this filter would otherwise flag it.**

### The target zone is direction-agnostic once confirmed
| Genuine sweep, target zone | Bullish | Bearish |
|---|---|---|
| 0.30–0.50% | 75.0% | 77.4% |
| 0.50–1.00% | n/a (thin) | 76.9% |

Once a sweep is genuinely confirmed in the 0.30–1.00% zone, bearish setups perform just as well as bullish ones. **The carry effect lives in the baseline, not in the quality of a confirmed signal** — a well-confirmed bearish setup is not a weaker trade than a well-confirmed bullish one.

### The fade/inverse-signal rule (Stage 3, point 4) is where the asymmetry matters most
| No-sweep in the 0.50–1.00% zone | Accuracy |
|---|---|
| Bullish | **63.6%** — the original bullish bias still wins more often than not, even unconfirmed |
| **Bearish** | **27.3%** — a strong, genuine inverse signal |

**This is the one rule that should change behavior by direction.** A missing sweep confirmation is weak grounds to fade a bullish bias — the underlying drift keeps carrying a majority of unconfirmed bullish days to the correct close anyway. The same missing confirmation on a bearish bias is strong grounds to fade — unconfirmed bearish setups are wrong close to three times out of four.

---

## Stage 2 — Opportunity Discovery: The Distance Filter

For the remaining ~58% of days (AL extreme not yet swept), compute the **percentage distance** from the 9:30 open to that AL extreme:

`distance % = |AL extreme − open| / open × 100`

This is the core refinement. A sweep of nearby liquidity and a sweep of distant liquidity are **not the same signal** — tested directly:

| Distance to liquidity at open | Frequency of sweep | Accuracy **if** swept | Accuracy **if not** swept |
|---|---|---|---|
| 0.00–0.15% (right on top of it) | 90.0% (near-automatic) | 61.1% — weak | too few to measure |
| 0.15–0.30% | 64.0% | 66.2% | 31.1% |
| **0.30–0.50%** | 46.8% | **76.5%** | 29.3% |
| **0.50–1.00%** | 27.6% | **81.0%** | 41.8% |
| >1.00% | 10.7% (rare) | n/a — too thin | 32.0% |

**The pattern is clear and consistent: the closer the liquidity sits to the open, the more automatic — and less meaningful — a sweep becomes. The farther away it sits, the rarer a genuine sweep is, but the more conviction it carries when it happens.**

---

## The Range Itself Is a Second Signal — Independent of Direction

Everything above uses the 7-9am range to set a *directional* bias. The range's raw **size** turns out to carry a separate, useful signal of its own: how much the whole RTH session is likely to move, regardless of which way it goes.

![7-9am range vs RTH range](byakugan_range_correlation.png)

| | Result |
|---|---|
| Correlation (7-9am range % vs. RTH range %) | **r = 0.399** — a real, moderate positive relationship (n=795) |
| RTH range after a wide 7-9am range (above median) | **336pts** |
| RTH range after a narrow 7-9am range (below median) | **244pts** — a 38% gap |

| Quintile | Avg. 7-9am range | Avg. RTH range |
|---|---|---|
| Q1 (narrowest) | 0.207% | 221pts |
| Q2 | 0.302% | 260pts |
| Q3 | 0.397% | 274pts |
| Q4 | 0.534% | 320pts |
| **Q5 (widest)** | **0.984%** | **377pts — 70% larger than Q1** |

**Every step up in 7-9am range size corresponds to a step up in RTH range — no plateau, no threshold, no reversal.** This is genuine volatility clustering, not just a two-bucket artifact of splitting at the median. A wide premarket range isn't only a cue for which direction to lean — it's a leading indicator of how far the session is likely to travel in total.

**Practical use: check this before Stage 3.** A day with an unusually wide 7-9am range should carry wider targets and stops sized to match, independent of what the distance filter says about direction. A narrow 7-9am range is a genuine signal to expect a correspondingly contained session — not just an ambiguous or low-conviction one.

---

## Stage 3 — Trade Planning: The Decision Tree

Use this sequence, in order. **Directional overlay in bold at each step — this is where the carry-driven bullish skew changes the decision, not just the odds.**

1. **Is the AL extreme already swept pre-open?**
   → **Bearish bias:** stand down strictly — this filter is a real anti-signal here (39.9%).
   → **Bullish bias:** optional stand-down — accuracy is mediocre but not clearly harmful (55.2%); a lower-priority filter for this direction.
2. **Is the distance to the AL extreme under 0.15%?** → A sweep here is near-certain but weak (61.1% pooled). Do not treat it as strong confirmation on its own in either direction — look for additional PD array confluence before committing.
3. **Is the distance between 0.30–1.00%?** → **This is the model's target zone, and it works equally well in both directions** (bullish 75.0%, bearish 76.9–77.4%). A genuine NY-session sweep of liquidity this far away is the strongest signal available regardless of bias direction.
4. **Does NY fail to sweep a level sitting 0.15–1.00% away?**
   → **Bearish bias:** treat as a strong, genuine inverse signal (27.3–31.1% — worse than a coin flip). Fade rather than hold.
   → **Bullish bias:** treat as weak grounds to fade — the underlying drift still carries a majority of unconfirmed bullish days to the correct close (63.6% in the 0.50–1.00% band). Prefer standing down over fading a bullish bias on non-confirmation alone.
5. **Is the distance over 1.00%?** → Sample is thin here (n=28 pooled). Default to standing down rather than trading on it, in either direction.

---

## Stage 4 — Trade Execution

- Entry is **not** at the open and **not** on the raw bias alone. Entry is on confirmation that the NY session has genuinely swept the AL extreme in the target-zone distance band (0.30–1.00%), using a PD array (your chosen lowest-timeframe confirmation tool — a gap, an order block, a break-and-retest) forming at or just past that sweep as the specific trigger.
- If the inverse-signal condition fires instead (failure to sweep in the 0.15–0.50% band), the entry logic flips: look for PD array confirmation of a fade *against* the original bias.

---

## Stage 5 — Trade Management: Recalibrated Targets

The raw continuation and terminus levels were tested directly and both need adjustment from their nominal values:

**1.5 continuation — treat as a floor, not a ceiling.**
Hit rate is real (63–66%), but on days that do extend, the *median* actual move is roughly **0.9R beyond the range edge** — nearly double what the 1.5 level itself represents (0.5R). Size targets toward a 2.0–2.5 extension as the realistic expectation once continuation is confirmed, not 1.5.

**−1.5 terminus — treat as an outer boundary, not the average case.**
The median counter-move, when one occurs, is **1.24–1.26R** — short of 1.5R. Unconditionally, only **31.0%** of all days (identical in both NQ and ES) reach the full −1.5 level. Use **−1.25** as the realistic average-case reference for where an adverse move typically stalls; reserve −1.5 as a legitimate but less-likely outer stop-region.

---

## One-Page Summary

1. Mark the 7–9AM range, midpoint, and Asia/London extremes before the open.
2. Determine the raw bias (open vs. midpoint) — **note that bullish bias days run 56.6% accuracy at baseline vs. bearish at 45.1%. NQ's carry-driven upward drift is real and shows up before any refinement.**
3. **Check if the AL extreme is already swept pre-open.**
   - Bearish: stand down strictly (39.9% — a real anti-signal).
   - Bullish: optional filter only (55.2% — mediocre, not clearly harmful).
4. Compute % distance from the open to the AL extreme in the bias direction.
5. **Target zone: 0.30–1.00% distance, genuine sweep.** Strongest signal available, **and it works equally well in both directions** (bullish 75.0%, bearish 76.9–77.4%).
6. **No-sweep in the 0.15–1.00% zone:**
   - Bearish: strong inverse signal — fade it (27.3–31.1%).
   - Bullish: weak grounds to fade — the drift still carries most unconfirmed bullish days correctly (63.6%). Prefer standing down over fading.
7. Entry on PD array confirmation at the sweep (or the bearish fade), not on the raw open.
8. Target 2.0–2.5x the 7–9AM range as the realistic continuation objective; use −1.25R as the realistic average adverse-excursion reference, −1.5R as the outer boundary.

---
*All confidence intervals are 95% Wilson score intervals. Distance, sweep, and directional-asymmetry conditioning tested on NQ; core bias and continuation/terminus recalibration confirmed independently on both NQ and ES. PD array matrix references are generic — apply your own confirmed structure-identification method at the marked levels.*
