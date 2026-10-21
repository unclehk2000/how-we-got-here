# MODEL 0 — Opening Range & Execution Range Model
**Built on 833 NQ trading days (2023–2026) · Money management intentionally excluded · All figures are tested, not theoretical**

---

## Two Honest Null Results First

**1. The 9:30–9:35 candle has no predictive value on its own.**
Tested three separate ways:
- As a filter for which side the Opening Range eventually breaks: hold rate when the candle agreed with the eventual breakout direction was 76.6%; when it disagreed, 76.4%. Identical.
- As a standalone momentum entry (enter at 9:35 in the candle's direction, check if price continues that way): **51.9%** — a coin flip.

**Do not use the first 5 minutes as a signal.** It has a role in this model, but only as an execution-discipline marker (a clean closed candle to reference instead of the raw open print), not as information.

**2. The Execution Range is a confirmation and targeting tool — not an extreme-caller.**
It contains the day's actual high only 5.8% of the time and the day's low only 8.2% of the time. Don't use it to guess where the session will top or bottom. Its real value is below.

---

## The Two Ranges

**Opening Range (OR): 9:30–10:00 ET.** The foundational range of the day.

**Execution Range (ER): 10:00–10:18 ET.** The 18 minutes immediately following the OR's close — where the OR's breakout signal actually resolves.

### Why 10:00–10:18 specifically
The OR is defined through 10:00, so no valid breakout can be confirmed before the range finishes forming — there is no real signal available before 10:00 no matter how price is behaving in the 9:50–10:00 stretch. Once the OR closes, the breakout timing was tested directly:

| When the confirmed breakout bar fires | Share of all breakouts |
|---|---|
| **10:00–10:18 (the Execution Range)** | **72.3%** (CI 68.3–76.1%) |
| 10:18–10:30 | remainder of the 10:00–10:30 window |
| After 10:30 | 16.6%, and the lowest-quality tail |

**Nearly three-quarters of all OR breakout signals fire inside this 18-minute window.** This is where the actual decision happens.

---

## The Model

### Stage 1 — Preparation
Before the open, note:
- The overnight range and its midpoint (retraced during RTH 75.8% of the time — useful context, not a trade trigger for this model)
- Any unfilled NDOG/NWOG nearby

### Stage 2 — Opportunity Discovery
- Let the OR build fully, 9:30–10:00. Mark its high and low as it forms.
- **Do not act on anything before 10:00.** The 9:35 candle, the 9:50 print, none of it carries a validated signal in isolation.
- At 10:00, the OR is complete. Begin watching for a clean **one-sided break** — price exceeding only the OR high or only the OR low, not both.

### Stage 3 — Trade Planning
- Bias is set by which side of the OR breaks cleanly.
- **The Execution Range confluence check is the core edge of this model:**

| Condition | Hold-to-close rate |
|---|---|
| Execution Range's own net direction (10:00–10:18 open-to-close) **agrees** with the OR breakout direction | **79.2%** (CI 74.8–83.1%) |
| Execution Range's net direction **disagrees** with the breakout | 68.5% (CI 60.0–75.9%) |

An 11-point gap with non-overlapping confidence intervals. This is a real, usable filter: don't just take the OR breakout at face value — check whether the Execution Range itself is confirming it before committing size.

### Stage 4 — Trade Execution
- Use a PD array (your chosen lowest-timeframe confirmation tool — a gap, an order block, a break-and-retest) forming inside the Execution Range as the specific entry trigger, once direction is confirmed by the confluence check above.
- Baseline OR breakout hold rates for reference: 82.0% (upside) / 70.0% (downside) — the Execution Range confluence check pushes the higher-quality subset of these trades toward ~79%, and flags the weaker subset (~69%) for reduced conviction rather than automatic entry.

### Stage 5 — Trade Management
**Targets — layered, from two independent range measurements:**

*From the Opening Range itself:*
| Multiple | Upside hit rate | Downside hit rate |
|---|---|---|
| 1.0x OR range | 28.7% | 28.6% |
| 1.5x OR range | 15.6% | 17.8% |
| 2.0x OR range | 9.0% | 11.8% |

*From the Execution Range, once it has formed (a second, closer-in layer):*
| Multiple | Upside hit rate | Downside hit rate |
|---|---|---|
| 1.0x ER range | 43.6% | 40.5% |
| 1.5x ER range | 28.7% | 29.2% |
| 2.0x ER range | 18.7% | 21.8% |

The ER-based targets hit more often since they're measured from a point already closer to the current move — treat the 1.0x ER target as the realistic first objective, the OR-based 1.0x/1.5x as the stretch objectives beyond it.

**Reversal watch:** a confirmed reversal (≥40pt retrace against the move) occurs in the 10:00–10:30 window on ~31% of days. If price stalls hard right after entry without extending toward even the 1.0x ER target, treat that stall as a real, non-trivial possibility rather than assumed noise.

---

## One-Page Summary

1. Ignore everything before 10:00 — the OR needs to finish forming, and the 9:35 candle is not a signal.
2. At 10:00, mark the OR high/low. Wait for a clean one-sided break.
3. Check the Execution Range's own direction (10:00–10:18) against the break — agreement = ~79% hold rate, disagreement = ~69%.
4. Enter on PD array confirmation inside the Execution Range.
5. Target the ER-based 1.0x level first, OR-based levels as stretch/runner targets.
6. Respect the ~31% chance of a genuine reversal forming before 10:30 if the move stalls.

---
*All confidence intervals are 95% Wilson score intervals. PD array matrix references are generic — apply your own confirmed structure-identification method at the marked levels.*
