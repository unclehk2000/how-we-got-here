# MODEL 2 — "SHIKAI"
> **Oct 2026 re-test:** the overnight midpoint is reached about as often as a level the same distance from the open on the *other* side. The touch rates are real distance/volatility facts, but the midpoint itself is not a magnet, and the prior-day-state tables do not hold against that placebo. Shikai is now used as a confluence map. See "Re-test (Oct 2026)" below.

### The Retracement Model — Broad, All-Session Framework
**Built on 531–873 NQ trading days (2023–2026) · Money management intentionally excluded**

---

## Why This Name
Shikai is the first, contained release — real power, but held back, not yet the full form. Retracement is exactly that: genuine two-sided movement, real range, but not a clean directional kill. It's the most common state in the market — the bread-and-butter, not the spectacular.

**This is the broad framework, covering all sessions.** For the tightest, time-bound NY AM-specific execution version of the overnight-midpoint tool, see Model 2B ("Bankai") — that document owns the minute-by-minute NY AM entry mechanics; this one covers the full-day picture and the other three sessions in depth.

---

## What "Retracement" Means Here
**Frequency: 41.7% of days — the single most common state, more common than the other three combined states are individually.** Stickiness: a Retracement day is followed by another Retracement day 45% of the time — the highest self-continuation of any state.

---

## Stage 1 — The Universal Anchor: Overnight Range Midpoint

