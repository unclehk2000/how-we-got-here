# MODEL 4 — "KEKKAI BARRIER"
> **Oct 2026 update:** the Phase 3 trade statistics did not survive a re-test. Kekkai is now used as a confluence map (Section "Session-on-session Kekkai"). The indicator draws walls, sweeps and shifts only.

### Consolidation Attack — Seek-and-Destroy Execution Framework
**379 Consolidation days, 2018/2022/2023–2026. NFP Fridays excluded.**

Yesterday's Consolidation range is the hunting ground. Both walls get hunted before the real move commits — don't mistake the hunt for the kill.

---

## Setup (before the session)

- Confirm yesterday's RTH range was under 75% of its own trailing 20-day average → **Consolidation confirmed.**
- Mark yesterday's RTH high and low. These are the walls being hunted today — **treat them as bait, not safety.** A container that's held is a container that's about to get tested harder.
- Ignore session counts. Two quiet days don't compress a third into expansion (4.8% vs. 13.3% baseline) — the trigger is structural, not a timer.

---

## Phase 1 — 9:30–10:18 (fires every day, Consolidation or not)

1. Mark the Opening Range (9:30–10:00).
2. Watch the Execution Range (10:00–10:18) — **72.3% of breakouts fire here.**
3. Net direction in the Execution Range agreeing with the OR break → **79.2% hold.** Disagreeing → **68.5%.**
4. Enter on PD array confirmation at the OR boundary. Targets: 1x/1.5x/2x off the OR (≈29%/16%/9–12% hit rates — take the 1x, don't chase 2x).

---

## Phase 2 — Hunt the Walls (10:18 → structural shift, Consolidation-trigger days only)

5. Fade yesterday's walls until the shift confirms. Target the opposite wall or midpoint. **This is the hunt, not the kill — don't oversize it.**
6. Watch for the shift: **two consecutive 30-min blocks, each printing a higher high + higher low (bullish) or lower low + lower high (bearish).**
7. This cannot confirm before ~11:00 — three full blocks are required. **Extend your watch to 11:30, not 11:00.** A real ~19% of confirmations land in that extra half hour, outside where a rigid session boundary would tell you to stop looking.
8. Fires one direction or the other **98.9%** of the time.

| Confirmation window | Share |
|---|---|
| **10:30–11:30** | **66.7%** |
| 11:30–13:00 | 24.5% |
| 13:00–14:30 | 7.5% |

---

## Phase 3 — The Strike (mechanics as originally written; see re-test below)

9. **Entry: at the break itself** — the level that confirms the shift (pre-shift block's high, bullish; low, bearish). This is the tested entry. Waiting for a retest/sweep back into a gap before entering is a valid discretionary tightening, but it was not what was simulated — don't assume the numbers below apply to a delayed entry.
10. **Stop: the pre-shift block's opposite extreme** — its low for a bullish entry, its high for a bearish one. This makes your risk exactly **1R = 1x the pre-shift block's own range**, by construction. No alternate stop placement was tested.
11. **At entry, size for two exits, not one:**
    - **Tier 1 — take 50% off at 0.5R.** Once hit, move the stop on the remaining size to breakeven (your entry price). This step is what turns most losing trades into scratches instead of full losses.
    - **Tier 2 — run the rest to the full target:** **1.0R if bullish, 1.5R if bearish.** Close there. Extending past this wasn't part of the tested mechanic — treat anything beyond as discretionary.
12. If price never reaches Tier 1, the full position stays at the original 1R stop.

### Re-test of this mechanic (Oct 2026): the earlier performance table is withdrawn

The original table (91% any-profit, +0.43R / +0.57R per trade) could not be reproduced. The code that produced it is no longer available.

**Re-test.** The rules were re-implemented exactly as written: entry at the pre-shift block's extreme, stop at its other extreme, 50% off at 0.5R with the stop to breakeven, and the rest to 1.0R (bull) / 1.5R (bear). The sample is the NQ 1-min data (2018, 2022–Aug 2026), after Consolidation days, with NFP Fridays excluded.

| Fill assumption | Trades | Any profit | Avg R |
|---|---|---|---|
| "As written": filled at the pre-shift extreme at confirmation | 361 | 67.6% | +0.09R |
| Market entry at confirmation | 361 | 65.7% | +0.06R (t ≈ 1.3) |
| Resting limit at the pre-shift extreme (78% get filled) | 281 | — | +0.00R |

- **Why "any profit" misleads.** With this exit, about two trades in three touch +0.5R before −1R even from random entries. A 66% any-profit rate is what the exit structure produces on its own, and the average R is not distinguishable from zero.
- **Status.** The trade mechanic is **not an edge**. Kekkai is kept as a **context and confluence map**: walls, sweeps and structural shifts. It is no longer a trade trigger, and the indicator no longer draws entries or targets.

---|---|---|---|
| Bullish (Tier 2 = 1.0R) | **91.1%** | 8.9% | +0.43R |
| Bearish (Tier 2 = 1.5R) | **91.7%** | 8.3% | +0.57R |

Bearish setups produce both the higher any-profit rate and the better average return — consistent with the asymmetry throughout this model. Trades that never resolve by session close are excluded from these rates and don't get carried overnight.

---

## Phase 4 — Lunch (1:31–3:00), only if still unresolved

13. Same entry/stop/two-tier mechanic as Phase 3. **Do not target the opposing side of the Lunch range** — tested and unreliable (under 10% either way) regardless of what triggered the setup.

---

## No Shift by 11:30

14. Back to Phase 2 fade logic for the rest of the session. Consolidation is sticky (44% self-continuation) — an unresolved day is a live candidate to reset and hunt again tomorrow.

---

## Checklist

**Pre-session**
1. Yesterday's RTH range < 75% of trailing 20-day avg → Consolidation confirmed
2. Yesterday's RTH high/low marked as today's hunted walls

**9:30–10:18**
3. OR marked (9:30–10:00)
4. Execution Range break confirmed (10:00–10:18), net direction checked for agreement
5. Entry on PD array at OR boundary → target 1x (don't chase 2x)

**10:18–11:30**
6. Fading walls until shift confirms — sized small, hunt only
7. Two consecutive 30-min blocks: HH+HL (bullish) or LL+LH (bearish)
8. Still watching through 11:30, not stopping at 11:00

**On shift confirmation**
9. Stop fading
10. Enter at the break level itself (pre-shift block's high/low)
11. Set initial stop at pre-shift block's opposite extreme (= 1R)
12. Tier 1: take 50% off at 0.5R, move stop on remainder to breakeven
13. Tier 2: run remainder to 1.0R (bullish) / 1.5R (bearish), close there

**1:31–3:00 (if still unresolved)**
14. Same entry/stop/two-tier mechanic — not the opposing Lunch-range wall

**No shift by 11:30**
15. Back to wall-fade logic for the session; re-check setup validity tomorrow

---

## Session-on-session Kekkai (ETH confluence version, Oct 2026)

**The chain.** Each high-volatility window hunts the walls of the window before it.

| Session (ET) | Its walls | Role |
|---|---|---|
| Asia 20:00–00:00 | prior RTH high / low | **wall builder only**: quiet, and its own shifts are noise |
| London 02:00–05:00 | Asia high / low | hunt session |
| NY AM 09:30–11:30 | London high / low (plus yesterday's RTH walls) | hunt session |

**Definitions.**
- **Sweep:** price trades beyond the earlier session's high or low.
- **Shift:** two consecutive 30-minute blocks printing HH+HL (bull) or LL+LH (bear) inside the session. In Asia, 15-minute blocks produce a "shift" in 99% of sessions, which is why Asia is used only to build walls.
- **Reversal:** a sweep of one wall followed by a shift *away* from it, i.e. hunt then kill.

**Test.** NQ, 2018 and 2022–Aug 2026. Rules fixed in advance, trained on 2018–2024 and checked once on 2025–26.

**How often the walls get hunted:**

| | High swept | Low swept | Both |
|---|---|---|---|
| London vs Asia walls | 58% | 49% | 14% |
| NY AM vs London walls | 68% | 67% | 35% |
| Asia vs prior RTH walls | 23% | 18% | 0% |

A shift confirms in 65% of London sessions and 41% of NY AM windows.

**Does the shift call direction to the end of the next session?** Hit % (n), train 2018–24 → test 2025–26:

| | Reversal (sweep → shift away) | Continuation (sweep → shift through) | Both walls swept first | No sweep |
|---|---|---|---|---|
| London | 51.4% (146) → 48.3% (60) | 45.4% (348) → 47.7% (153) | 63.2% (68) → 58.3% (12) | 50.8% (61) → 56.8% (37) |
| NY AM | 44.7% (47) → 50.0% (18) | 54.0% (211) → 57.1% (84) | 53.6% (138) → 55.8% (52) | — |

**No class calls direction reliably in both periods.** The best-looking one, London after both Asia walls have been swept, has only 12 test sessions.

**Does a reversal reach the other wall?** Measured by the end of the next session, against the baseline rate after any first sweep:

| | Reversal → opposite wall | Baseline after any first sweep | Lift |
|---|---|---|---|
| London (by 11:30) | 72.6% train / 61.7% test | 61.6% / 57.0% | +11 → +5 pts |
| NY AM (by 16:14) | 51.1% train / 55.6% test (n 18) | 51.2% / 47.2% | 0 → +8 pts |

### Re-test on the standard session definitions (Oct 2026)

These are the sessions used across the model library (Session Multi-Tier v4): Asia 20:00–00:00, London 02:00–05:00, NY AM 09:30–11:00, NY Lunch 11:30–13:00 and NY PM 13:30–16:00 ET. The chain is: London hunts Asia, NY AM hunts London, NY PM hunts Lunch. A shift may confirm on the final 30-minute block, which is checked at the session close. Each outcome is measured to the end of the next hunt session (London → 11:00, NY AM → 16:00, NY PM → 16:59). Script: `Kekkai/sos2.py`.

| Hunt session | High swept | Low swept | Both | Shift confirms |
|---|---|---|---|---|
| London vs Asia | 58% | 49% | 14% | 75% |
| NY AM vs London | 65% | 64% | 31% | 41% (always at 11:00) |
| NY PM vs Lunch | 61% | 52% | 18% | 69% |

- **NY AM:** with a 90-minute window and 30-minute blocks, a shift can only confirm at the 11:00 close.
- **Direction:** no class calls direction in both periods. Train → test hit rates sit between 40% and 59%. NY AM reversal reads 66.7% on test, but only 18 sessions, against 43.8% on train.

| Reversal → opposite wall | Reversal (train / test) | Baseline after any first sweep | Lift |
|---|---|---|---|
| London → other Asia wall by 11:00 | 74.4% / 65.3% (n 176 / 72) | 59.6% / 53.8% | +15 / +12 pts |
| NY AM → other London wall by 16:00 | 52.1% / 55.6% (n 48 / 18) | 51.2% / 47.7% | +1 / +8 pts |
| NY PM → other Lunch wall by 16:59 | 25.0% / 25.8% (n 152 / 66) | 22.7% / 21.7% | +2 / +4 pts |

**How to use it.**
- **Walls and sweeps are a map, not a signal.** They tell you whose liquidity is being taken. NY AM takes at least one London wall about 70% of the time.
- **A London reversal is the one target cue.** On these definitions it lifts the chance of reaching the other Asia wall by 11:00 by about 12 points out of sample (65% vs 54%). It is still not an entry, and about a third of the time the other wall isn't reached.
- **The NY PM–Lunch chain adds nothing measurable.**
- **Ignore Asia shifts.**
- **Session compression (range under 75% of its own 20-session average) is shown as context only.** It was not tested as a filter here.
- **Session ranges are the reliably predictable part** (see HYDRA).
- **Indicator (Oct 2026):** draws Asia and London walls, sweeps and shifts. The higher-timeframe walls are PDH/PDL, each completed day's high and low this week, today's high and low so far, and the week-to-date and month-to-date high and low; previous week and month levels are optional. It uses no RTH levels and has no on-screen table.

**Probability that a session-on-session Kekkai trade trigger makes +0.1R or more after costs on new data: about 10%. As a confluence map it is honest as it stands.**

---
*95% Wilson CIs on all tested figures. PD array references are generic — apply your own confirmed structure ID.*
