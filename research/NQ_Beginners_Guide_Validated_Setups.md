# NQ Time & Price — A Beginner's Guide to Validated Setups

**What this is:** a consolidated summary of statistical testing on **833 trading days of NQ futures 1-minute data (January 2023 – August 2026)**, covering four independent calendar years and roughly 1.4 million individual price bars.

**What this is not:** a system that prints money. Every number below is a *probability*, not a promise. Read the "Before You Trade Any Of This" section before anything else.

---

# PART 0 — BEFORE YOU TRADE ANY OF THIS

If you read nothing else, read this section.

### A hit rate is not an edge
A setup that wins 79% of the time still loses money if the 21% of losses are four times larger than the wins. **Probability tells you how often you're right. Risk management determines whether you make money.** These two things are independent, and this document only addresses the first one.

### These numbers include no costs
Every statistic here is computed on raw price data. Real trading subtracts spread, commission, and slippage from every single trade. A setup with a genuine 3-point average edge is a *losing* strategy once you pay 2 points in costs per round trip.

### Regimes change
This data covers 2023–2026 — a period that was, on balance, an uptrending market. Several findings in this analysis turned out to be artifacts of that uptrend rather than structural truths (documented below). If the market enters a sustained downtrend, some of these numbers will move, and a few may invert.

### Confidence intervals matter more than point estimates
When you see "79.5% (CI 75.3–83.2%)", the honest reading is *"somewhere between roughly 75% and 83%"* — not 79.5% exactly. Where samples are smaller, those ranges get wider. Always look at the range, not the headline number.

### Sizing rule for a beginner
Until you have logged at least 50–100 of your own trades on a single setup and confirmed it behaves for *you* the way this data says it should, risk an amount per trade that you would be genuinely indifferent to losing. NQ moves fast — one full-size contract moves $20 per point, and the average NY AM session covers 188 points.

---

# PART 1 — THE FIVE TRADING SESSIONS

All times Eastern. Know these cold before anything else.

| Session | Hours | Avg range | Character |
|---|---|---|---|
| Asia | 20:00–00:00 | 83 pts | Quiet, decays steadily all session |
| London | 02:00–05:00 | 92 pts | Moderate, but **most directionally reliable** |
| **NY AM** | **09:30–11:00** | **188 pts** | Most volatile period of the entire 24h cycle |
| NY Lunch | 11:30–13:00 | 112 pts | Chop-prone, low conviction |
| NY PM | 13:30–16:00 | 138 pts | Flat until 15:30, then closing spike |

**Critical scale point for a beginner:** the *quietest* 30 minutes of NY AM is still twice as volatile as the *busiest* 30 minutes of London. If you size a position the same way across sessions, you are taking wildly different risk without realising it.

---

# PART 2 — THE SETUPS THAT ACTUALLY VALIDATED

These are ordered by strength of evidence. Each shows the probability, the confidence interval, and the sample size.

## Tier 1 — Strongest

### 1. London Opening-Block Breakout — 79.5%
**(CI 75.3–83.2%, n=405)**

Mark the high and low of London's first 30 minutes (**02:00–02:30**). If price later breaks *one side only* — and does not break the other — it closes beyond that level at the 05:00 London close about four times in five.

*Why it's the best setup found:* it's the highest directional probability anywhere in this entire study, across 405 clean occurrences.

*The catch:* it requires a **clean one-sided break**. Days that break both directions are excluded and are not tradeable under this rule. Roughly half of London sessions don't produce a qualifying setup — patience is part of the edge.

### 2. NY AM Opening-Block Range Forecast — r=0.825
**(correlation, n=829)**

The size of the **09:30–10:00** range predicts the size of the entire NY AM session with the tightest correlation found anywhere in this work.

- Narrow opening block → expect a session around **115 points**
- Wide opening block → expect a session around **289 points**

That's a **2.5x difference in available range**, known by 10:00 AM.

*This is a targeting and sizing tool, not a direction tool.* It tells you how much room there is, not which way to go. Use it to set realistic profit targets instead of guessing.

### 3. Overnight Range 50% Retracement — 75.8%
**(CI 72.7–78.5%, n=833)**

Take the full overnight range (prior day 18:00 close through 09:30 open) and mark its midpoint. Price returns to that midpoint at some point during the RTH session about three days in four.

*One of the most dependable magnet levels found.* Simple to mark, high hit rate, works regardless of direction.

## Tier 2 — Solid