### The honest rate
The overnight midpoint (prior 18:00 close through today's 9:30 open) is retraced during RTH:

| | Rate |
|---|---|
| Unconditional (includes trivial near-open cases) | 75.8% |
| **Meaningful-distance subset (open ≥0.15% from midpoint) — use this number** | **67.4%** (CI 63.3–71.3%) |

### The full target ladder (direction-relative, from the open toward the far overnight extreme)

| Distance from open | Hit rate |
|---|---|
| 1/8 (12.5%) | 88.7% |
| 2/8 (25.0%) | 79.3% |
| 3/8 (37.5%) | 69.7% |
| **4/8 (midpoint)** | **61.4%** |
| 5/8 (62.5%) | 53.9% |
| 6/8 (75.0%) | 46.5% |
| 7/8 (87.5%) | 41.2% |

### Timing — most of the opportunity is front-loaded across the whole day too
38.8% of retraces occur in the 9:30–10:00 window alone, and nearly 90% of all retraces that happen, happen by 11:00 AM. Past 11:00, treat an untouched midpoint as fading, not pending — see Bankai for the precise minute-level breakdown if trading this specifically in NY AM.

### Post-touch caution — applies everywhere
Once the midpoint is tagged, continuation-through vs. bounce-back is a **coin flip** (48.6% / 51.4%). The touch is not the signal — it's the point where you need independent confirmation (a PD array reaction) before assuming direction.

---

## Stage 2 — Session-Specific Tools and Their Conditioning

Beyond the overnight midpoint, each session has its own hottest-30-minute-block midpoint as a secondary target. **Critically, which prior-day state (yesterday's price-delivery classification) sharpens this tool is different for every session — there is no universal rule.**

| Session | Unconditional hot-block retrace | Best conditioning | Worst conditioning |
|---|---|---|---|
| **Asia** | 69.6% | **Yesterday = Consolidation: 73.1%** | Yesterday = Retracement: 64.2% |
| **London** | 62.8% | Little differentiation (59.7–67.3% across all four states) | — |
| **NY AM** | 52.7% — **do not use this tool here at all**, coin flip regardless of conditioning | — | — |
| **NY PM** | 69.3% | **Yesterday = Reversal: 76.2%, Expansion: 75.6%** | Yesterday = Retracement: 64.0% |

**NY PM is the mirror image of NY AM.** For a NY-AM-specific trade (see Bankai), a grinding prior day (Retracement or Consolidation) produces the cleanest setup. For NY PM, it's the *opposite* — a big directional or reversal day yesterday sets up the more reliable afternoon retracement, while a grinding prior day actually weakens it here. **Don't apply the NY AM conditioning logic to NY PM — they run in opposite directions.**

**London shows almost no differentiation by prior-day state** (all four states cluster in the high-50s to high-60s) — this conditioning layer isn't worth applying there; just use the flat 62.8% baseline.

### Full detail by session and prior-day state

**Asia:**
| Yesterday's state | Retrace rate |
|---|---|
| Consolidation | 73.1% (CI 67.0–78.5%) |
| Reversal | 67.2% (CI 58.3–75.1%) |
| Expansion | 66.7% (CI 57.2–75.0%) |
| Retracement | 64.2% (CI 58.9–69.2%) |

**London:**
| Yesterday's state | Retrace rate |
|---|---|
| Reversal | 67.3% (CI 57.8–75.6%) |
| Expansion | 65.6% (CI 55.7–74.4%) |
| Consolidation | 61.2% (CI 54.3–67.7%) |
| Retracement | 59.7% (CI 54.1–65.1%) |

**NY PM:**
| Yesterday's state | Retrace rate |
|---|---|
| **Reversal** | **76.2%** (CI 65.9–84.2%) |
| **Expansion** | **75.6%** (CI 65.1–83.8%) |
| Consolidation | 70.3% (CI 62.5–77.0%) |
| Retracement | 64.0% (CI 57.4–70.1%) |

---

## Stage 3 — The Big-Range-Day + Choppy-Overnight Setup (NY AM Specific)

A separate, validated conditioning specific to NY AM: when yesterday's RTH range exceeded 115% of its own trailing 20-day average **and** the overnight into today was choppy (|net|/range < 0.35), the overnight-midpoint retrace rate during NY AM rises to **75.3%** (vs. 65.5% baseline). London's **full session range** midpoint (not just its hot block) also becomes a viable secondary tool under this same setup — **69.9%**, up from 60.8% unconditionally. Asia's full-session version does not show this improvement and should stay on its hot-block tool.

**Tested and ruled out under this setup:** the idea that NY AM reverses direction from yesterday — 48.9% vs. 47.5% baseline, no meaningful difference. This setup sharpens the *midpoint-retrace* odds specifically, not a directional call.

---

## Stage 4 — Trade Execution

1. Mark the overnight midpoint before the open; confirm the open sits a meaningful distance from it (≥0.15% of price) before treating this as a real setup.
2. Identify which session you're trading and apply that session's specific conditioning rule from Stage 2 — not a universal one.
3. If trading NY AM specifically with the big-range + choppy-overnight setup active, weight conviction up (75.3%) and consider London's full-session-range midpoint as an added tool.
4. Entry is a fade — a PD array (your chosen confirmation tool) confirming a stall or rejection near the marked level.
5. This is explicitly **not** a breakout model — if price is cleanly breaking and holding beyond an established range, that's Model 1 territory.

---

## Stage 5 — Trade Management

- At the touch, require independent confirmation before assuming direction — continuation vs. bounce is a coin flip everywhere this was tested.
- Respect the timing decay — most opportunity is front-loaded early in whichever session you're trading.
- A loss doesn't mean abandon the model — Retracement days persist (45% self-continuation); check whether the broader day-type has genuinely changed before stepping away.
- **Never use the hot-block-midpoint tool in NY AM under any conditioning** — it's a coin flip (52.7%) regardless of yesterday's state. Use Bankai's overnight-midpoint framework for that session instead.

---

## Re-test (Oct 2026)

**Method.** NQ 1-min data (2018, 2022–Aug 2026); trained on 2018–24, checked on 2025–26. The overnight range runs 18:00–09:29 ET, and only meaningful-distance days count (open ≥0.15% from the midpoint; 860 days). The **placebo** is a mirror level: the same distance from the 09:30 open, on the opposite side. If the midpoint were special, it would be hit more often than its mirror. Scripts: `Shikai_Bankai/retest.py`, `Shikai_Bankai/hot.py`.

| Overnight midpoint reached | Midpoint (train → test) | Mirror (train → test) |
|---|---|---|
| By 16:14 (RTH) | 70.4% → 65.8% | 68.8% → 64.9% |
| By 11:00 | 58.0% → 54.5% | 55.3% → 54.1% |
| By 10:00 | 43.1% → 37.2% | 36.7% → 39.8% |

- **Ladder (RTH reach, eighths counted from the extreme on the open's side):** 1/8 94%, 2/8 85%, 3/8 79%, 4/8 69%, 5/8 61%, 6/8 52%, 7/8 43%. It is a distance ladder: the further a level is, the less often it's reached.
- **Post-touch:** price goes on through vs bounces back 48.7% vs 51.3%, a coin flip. This confirms the original finding.
- **Big-range day + choppy overnight (Stage 3):** the midpoint is hit by 11:00 67% (train) and 69% (test, n 13), but its mirror is hit just as often (69%, 69%). The setup predicts **more travel in both directions**, not a midpoint pull.
- **Prior-day state:** midpoint minus mirror swings between −10 and +10 points across states and periods. Consolidation is the only state ahead in both periods (+5 train, +10 test, n 57), which is too small and too unstable to use.

**Hot-block midpoint, real-time version.** The widest 30-minute block *so far* is known at its close. The original figures used the session's true hottest block, which is only known in hindsight.

| Session | Midpoint reached by session end (train → test) | Mirror |
|---|---|---|
| Asia | 70.2% → 69.3% | 68.9% → 67.5% |
| London | 63.1% → 63.2% | 61.7% → 62.1% |
| NY AM | 59.2% → 53.2% | 62.3% → 57.7% |
| NY PM | 70.8% → 73.3% | 71.4% → 65.3% |

The hot-block midpoint is no better than an equal-distance level in any session (NY PM test +8 vs train −1). The prior-day conditioning tables in Stage 2 don't separate from the mirror either.

**Verdict.** The reach rates are honest as *how far price usually travels* figures, and they work as target odds and a volatility map. They are **not** a directional or magnet edge. Probability that an overnight-midpoint fade beats the always-long carry benchmark after costs on new data: **about 10%**.

---

## Carry-charge use (Oct 2026)

NQ is a carry-charge market, so the long side is the one expected to hold up. Two intraday uses were tested on meaningful days. Trained on 2018–24, checked on 2025–26, with a cost of 1 pt round trip. Scripts: `Shikai_Bankai/carry.py`, `Shikai_Bankai/fade.py`.

**1. Trading INTO the midpoint from the 09:30 open.** Target is the midpoint and the stop is the mirror, so this is a symmetric race.

| | 16:14 (train → test) | 11:00 (train → test) |
|---|---|---|
| LONG into mid (open below mid) | +0.023R → +0.025R (53% → 52%) | +0.010R → +0.023R |
| SHORT into mid (open above mid) | +0.027R → −0.050R (52% → 47%) | +0.006R → −0.073R |

Only the long side stays positive out of sample, which is the carry asymmetry. The size is tiny (+0.02R, t 0.5), though. In 2025–26 a long with the same distances worked about as well whichever side the midpoint was on, so the carry is doing the work, not the midpoint.

**2. Go through the midpoint, then trade back out of it (reclaim).** The entry is the first 1-min close back on the approach side after price trades through. The stop is the sweep extreme minus 1 tick, and the target is 1R.

| | Train | Test |
|---|---|---|
| LONG reclaim (with carry) | −0.22R, 45% win | −0.09R, 49% win |
| SHORT reclaim (against carry) | −0.09R, 51% win | −0.09R, 49% win |

The long reclaim pooled is −0.19R (t −3.1). **A tight stop under the sweep extreme loses.** The 3/8, 5/8 and mirror levels show the same thing, so this is the entry structure failing, not the level.

**3. The carry foothold (discount mirror).** When the open is below the overnight midpoint (discount), the mirror sits the same distance *below* the open. Buy the first touch there, with a stop 0.5× that distance beyond and the target back at the open (2R):

| | Train | Test | Pooled |
|---|---|---|---|
| LONG at the discount mirror | +0.08R (39% win, n 201) | +0.18R (41%, n 64) | +0.105R, t 1.2 |
| SHORT at the premium mirror (open above mid, price pops the same distance above the open) | −0.22R (n 232) | −0.28R (n 86) | **−0.236R, t −3.3** |

The long−short gap is about +0.34R (t ≈ 3.0), and that is the carry effect in this model. **Don't fade the premium pop short.** The long foothold is a lean, not a proven edge. Probability it holds at ≥ +0.1R after costs on new data: **about 25%**.

**How to use it intraday.**
- **Into the point:** treat the midpoint as a target. Favour it when it is above the open (the long side). A short into a midpoint below the open is against carry, and it was negative in 2025–26.
- **Through and back out:** don't enter on the first reclaim close with a stop at the sweep extreme, because that tested clearly negative. The reversal at the level is a coin flip either way, so it needs your own confirmation and a wider stop.
- **Carry foothold:** on discount opens, a drop to the mirror is the long-side area to watch. On premium opens, a pop to the mirror is not a short.

---

## Session candles + London 25% (merged into the Session Map indicator, Oct 2026)

Sessions: Asia 18:00–01:59, London 02:00–07:59, NY 08:00–16:59 ET. NQ, trained on 2018–24 and checked on 2025–26. Script: `Shikai_Bankai/src25.py`.

- **Regime (London vs Asia) → NY bullish:** all days 51.2% → 53.3% (the carry baseline). By regime:
  - London partial up: 53.8% → 49.4%
  - London partial down: 48.5% → 56.1%
  - London engulfs Asia: 53.5% → 72.5% (n 40)
  - Asia engulfs London: 45.2% → 44.9% (n 93 / 49)

  Only "Asia engulfs London" leans the same way in both periods, below the long baseline, and the samples are small.
- **London 25% level:** NY stays on the right side of it only 5–10% of the time. After a wick through it, NY closing back on the London side vs not is about 50/50 (bull London: 50.4% / 44.5% train, 46.5% / 43.7% test).

**Verdict:** the 25% level is not a barrier, and the regime split doesn't beat the carry baseline. The indicator computes all of these live from chart history and shows the all-days baseline beside them.

---

## One-Page Summary

1. This is the default day-type — expect to be running this model more often than any other.
2. **Overnight midpoint, honest rate: 67.4%.** Full target ladder available for graduated targets (88.7% → 41.2% across the eighths).
3. **Session-specific conditioning is NOT universal** — check the right table before applying it:
   - Asia: best after Consolidation (73.1%)
   - London: flat across all states, don't bother conditioning (62.8% baseline)
   - **NY PM: best after Expansion or Reversal (75–76%) — opposite of NY AM's pattern**
   - NY AM: use Bankai (Model 2B) instead of the hot-block tool, which is a coin flip here regardless
4. **Post-touch continuation vs. bounce is always a coin flip** — require independent confirmation everywhere.
5. Big-range-day + choppy-overnight setup: boosts NY-AM midpoint retrace to 75.3% and makes London's full-session-range midpoint viable (69.9%).
6. Entry is a fade toward the marked level, not a breakout chase.
7. A loss doesn't mean abandon the model — persistence is real (45% self-continuation).

---
*All confidence intervals are 95% Wilson score intervals. PD array matrix references are generic — apply your own confirmed structure-identification method at the marked levels.*
