# NQ 30-Minute Dealing Range Analysis (v5)
**Dataset:** NQ continuous 1-min, Jan 2023 – Aug 2026, **829 days**, all five sessions present
**Sessions:** Asia 20:00–00:00 · London 02:00–05:00 · NY AM 09:30–11:00 · NY Lunch 11:30–13:00 · NY PM 13:30–16:00 (ET)

---

## HEADLINE — Two findings here are stronger than anything in v1–v4

1. **London opening-block breakout holds 79.5% of the time** — the single strongest directional setup found in this entire project, beating the lunch-range breakout (61.3%) by a wide margin.
2. **Opening-block volatility predicts total session range with r=0.825** — the tightest correlation found anywhere in this work. The first 30 minutes tells you how big the session will be.

Both are detailed below.

---

# PART 1 — THE VOLATILITY MAP

Average 30-minute block range across all 829 days:

### Asia (20:00–00:00) — monotonic decay
| Block | Avg range | Median |
|---|---|---|
| **20:00–20:30** | **38.7** | 25.2 |
| 20:30–21:00 | 31.7 | 21.5 |
| 21:00–21:30 | 30.4 | 20.5 |
| 21:30–22:00 | 29.5 | 20.5 |
| 22:00–22:30 | 26.5 | 17.8 |
| 22:30–23:00 | 23.4 | 15.8 |
| 23:00–23:30 | 22.3 | 15.2 |
| 23:30–00:00 | 21.2 | 14.2 |

Every block is quieter than the one before it — a 45% decline from open to close. Asia front-loads entirely.

### London (02:00–05:00) — bimodal, peaks late
| Block | Avg range | Median |
|---|---|---|
| 02:00–02:30 | 32.0 | 25.8 |
| 02:30–03:00 | 29.0 | 22.0 |
| **03:00–03:30** | **43.2** | 35.0 |
| 03:30–04:00 | 36.7 | 30.5 |
| **04:00–04:30** | **44.3** | 35.5 |
| 04:30–05:00 | 34.5 | 27.5 |

**London breaks the pattern of every other session.** It does *not* peak at its open — it peaks at 03:00–03:30 and again at 04:00–04:30, both ~40% hotter than the open. If you assumed London volatility concentrates at the open the way NY's does, that's wrong.

### NY AM (09:30–11:00) — monotonic decay, highest absolute volatility of the day
| Block | Avg range | Median |
|---|---|---|
| **09:30–10:00** | **124.6** | 104.0 |
| 10:00–10:30 | 104.9 | 87.0 |
| 10:30–11:00 | 88.3 | 74.0 |

The 09:30–10:00 block is the most volatile 30 minutes in the entire 24-hour cycle. Note this is exactly the corrected Opening Range window.

### NY Lunch (11:30–13:00) — mild decay
| Block | Avg range | Median |
|---|---|---|
| 11:30–12:00 | 69.5 | 57.5 |
| 12:00–12:30 | 64.2 | 52.0 |
| 12:30–13:00 | 61.0 | 48.5 |

### NY PM (13:30–16:00) — flat, then closing spike
| Block | Avg range | Median |
|---|---|---|
| 13:30–14:00 | 58.9 | 47.0 |
| 14:00–14:30 | 60.6 | 47.2 |
| 14:30–15:00 | 58.4 | 45.8 |
| 15:00–15:30 | 59.2 | 45.5 |
| **15:30–16:00** | **71.9** | 57.2 |

13:30–15:00 is the deadest stretch of the RTH day — four blocks within a 3-point band. Then the closing auction lifts the final block 23%.

### Cross-session scale check
The **quietest** NY AM block (88.3) is still **2x London's hottest** (44.3) and **2.3x Asia's hottest** (38.7). Position sizing calibrated to one session will be badly wrong in another.

---

# PART 2 — OPENING-BLOCK BREAKOUT QUALITY (Tier 1 Edge)

Does a one-sided break of a session's **first 30-minute block** hold through that session's close?

| Session | Hold rate | 95% CI | n |
|---|---|---|---|
| **London (02:00–02:30 block)** | **79.5%** | 75.3–83.2% | 405 |
| NY PM (13:30–14:00 block) | 69.6% | 65.4–73.6% | 481 |
| Asia (20:00–20:30 block) | 68.8% | 64.7–72.7% | 520 |
| NY AM (09:30–10:00 block) | 60.8% | 57.1–64.4% | 681 |
| NY Lunch (11:30–12:00 block) | 59.3% | 55.4–63.1% | 627 |

**London is the standout and it isn't close.** A clean one-sided break of London's opening 30 minutes holds to the London close nearly 80% of the time — the best directional probability found anywhere in v1–v5.

**The counterintuitive part:** NY AM has the *highest volatility* but among the *worst breakout reliability* (60.8%). Volatility and directional persistence are not the same thing. NY AM's opening block is violent but choppy — breaks get faded. London's opening block is quieter but far more decisive.

