# NQ Session-Based Multi-Tier Analysis (v4)
**Dataset:** NQ continuous 1-min, Jan 2023 – Aug 2026, **829 days with all five sessions present**
**Session definitions used:** Asia 20:00–00:00 · London 02:00–05:00 · NY AM 09:30–11:00 · NY Lunch 11:30–13:00 · NY PM 13:30–16:00 (all ET)

---

## READ THIS FIRST — Headline Result

Most of the session-based directional setups tested here **came back as coin flips**. That is the single most important finding in this document, and it's reported first deliberately so it doesn't get lost underneath the handful of things that did work.

This is a useful result, not a failed one. Knowing that London's direction tells you nothing about NY AM saves you from trading a setup that feels intuitive but has no statistical support.

---

# TIER 1 — REAL, TRADEABLE EDGES
*Findings that clear a coin flip by a meaningful margin with tight confidence intervals*

| Setup | Probability | 95% CI | n |
|---|---|---|---|
| **Lunch-range one-sided break holds into PM close** | **61.3%** | 57.5–64.9% | 648 |
| NY AM contains the RTH day's LOW | 54.5% | 51.1–57.9% | 829 |
| NY AM contains the RTH day's HIGH | 44.4% | 41.0–47.8% | 829 |

**The lunch-range breakout is the only genuinely strong directional setup found in this entire session analysis.** When price breaks one side (and only one side) of the 11:30–13:00 lunch range during the PM session, it closes beyond that level 61.3% of the time. The confidence interval sits comfortably above 50%, and n=648 is a solid sample.

**The AM high/low asymmetry is real but modest.** The NY AM session is meaningfully more likely to contain the day's low (54.5%) than its high (44.4%) — a ~10-point spread. Consistent with the generally uptrending character of 2023–2026; would need re-testing in a sustained downtrend to know whether it's structural or regime-specific.

---

# TIER 2 — MECHANICALLY TRUE BUT NOT AN EDGE
*Findings that look dramatic but are largely arithmetic artifacts*

| Finding | Probability |
|---|---|
| NY AM takes out **either** side of the Asia range | 99.4% |
| NY AM takes out **either** side of the London range | 98.7% |
| NY AM takes out Asia HIGH | 68.0% |
| NY AM takes out Asia LOW | 63.9% |
| NY AM takes out London HIGH | 66.1% |
| NY AM takes out London LOW | 64.5% |

**Why the 99% number is not the edge it appears to be:** NY AM's average range is **188 points**. Asia's is **83**, London's is **92**. A range more than twice the size will almost always engulf at least one side of a smaller range that precedes it — that's geometry, not order flow. Treat the "NY AM sweeps Asia/London liquidity" observation as descriptive context, not as a predictive signal you can position around.

The one-sided numbers (63–68%) are more interesting, but note they're roughly symmetric — NY AM is about equally likely to take the high or the low, which means knowing that a sweep will happen tells you nothing useful about *which direction*.

---

# TIER 3 — THE "SWEEP THEN REVERSE" NARRATIVE: NOT SUPPORTED

| Setup | Probability | 95% CI | n |
|---|---|---|---|
| Asia range swept one side → NY AM closes opposite direction | **31.6%** | 27.9–35.6% | 554 |
| London range swept one side → NY AM closes opposite direction | **26.0%** | 22.6–29.9% | 553 |

**This is a direct contradiction of a widely-taught setup.** The "sweep the highs then reverse" pattern (often called a Judas swing or stop hunt) occurs **less often than a coin flip would predict** — substantially less. Both confidence intervals sit well below 50%.

**What this actually means:** when NY AM takes out one side of the overnight range, price is roughly **2 to 3 times more likely to continue in that direction than to reverse**. If you're fading these sweeps as a default, the data across 829 days says you're on the wrong side of the distribution. The sweep is more often a genuine breakout than a trap.

---

# TIER 4 — NULL RESULTS (No Edge Found)
*Every one of these is statistically indistinguishable from a coin flip*

| Setup | Probability | 95% CI | Verdict |
|---|---|---|---|
| London direction → NY AM same direction | 48.2% | 44.8–51.7% | No edge |
| Asia direction → NY AM same direction | 52.0% | 48.6–55.4% | No edge |
| NY AM direction → NY PM same direction | 49.3% | 45.9–52.7% | No edge |
| Asia + London **agree** → NY AM follows | 50.1% | 45.2–55.0% | No edge |
| Asia + London **agree** → full RTH day follows | 47.8% | 42.9–52.8% | No edge |

**The conditional filter didn't help.** The intuition that "when Asia and London agree, that's a stronger signal" is reasonable — but it tested at 50.1%, an almost perfect coin flip. Adding the confluence requirement cut the sample from 823 to 393 days and bought exactly nothing in predictive power.

