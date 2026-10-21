# Five Price Delivery Models
**Built on 833 NQ trading days (2023–2026) · Money management intentionally excluded per request · PD Array Matrix used generically for entry/confirmation timing, since specific structures (order blocks, FVGs, breakaway gaps, mitigation blocks) require pattern recognition beyond what pure OHLC boundary testing can confirm — wherever you see "PD array," read it as "your lowest-timeframe confirmation tool of choice."**

---

## A NOTE ON HONESTY BEFORE ANY MODEL

One piece of grounding testing was done before writing these: does the first 5-minute candle (9:30–9:35) predict which side of the Opening Range eventually breaks out and holds?

**No. It doesn't.** Hold rate when the 5-min candle agreed with the eventual breakout direction: 76.6%. Hold rate when it disagreed: 76.4%. Statistically identical (n=291 vs n=208). **The 9:35 mark in the model below is used for execution discipline — not entering on the raw open print — not because the first candle carries predictive information.** Stating this plainly rather than dressing up a null result as a filter.

---

# MODEL 0 — THE 9:35 OPENING RANGE MODEL

*A single, standalone model — ignore the four "price delivery" models below for this one. Structured in the five stages you'd recognize: Preparation, Opportunity Discovery, Trade Planning, Trade Execution, Trade Management (money management removed per request).*

## Preparation
Note the overnight range (prior day's close through today's 9:30 open) and its midpoint — this level gets revisited during RTH **75.8%** of the time and is a natural point of reference for where the OR sits relative to the day's existing structure. Note whether an NDOG or NWOG sits unfilled nearby (92%+ / 95%+ fill rates within 1–3 days — a real, live magnet if unfilled).

## Opportunity Discovery
- Let the 9:30–9:35 candle print and close. **Do not enter on it — it has no signal value**, per the test above. Its only function here is giving you a clean, closed candle to reference instead of reacting to the raw tick.
- From 9:35 onward, continue building the Opening Range through 10:00. Mark the evolving high and low.
- Watch for a clean **one-sided break**: price exceeding the OR high without also exceeding the OR low, or vice versa. A break of both sides before 10:00 disqualifies the day for this model — no signal.

## Trade Planning
- **Bias is set by which side breaks cleanly, not by the 9:35 candle.** If the high breaks cleanly: bias long. If the low breaks cleanly: bias short.
- Use a PD array (your chosen lowest-timeframe confirmation — a gap, an order block, a break-and-retest) that forms **at or just past the broken OR boundary** as your specific entry trigger, rather than entering on the breakout candle itself.
- Set expectations using the validated projection curve, not a fixed number of points:

| Target | Upside hit rate | Downside hit rate |
|---|---|---|
| 1.0x the OR's own range, beyond its high/low | 28.7% | 28.6% |
| 1.5x the OR's own range | 15.6% | 17.8% |
| 2.0x the OR's own range | 9.0% | 11.8% |

Treat 1.0x as a realistic base target, 1.5x as a stretch target, 2.0x as a runner.

## Trade Execution
- Entry is the PD array confirmation **after** the clean one-sided break — not the breakout candle itself.
- **Base rate for the breakout holding through the close, once confirmed clean and one-sided:** 82.0% (upside) / 70.0% (downside). This is the actual edge of the model — the confirmed breakout, not the raw 9:35 print.

## Trade Management
- If price stalls below the 1.0x target for an extended period, be aware the base rate for reaching even 1.0x is under 30% — this is not a target you should expect on every trade, it's a target you take when offered.
- Be aware of the 10:00–10:30 window specifically: a confirmed reversal (≥40pt retrace against the current move) occurs in this window on **~31% of days** — not the majority, but common enough that a move stalling hard right at 10:00–10:15 deserves attention rather than being assumed to be noise.

---

# THE FOUR PRICE DELIVERY MODELS

Every trading day was classified into one of four states — Expansion, Retracement, Reversal, Consolidation — based on range and directionality relative to a trailing 20-day average. Frequencies and session-by-session behavior below are real, tested numbers, not descriptions.

| State | Frequency | Most likely to follow |
|---|---|---|
| Retracement | 41.7% | Itself (45%) |
| Consolidation | 29.7% | Itself (44%) |
| Reversal | 15.0% | Retracement (46%) |
| Expansion | 13.5% | Retracement (42%) |

---

## MODEL 1 — "DOMAIN EXPANSION"
### *(Expansion Model — the rare, high-magnitude directional day)*

**Why this name:** a Domain Expansion is a technique that forces the entire battlefield onto your terms — total, overwhelming control of the space. That's an expansion day: it's rare (13.5% of days) but when it's live, it dominates the session and everything else becomes secondary.

### Preparation
Expansion is a transitional state — it follows Retracement 42% of the time and Reversal 22% of the time, but almost never follows itself (13%). **Do not hunt for expansion the day after an expansion day.** The highest-probability setup window is a day emerging from an extended Retracement or Consolidation stretch.