**Sample-size note:** London's n=405 is smaller than NY AM's n=681 because London produces clean one-sided breaks less often (more days break both ways and get excluded). That's part of why the ones that do occur carry more information.

---

# PART 3 — OPENING-BLOCK VOLATILITY PREDICTS SESSION RANGE (Tier 1 Edge)

Split each session's days into terciles by the size of its opening 30-min block, then compare resulting full-session range:

| Session | Low-vol-open tercile | High-vol-open tercile | Ratio | Correlation |
|---|---|---|---|---|
| **NY AM** | 115 pts | 289 pts | **2.50x** | **r=0.825** |
| London | 58 pts | 140 pts | 2.41x | r=0.712 |
| NY PM | 93 pts | 201 pts | 2.15x | r=0.649 |

**r=0.825 for NY AM is the tightest correlation in this entire body of work** — tighter than the morning-range/day-range correlation from v3 (r=0.783). The first 30 minutes of NY AM tells you, with real precision, how large the whole session will be.

**Practical use:** this is a *sizing and target* tool, not a directional one. A wide 09:30–10:00 block means expect a ~289-point NY AM session; a narrow one means expect ~115. That's a 2.5x difference in what's realistically available, known by 10:00 AM.

---

# PART 4 — PEAK-VOLATILITY BLOCK RETRACEMENT

After a session's hottest 30-min block completes, does price return to that block's 50% midpoint before session end?

| Session | Retracement rate | 95% CI | n |
|---|---|---|---|
| Asia | 69.6% | 66.3–72.7% | 792 |
| **NY PM** | **69.3%** | 65.3–73.0% | 550 |
| London | 62.8% | 59.3–66.2% | 756 |
| NY AM | 52.7% | 49.0–56.3% | 729 |

**Consistent with the v3 finding** that consequent-encroachment/midpoint retracement is a real structural behavior (overnight range midpoint retraced 75.8% of the time). Asia and NY PM show it strongest here.

**NY AM is the exception at 52.7% — essentially a coin flip.** When NY AM makes a violent move, it tends *not* to come back to the midpoint within the session. This reinforces the Part 2 finding: NY AM is directionally messy but, once it moves hard, it doesn't retrace as readily as other sessions do.

---

# PART 5 — DOES THE HOTTEST BLOCK CONTAIN THE SESSION EXTREME?

Initial results showed a striking asymmetry — the hottest block contained the session **low** far more often than the **high**, across every session:

| Session | Hottest block has HIGH | Hottest block has LOW |
|---|---|---|
| Asia | 22.3% | 37.2% |
| London | 23.9% | 29.8% |
| NY AM | 39.4% | 52.4% |
| NY Lunch | 39.4% | 51.6% |
| NY PM | 30.4% | 42.1% |

**This turned out to be regime-driven, not structural.** Splitting by whether the day closed up or down:

| Condition | Hottest block has HIGH | Hottest block has LOW |
|---|---|---|
| NY AM, **up days** (n=456) | 31.4% | **64.0%** |
| NY AM, **down days** (n=371) | **49.3%** | 38.0% |

The apparent "low bias" was just the uptrend in 2023–2026. What the hottest block actually contains is **whichever extreme initiates the session's directional move** — the low on up days, the high on down days. That's a sensible mechanical result, but it means you cannot use it predictively without already knowing the day's direction, which defeats the purpose.

**Worth flagging honestly:** this is close to circular. The block where the turning point occurs is, unsurprisingly, the block with the biggest range. Treat Part 5 as descriptive structure, not a tradeable signal.

---

# WHAT TO ACTUALLY USE FROM V5

**Trade these:**
1. **London opening-block breakout — 79.5%.** Best directional edge in the project. Mark London's 02:00–02:30 range; a clean one-sided break holds to the 05:00 close four times in five.
2. **NY PM and Asia opening-block breakouts — ~69%.** Second tier but solid.
3. **NY AM opening-block size as a range forecast — r=0.825.** By 10:00 AM you have a high-confidence read on the session's total available range. Use it for targets and sizing.
4. **Peak-block midpoint retracement in Asia/NY PM — ~69%.** Reliable magnet levels in those two sessions.

**Do NOT use these:**
1. **NY AM opening-block breakout for direction (60.8%)** — weakest of the five sessions despite being the most volatile. Volatility ≠ directional reliability.
2. **NY AM peak-block midpoint retracement (52.7%)** — coin flip, no edge.
3. **Hottest-block-contains-extreme (Part 5)** — regime-dependent and near-circular.

**The broader pattern now visible across v3–v5:** NQ's exploitable structure is concentrated in **range forecasting, level retracement, and breakout persistence** — and notably, **London is far more directionally reliable than New York** despite carrying half the volatility. That runs against the common assumption that the NY open is the highest-quality session to trade.

---
*All confidence intervals are 95% Wilson score intervals. Terciles computed within-session. Correlations are Pearson.*