### 4. Opening Range Breakout, RTH — 82% / 70%
**(n=272 up / n=227 down)**

Using the **9:30–10:00** Opening Range: a clean one-sided break above holds to the close 82% of the time; a clean break below holds 70% of the time.

*Note the asymmetry* — upside breaks were meaningfully more reliable than downside breaks in this dataset, likely reflecting the period's uptrend. Do not assume this holds in a bear market.

### 5. NY PM and Asia Opening-Block Breakouts — ~69%
**(NY PM: 69.6%, n=481 · Asia: 68.8%, n=520)**

Same rule as the London setup, applied to those sessions' first 30 minutes (13:30–14:00 and 20:00–20:30). Solid, second-tier reliability.

### 6. Lunch-Range Breakout into PM — 61.3%
**(CI 57.5–64.9%, n=648)**

Mark the 11:30–13:00 lunch range. A one-sided break during the PM session closes beyond that level 61.3% of the time.

### 7. Peak-Block Midpoint Retracement (Asia / NY PM) — ~69%
**(Asia: 69.6%, n=792 · NY PM: 69.3%, n=550)**

After a session's most volatile 30-minute block completes, price returns to that block's midpoint before session end about 69% of the time — in Asia and NY PM specifically.

**Important exception: this does not work in NY AM (52.7% — coin flip).** When NY AM moves hard, it tends not to come back.

### 8. Weekly Level Revisits — 63.7% / 38.0%
**(n=179 weeks)**

Each week, mark the *prior* week's high and low. The prior week's high gets revisited 63.7% of the time; the prior week's low only 38.0%.

*Regime warning:* this asymmetry is almost certainly a product of the 2023–2026 uptrend. Expect it to flatten or invert in a downtrend.

### 9. Gap Fills — NDOG and NWOG
- **NDOG** (daily 17:00 close → 18:01 reopen gap): fills 92.2% within 1 day, 95.3% within 2–3 days
- **NWOG** (Friday close → Sunday reopen gap): fills 95.7% within 1 day, **100% within 3 days** (n=23)

*The NWOG 100% figure is on a small sample (23 weekly gaps).* The realistic true rate is likely somewhere in the 86–100% band. Still, both are high-probability magnet levels.

### 10. Monthly Seasonality — July and November
Based on **16 years** of NQ monthly returns (2010–2025):
- **July**: positive in **15 of 16 years (94%)**, p=0.011
- **November**: positive in 75% of years, p=0.037

These are the only two months that clear statistical significance across the full history. Treat as a mild seasonal tailwind, never as a standalone reason to trade.

---

# PART 3 — THINGS THAT SOUND GOOD BUT DON'T WORK

**This section may be more valuable than Part 2.** Beginners lose money trading plausible-sounding patterns that have no statistical support. Every item below was tested and failed.

### ❌ "Sweep the highs then reverse" — 31.6% (Asia) / 26.0% (London)
This is a widely-taught setup, and the data flatly contradicts it. When NY AM takes out one side of the overnight range, price **continues** in that direction 2–3 times more often than it reverses.

If you are fading these sweeps by default, 829 days of data say you are systematically on the wrong side.

### ❌ Session-to-session direction carryover — all coin flips
| Test | Result |
|---|---|
| London direction → NY AM | 48.2% |
| Asia direction → NY AM | 52.0% |
| NY AM direction → NY PM | 49.3% |
| Asia **and** London agree → NY AM | 50.1% |
| Asia **and** London agree → full day | 47.8% |

**Every single one is a coin flip.** Even the "confluence" version — requiring two sessions to agree — bought exactly zero predictive power while cutting the sample in half.

*The lesson:* "this session went up, so the next one will too" has no basis in this data.

### ❌ Magic minutes — no tradeable minute-of-day edge
Testing all 1,380 minutes of the trading day: 110 looked "significant" at the usual p<0.05 threshold. But when you run 1,380 simultaneous tests, **roughly 69 will look significant by pure chance alone**.

After proper statistical correction, only **2 minutes survive** — and both show average moves of about **1 point**, which is smaller than the spread plus commission. Not tradeable.

*The lesson for a beginner:* if you test enough patterns, some will always look impressive. That is not the same as finding an edge.