### Opportunity Discovery — Session by Session
This model lives or dies on which session's opening 30-minute block you're trading:

| Session | Opening-block breakout hold rate |
|---|---|
| **London (02:00–02:30)** | **79.5%** — the strongest session for this model, by a wide margin |
| NY PM (13:30–14:00) | 69.6% |
| Asia (20:00–20:30) | 68.8% |
| NY AM (09:30–10:00) | 60.8% — the *weakest* despite being the most volatile session of the day |
| NY Lunch (11:30–12:00) | 59.3% |

**The counterintuitive core of this model: NY AM is not your best expansion hunting ground, despite being the loudest.** London is quieter but far more decisive. If you're specifically hunting a Domain Expansion day, weight London heavily.

### Trade Planning
- Mark the session's opening 30-minute range. A clean one-sided break of it is your trigger.
- Use a PD array forming at the break for entry confirmation.
- Reference the 20-day trailing average range for that session — true expansion is range >125% of that average with a strongly directional close (>55% of the range in one direction).

### Trade Execution
- Enter on PD array confirmation following the clean break, in the direction of the break.
- **Given a genuinely expanding session, morning-range size predicts full-day range with r=0.783–0.919** depending on instrument — once NY AM's opening block is visibly wide, expect the whole day to be wide, and size targets to the day, not just the session.

### Trade Management
- Do not expect a second consecutive expansion day. Plan the exit for this leg specifically — don't hold into the next session assuming continuation, since the base rate says Retracement (42%) is the far more likely next state.

---

## MODEL 2 — "SHIKAI"
### *(Retracement Model — the default, most common state)*

**Why this name:** Shikai is the first, contained release — real power, but held back, not yet the full form. Retracement is exactly that: genuine two-sided movement, real range, but not a clean directional kill. It's the most common state in the market (41.7% of days) — the bread-and-butter, not the spectacular.

### Preparation
Retracement is the **stickiest non-consolidation state** — 45% chance of following itself, meaning if yesterday was a retracement day, today probably is too. This model is built for grinding, two-sided sessions, not trend days.

### Opportunity Discovery — Session by Session
This model targets **mean-reversion to already-established reference levels**, since retracement days are defined by two-sided movement around a center rather than a clean directional push:

- **Overnight range 50% midpoint:** retraced during RTH **75.8%** of the time — the single most reliable magnet level in the entire framework, and the anchor of this model
- **Peak-volatility-block midpoint retracement** (the most active 30-min stretch of a session, retraced afterward): Asia 69.6%, NY PM 69.3%, London 62.8% — **NY AM is the exception at 52.7%, close to a coin flip.** Don't run this model off an NY AM peak block.
- **Lunch-range breakout into PM:** 61.3% — a smaller, session-local version of the same mean-reversion logic

### Trade Planning
- Mark the overnight range midpoint before the open — this is your primary target zone for the day, regardless of which session you're trading.
- Within a session, mark its most volatile 30-minute block once it's formed, and treat its midpoint as a secondary retracement target — except in NY AM, where this specific tool doesn't work.