**Practical implication:** session-to-session directional carryover does not exist in this data. Whatever edge exists in NQ intraday behavior is in **levels, ranges, and retracement probabilities** (see the v3 document — overnight range 50% retracement at 75.8%, NWOG fills at 95%+), **not** in "this session went up so the next one will too."

---

# TIER 5 — MINUTE-LEVEL DIRECTIONAL BIAS: NO TRADEABLE SIGNAL

You asked for every-minute analysis. Here it is, with the multiple-comparisons problem handled properly.

| Metric | Result |
|---|---|
| Minutes tested (with n≥200 observations) | 1,380 |
| Minutes "significant" at raw p<0.05 | 110 |
| **Minutes expected significant by pure chance** | **~69** |
| Minutes surviving Bonferroni correction (p<0.000036) | **2** |

**The two survivors:**

| Minute | Mean move | % up | p-value |
|---|---|---|---|
| 09:24 ET | **−0.81 pts** | 40.5% | 3.9×10⁻⁶ |
| 09:27 ET | **−1.26 pts** | 45.2% | 4.3×10⁻⁶ |

**Both are economically meaningless.** A statistically real −1 point average drift is smaller than the bid-ask spread plus commission on a single NQ contract. You cannot trade it profitably. They're likely a real microstructure artifact of pre-open positioning in the final minutes before 9:30, but they are not a setup.

**The core lesson from this tier:** 110 minutes crossed the naive p<0.05 threshold, but chance alone predicts ~69. Without correction, you would have concluded there were dozens of "magic minutes" and built a framework on statistical noise. **After correction, there is no exploitable minute-of-day directional edge in NQ.**

---

# TIER 6 — CONTRACT-MONTH SEGMENTATION: DOESN'T RELIABLY HELP

You proposed truncating by contract month (H/M/U/Z) to tighten correlation. Tested directly:

| Contract | Days | NY AM avg range | NY AM % up | Sweep-reverse % | Range CV |
|---|---|---|---|---|---|
| H (Mar) | 174 | 190 | 51.1% | 33.9% | 0.486 *(tighter)* |
| M (Jun) | 246 | 184 | 55.3% | 30.7% | 0.746 *(worse)* |
| U (Sep) | 224 | 206 | 50.0% | 32.2% | 0.609 *(tighter)* |
| Z (Dec) | 185 | 172 | 49.2% | 29.9% | 0.485 *(tighter)* |
| **Pooled** | 829 | 188 | 51.6% | 31.6% | **0.613** |

**Verdict: segmentation is not worth the cost.** Three of four contracts showed slightly tighter dispersion (lower coefficient of variation), but M was substantially *worse*, and none of the directional statistics moved meaningfully — the sweep-reverse rate stayed in a narrow 29.9–33.9% band across all four, and % up days stayed near 50% everywhere.

Meanwhile, segmenting cuts your sample from 829 days to ~200 per bucket, roughly **doubling your confidence intervals**. You would be paying a real, quantifiable precision penalty for a correlation improvement that the data does not show exists.

---

# SESSION PROFILE REFERENCE

| Session | Avg range | Median range | Avg net move | % closes up |
|---|---|---|---|---|
| Asia (20:00–00:00) | 83 pts | 57 | +0.9 | 53.3% |
| London (02:00–05:00) | 92 pts | 74 | +3.8 | 54.2% |
| **NY AM (09:30–11:00)** | **188 pts** | **162** | −1.5 | 51.6% |
| NY Lunch (11:30–13:00) | 112 pts | 91 | +2.4 | 53.9% |
| NY PM (13:30–16:00) | 138 pts | 109 | +0.5 | 54.2% |

**NY AM is the volatility engine** — more than double Asia's range and roughly 35% larger than NY PM. Note also that every session's average net move is within ±4 points of zero, which is another way of stating the Tier 4 result: no session has a meaningful inherent directional bias.

---

# WHAT TO ACTUALLY DO WITH THIS

**Trade these:**
1. **Lunch-range breakout into PM** — 61.3%, the strongest session-based directional setup found
2. **Level-based setups from v3** — overnight range 50% retracement (75.8%), NWOG fill (95%+ within 3 days), OR breakout hold (82% high / 70% low)

**Stop doing these if you are:**
1. **Fading overnight-range sweeps by default** — the data says continuation is 2–3x more likely than reversal
2. **Using London or Asia direction to bias NY AM** — pure coin flip, no information content
3. **Looking for magic minutes** — after correcting for multiple comparisons, they don't exist

**The overall shape of the edge in NQ, based on everything tested across v1–v4:** it lives in **where price is likely to go (levels, ranges, retracements)**, not in **which direction a session will close**. Every directional-carryover test failed; nearly every level-and-retracement test succeeded. Weight your framework accordingly.

---
*All confidence intervals are 95% Wilson score intervals. Minute-level testing uses Bonferroni correction for 1,380 simultaneous comparisons. Session windows per user specification.*