### ❌ NY AM opening-block breakout for direction — 60.8%
The most volatile session has among the **worst** breakout reliability (60.8%, vs London's 79.5%).

**Volatility and directional reliability are not the same thing.** NY AM is loud but choppy — breaks get faded frequently. Many beginners gravitate to the NY open precisely because it's exciting, and that's the wrong instinct.

### ❌ Power hour trend continuation — ~47%
The 15:00–16:00 "power hour" does not reliably continue the day's trend. Coin flip.

### ❌ Contract-month segmentation — no improvement
Splitting data by contract (H/M/U/Z) did not meaningfully improve any statistic, while roughly doubling confidence intervals by cutting sample size. Not worth the precision cost.

---

# PART 4 — A SIMPLE DAILY ROUTINE

### The night before / early morning
1. Mark the **overnight range** (18:00 prior day → 09:30) and its **midpoint** — 75.8% retracement level
2. Note any unfilled **NDOG** (17:00→18:01 gap) — 92% fills within a day
3. On Mondays, mark the **NWOG** (Friday close → Sunday open) — near-certain fill within 3 days

### If you trade London (02:00–05:00)
4. Mark the **02:00–02:30 range**
5. Wait for a **clean one-sided break** — do not act if both sides break
6. That break holds to the 05:00 close **79.5%** of the time — your highest-probability setup

### At the NY open (09:30–10:00)
7. Let the full 30 minutes complete. Do not trade the first bar.
8. Measure the block's range → this forecasts the whole session's size (**r=0.825**). Narrow ≈ 115 pt session, wide ≈ 289 pt session. Set targets accordingly.
9. Mark the OR high/low. A clean one-sided break holds **82% (up) / 70% (down)**.
10. **Do not fade overnight-range sweeps.** Continuation is 2–3x more likely.

### Midday (11:30–13:00)
11. Mark the lunch range. A one-sided PM break holds **61.3%**.
12. Expect chop. This is a low-conviction window.

### Weekly
13. Mark **prior week's high and low**. High revisited 63.7%, low 38.0%.

---

# PART 5 — HOW TO THINK ABOUT THIS PROPERLY

### The shape of the edge
Across everything tested, a clear pattern emerged:

> **NQ's exploitable structure lives in levels, ranges, and retracements — not in predicting which way a session will close.**

Nearly every *directional carryover* test failed. Nearly every *level and retracement* test succeeded. Build your thinking around "where is price likely to go and how far", not "will it go up or down".

### Two honest examples of being wrong
Both of these happened during this analysis and are worth internalising:

1. **A "10:16 AM reversal minute" looked real** at small sample size (64% of reversals clustered there). With the full dataset it dissolved into a broad, unremarkable 10:00–10:24 lean. **Small samples create convincing illusions.**

2. **A "May/June are the strong months" finding** from 4 years of data did not survive when 16 years became available — **July and November** turned out to be the genuinely significant months instead.

If your backtest is based on a handful of instances, assume it is probably noise until proven otherwise.

### What to do next
1. **Paper trade one setup** — start with London opening-block breakout or the overnight midpoint retracement. One setup, not ten.
2. **Log every trade** — entry, exit, whether the setup qualified under the strict rules, and outcome.
3. **After 50 trades**, compare your actual hit rate to the number in this document. If it's dramatically lower, the problem is usually execution or setup qualification, not the statistic.
4. **Only then** consider adding a second setup.

---

## Quick Reference Card

| Setup | Probability | When |
|---|---|---|
| London opening-block breakout | **79.5%** | 02:00–02:30 range, hold to 05:00 |
| RTH OR breakout (upside) | 82% | 09:30–10:00 range |
| Overnight range 50% retrace | 75.8% | Any time during RTH |
| RTH OR breakout (downside) | 70% | 09:30–10:00 range |
| NY PM opening-block breakout | 69.6% | 13:30–14:00 range |
| Asia opening-block breakout | 68.8% | 20:00–20:30 range |
| Peak-block midpoint retrace (Asia/PM) | ~69% | After hottest 30-min block |
| Prior week's high revisited | 63.7% | During following week |
| Lunch-range breakout | 61.3% | 11:30–13:00 range, break in PM |
| NY AM session range forecast | r=0.825 | From 09:30–10:00 block size |

**Avoid:** fading overnight sweeps · session direction carryover · minute-of-day patterns · NY AM breakouts for direction · power hour continuation

---
*All probabilities are 95% Wilson score confidence intervals computed on 833 NQ trading days, Jan 2023 – Aug 2026, except monthly seasonality (16 years, 2010–2025) and weekly levels (179 weeks). Statistics are descriptive of historical behaviour and are not predictions. This document is educational and is not financial advice.*