### Trade Execution
- Entry is on a PD array confirming a stall or rejection near a prior extreme, aiming back toward the marked midpoint(s) — not a breakout entry, a fade-back-to-center entry.
- This model is explicitly **not** a breakout model. If price is cleanly breaking and holding beyond the OR (Model 0's territory), that's a different day-type; don't force Shikai onto an expansion day.

### Trade Management
- Retracement's own stickiness (45% self-continuation) means a losing Shikai setup is more likely to be followed by another retracement opportunity than by a trend day — don't abandon the model after one loss on the assumption the character of the day has changed.

---

## MODEL 3 — "GENJUTSU KAI"
### *(Reversal Model — built on SMT divergence)*

**Why this name:** "Kai" means release — specifically, the technique used to break a genjutsu, an illusion cast over the battlefield. That's precisely what an SMT divergence is: the current move is revealed to be an illusion the moment a correlated instrument refuses to confirm it, and price snaps back through the level as the illusion breaks.

### Preparation
This is the strongest signal validated anywhere in this framework. Reversal itself is a fairly rare state (15.0% of days) — but SMT divergence is the tool that flags it in real time rather than after the fact.

### Opportunity Discovery — Session by Session
Track NQ against a correlated index (ES) session by session. A divergence forms when one index prints a fresh session/day extreme that the other fails to confirm.

| Session where divergence forms | Occurrences (n) | Retrace-through rate |
|---|---|---|
| **London** | 31 (bear) / 34 (bull) | **96.8% / 94.1%** |
| NY AM | 58 / 87 | 87.9% / 93.1% |
| NY Lunch | 52 / 42 | 84.6% / 97.6% |

**London-session divergences are the cleanest signal in this entire body of work — nearly 97% retrace-through.** Every session tested clears 85%+, making this the most session-independent, reliably strong model of the four.

### Trade Planning
- **Be precise about what this promises.** The retrace-through rate (85–97%) means price reliably trades back through the level it was at *before* the divergent extreme formed. The **day closing fully reversed** is a separate, much weaker statistic — close to a coin flip (~50–54%). Plan the primary objective around the retracement, and treat a full reversal as a bonus, not the base case.
- No PD array is strictly required to identify the setup itself — the divergence is the signal. Use a PD array on the entry timeframe purely for precise entry timing once the divergence is confirmed.

### Trade Execution
- Once NQ prints a fresh high (or low) that the correlated instrument does not confirm, that is the trigger. Enter on confirmation of the reversal beginning — a PD array close back inside the prior range is a reasonable trigger.
- Target: the level NQ was at immediately before the divergent extreme formed. This is the level with the 85–97% hit rate — not a fixed point projection.

### Trade Management
- Manage the trade as a retracement play primarily. If the day-close reversal (the bonus outcome) starts developing — confirmed by the broader session character continuing against the original move — that's earned information to hold for more, not something to assume from the outset.

---

## MODEL 4 — "KEKKAI BARRIER"
### *(Consolidation Model — the contained, range-bound state)*

**Why this name:** a Kekkai is a barrier technique — a bounded field that contains whatever's inside it. Consolidation is exactly that: a range the market can't break, and won't, until something changes the terms.

### Preparation
**Consolidation is the single stickiest state in the entire model** — 44% chance of remaining consolidation the following day, higher self-continuation than any other state including Retracement. If you identify a consolidation day, the highest-probability expectation for tomorrow is more of the same, not a breakout.

### Opportunity Discovery — Session by Session
This model targets the flattest, most range-bound stretches of the day directly:

- **NY PM, 13:30–15:00 specifically** is the quietest stretch of the entire RTH session — four consecutive 30-min blocks sitting in a tight band with minimal variation between them, before a closing-auction spike at 15:30–16:00
- **NY Lunch (11:30–13:00)** broadly: narrow consolidation (range <70% of a typical hour) occurs **38.3%** of days, and reversal-or-consolidation combined occurs **69.2%** of days — lunch is a low-conviction, range-favoring window more often than not
- **NY AM's quietest 30-min block (10:30–11:00)** is still the least volatile part of the morning, though nowhere near as flat as the PM dead zone

### Trade Planning
- Once a session's range has been established and 2–3 consecutive 30-minute blocks show compressed, similar ranges, treat the session's extremes as the container walls.
- Fade toward the center on approach to either wall, using a PD array at the wall itself (a rejection candle, a failed break-and-return) as entry confirmation.
- This model explicitly does **not** apply during NY AM's opening 30 minutes (09:30–10:00) — that block is the most volatile of the entire day and is structurally the wrong environment for this model.

### Trade Execution
- Entry is a fade at the established range wall, on PD array rejection confirmation, targeting the opposite wall or the range midpoint.
- Given the wide (44%) self-continuation rate, a Kekkai Barrier setup that fails to hold today is still reasonably likely to have another opportunity form tomorrow in the same instrument.

### Trade Management
- Watch specifically for the transition signal: Consolidation → Consolidation is 44%, but Consolidation → Retracement is 35% — a real possibility of the range starting to lean directionally without fully breaking. If price is walking one wall repeatedly without touching the other, that's the barrier starting to give, and this model should be stood down in favor of Model 1 (Domain Expansion) or Model 2 (Shikai) forming instead.

---

# HOW THE FOUR MODELS RELATE

The transition table is the map between all four:

**Expansion → mostly Retracement (42%)** → use Shikai once the expansion leg is spent
**Retracement → mostly itself (45%), sometimes Consolidation (27%)** → Shikai is genuinely the default; expect to be running it most often
**Reversal → mostly Retracement (46%)**, but also a real chance of fresh Expansion (22%) → Genjutsu Kai's retrace-through target often *is* the handoff into a new Shikai setup
**Consolidation → mostly itself (44%)** → Kekkai Barrier persists; watch for the 35% chance of a shift into Shikai as the range starts to lean

**In practice:** most days are Shikai (Retracement) days wearing a Kekkai Barrier (Consolidation) costume for part of the session. Domain Expansion (true Expansion) is the rare, valuable exception — and Genjutsu Kai (SMT-confirmed Reversal) is your highest-conviction tool for catching the exact moment one state's illusion breaks and hands off to the next.

---
*All confidence intervals are 95% Wilson score intervals unless noted. PD array matrix references are intentionally generic — specific structure identification (order blocks, fair value gaps, breakaway gaps, mitigation blocks) requires visual/pattern confirmation beyond what OHLC boundary testing alone can validate; apply your own confirmed method at the marked levels.*
