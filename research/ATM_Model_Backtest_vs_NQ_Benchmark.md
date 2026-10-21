# ATM Model — Time & Price Backtest Against the NQ Benchmark

**What was tested:** the core structural premise of the ATM approach — a defined Time-Based Range (TBR) forms during a set window, one side of that range gets swept during a following execution window, and price is expected to then run to the *opposite* side of the same range (ATM High ↔ ATM Low).

**Dataset:** NQ continuous, 2023–2026, full 24-hour coverage, **833–876 qualifying days per session** (varies slightly by window due to data coverage).

**Sessions tested, using the windows as specified:**
| Session | Time-Based Range | Execution Window |
|---|---|---|
| AS (Asia) | 18:00–20:00 ET | 20:01–22:00 ET |
| AM (New York) | 07:00–09:30 ET | 09:31–11:00 ET |
| LU (Lunch) | 11:30–13:30 ET | 13:31–15:00 ET |

---

## A note on scope, stated upfront

This tests the **structural premise** of the model — does the sweep-then-run pattern actually occur — using pure OHLC boundary logic. It does **not** test the model's precise entry mechanics (fair value gap / inverted fair value gap identification), stop placement, correlated-asset displacement confirmation, or the 1.5R exit rule, since those require gap-detection logic beyond a simple high/low boundary test. What follows is a direct test of the core claim the model is built on; the refinement rules are addressed qualitatively at the end.

---

## I caught and fixed a real error while building this — worth showing

My first pass returned a "full run to opposite side" rate of essentially **0%** across all three sessions. That result was wrong, and the reason is instructive: I had defined "one-sided sweep" in a way that *excluded* any day where the opposite side also broke — which meant the population I was testing for "does it reach the opposite side" had already been filtered to only contain days where it structurally couldn't. The fix was to track which boundary breaks first chronologically, then check whether the other boundary breaks *afterward*, across the full population of swept days rather than a pre-filtered subset. The corrected numbers below reflect that fix.

---

## RESULTS

### AM Session (New York) — the strongest of the three
| Metric | Result |
|---|---|
| TBR gets swept at all during execution | **97.1%** (839/864), CI 95.8–98.0% |
| Given a sweep, stays one-sided (no full run) | 64.5% |
| **Given a sweep, price runs to the OPPOSITE side (full ATM High↔Low)** | **35.5%** (298/839), CI 32.4–38.8% |
| Given a full run, window closes confirming beyond the 2nd side | 52.7% (157/298) |

### AS Session (Asia)
| Metric | Result |
|---|---|
| TBR gets swept at all during execution | 83.0% (727/876), CI 80.4–85.3% |
| Given a sweep, stays one-sided | 86.0% |
| **Given a sweep, full run to opposite side** | **14.0%** (102/727), CI 11.7–16.7% |
| Given a full run, close confirms beyond 2nd side | 46.1% (47/102) |

### LU Session (Lunch)
| Metric | Result |
|---|---|
| TBR gets swept at all during execution | 79.2% (660/833), CI 76.3–81.8% |
| Given a sweep, stays one-sided | 92.4% |
| **Given a sweep, full run to opposite side** | **7.6%** (50/660), CI 5.8–9.8% |
| Given a full run, close confirms beyond 2nd side | 42.0% (21/50) |

---

## What this actually means

**The core premise is real but session-dependent, and it's the exception rather than the rule everywhere it was tested.** A TBR getting swept at all is common (79–97%), but the full run to the *opposite* boundary — the actual setup the model is built around — happens in a minority of cases in every session:

- **AM: 35.5%** — roughly 1 in 3 sweeps completes the full run
- **AS: 14.0%** — roughly 1 in 7
- **LU: 7.6%** — roughly 1 in 13

**AM is by far the most viable session for this specific setup.** It also has the tightest confidence interval and largest sample. If you're going to trade this model on one session, the data says it should be the AM window, not Asia or Lunch — which is somewhat notable given AM's TBR (7:00–9:30) overlaps almost exactly with the premarket-and-open period already shown elsewhere in this project to carry the day's highest volatility. A wide, information-rich TBR is more likely to produce a genuine two-way run than a quieter one.

**LU is the weakest by a wide margin.** This lines up with earlier findings in this project — the 11:30–13:00 lunch hour was already shown to be a low-conviction, chop-prone window. A model expecting a decisive two-sided run through that window is fighting the session's own character.

**The "displacement closes beyond the second side" confirmation roughly halves an already-selective sample.** Even after a genuine full run occurs, the execution window only *closes* confirming that displacement 42–53% of the time — meaning a real fraction of "full run" days see price wick through the opposite boundary and then pull back before the window ends. This matters directly for the model's exit rule: a strategy holding for the full displacement-confirmation close would be relying on a coin-flip-or-worse event happening *after* the harder-to-achieve full run already occurred.

## Compounding the probabilities — a realistic end-to-end estimate

Multiplying through the AM session's own numbers gives a rough sense of how selective the complete setup is:

**Sweep occurs (97.1%) × full run to opposite side (35.5%) × close confirms displacement (52.7%) ≈ 18.2%**

That's the probability of the complete structural sequence happening in the AM session on any given day, using purely mechanical OHLC criteria. This is *before* the model's own IFVG/FVG entry filter, which is designed to select for higher-quality instances of this pattern rather than fire on every one — so 18.2% is a ceiling on frequency, not a hit rate for the actual trade signal (which requires the additional gap-formation criteria to even trigger an entry).

---

## What wasn't tested, and why

The refinement rules described in the source material — using correlated-asset displacement as confirmation, treating SMT (smart money technique) divergences as valid sweeps, and moving to breakeven when a correlated asset reaches the opposing liquidity level — are explicitly designed to *filter down* from this base rate to a smaller number of higher-quality setups. Testing those requires:

1. A synchronized second correlated instrument (e.g. ES, run in parallel with NQ) — buildable from the gold/silver-style pipeline already established in this project, but not yet done for an ES/NQ pair
2. Fair value gap / inverted fair value gap detection — a distinct pattern-recognition task on the 1-minute bars, not something the boundary-sweep test above captures

Both are buildable with the existing dataset if useful — the ES/NQ correlated-pair test in particular would directly test optimization rule #2 (both correlated assets must show displacement) and is a natural extension of the ES/NQ leadership-pair framework already sketched out earlier in this project.

---

## Bottom line

| Session | Full-run rate given a sweep | Verdict |
|---|---|---|
| **AM** | **35.5%** | Most viable of the three — still a minority outcome, but the strongest base rate |
| AS | 14.0% | Weak base rate — most sweeps stay one-sided |
| LU | 7.6% | Weakest — consistent with lunch being a chop-prone window in every other test in this project |

The model's core structural claim — that a swept time-based range tends to run to its opposite extreme — is **not the default outcome** in any of the three sessions on pure mechanical terms. It's a real, minority-probability event that the model's additional filters (FVG entries, correlated-asset confirmation, SMT sweeps) are presumably designed to select for. Whether those filters succeed in raising the hit rate meaningfully above these base rates is a separate, currently untested question.
