# Gold (GC) Time & Price Analysis — Full Parameter Suite vs NQ Benchmark

**Dataset:** GC continuous, **5-minute** bars, Jan 2023 – Aug 2026
**Usable RTH sessions:** 450 (434 with all five session windows)
**Benchmark:** NQ 2023–2026, 833 sessions, 1-minute bars
**Gold over the period:** $1,847 → $4,052 (**+119.4%**)

---

# ⚠️ PART 0 — DATA QUALITY (READ BEFORE ANY CONCLUSION)

Three limitations materially affect what can and cannot be concluded from this file.

### 1. Severe monthly coverage bias — calendar analysis is INVALID

| Month | Median RTH bars/day (81 = full) | Days |
|---|---|---|
| Jan | **81** | 86 |
| Feb | **9** | 75 |
| Mar | **81** | 86 |
| Apr | **11** | 79 |
| May | **81** | 89 |
| Jun | **8** | 79 |
| Jul | **81** | 90 |
| Aug | **8** | 78 |
| Sep | 76 | 64 |
| Oct | **5** | 62 |
| Nov | **81** | 63 |
| Dec | **9** | 62 |

**Odd months have full intraday coverage; even months are essentially empty.** This follows from how the continuous series was assembled — gold's contracts expire in even months (G/J/M/Q/V/Z), and the file only carries dense intraday data during each contract's most-liquid stretch.

**Consequence:** the sample is ~93% odd-month days. **Every calendar-based statistic — monthly, quarterly, day-of-month, month-half — is unusable.** I ran them, and I'm reporting that they're invalid rather than presenting numbers that look legitimate but aren't. Proper gold seasonality requires daily (not intraday) bars, which don't suffer this problem.

### 2. Five-minute resolution, not one-minute
Minute-level testing is impossible. The Opening Range is 6 bars rather than 30, and reversal timing is coarser. Findings are directionally comparable to NQ but less granular.

### 3. Contract rolls create real price gaps
**17 of 21 contract transitions show jumps over $5**, one as large as **+$52**. Roll days are excluded from all gap and overnight calculations. Any analysis ignoring this would produce phantom gaps.

### What remains valid
Within-day, non-calendar statistics: session profiles, OR breakouts and projections, sweep behaviour, carryover, intraday correlations, overnight encroachment (with coverage filter), and day-of-week. These make up the bulk of this document.

---

# PART 1 — THE HEADLINE STRUCTURAL DIFFERENCE

**Gold's trading sessions are far more evenly weighted than NQ's.**

| Session | GC avg range | GC % up | NQ avg range | NQ ratio to Asia |
|---|---|---|---|---|
| Asia (20:00–00:00) | **$19.75** | 48.4% | 83 pts | 1.00x |
| London (02:00–05:00) | $17.60 | 52.8% | 92 pts | 1.11x |
| **NY AM (09:30–11:00)** | **$22.42** | 51.2% | **188 pts** | **2.26x** |
| NY Lunch (11:30–13:00) | $12.99 | 50.9% | 112 pts | 1.35x |
| NY PM (13:30–16:00) | $14.36 | 53.2% | 138 pts | 1.66x |

**In NQ, the NY AM session is 2.26x the size of Asia. In gold it is only 1.13x.**

This is the single most important structural finding in the comparison. NQ is overwhelmingly a New York instrument — volatility concentrates in the US morning. Gold is a genuinely **24-hour global market**, with Asian and London hours carrying nearly the same weight as New York.

**Volume profile confirms it.** Gold's busiest 5-minute slots are **08:30 ET** (US economic data) and **10:00 ET**, not the 09:30 equity open. Gold responds to macro data releases, not the NYSE bell.

**Practical implication:** an NQ trader moving to gold cannot assume the US morning is where the opportunity is. Gold's Asian session is nearly as active as its NY session — and, as shown below, considerably more reliable directionally.

---

# PART 2 — OPENING RANGE (9:30–10:00 ET)

## 2.1 Breakout hold rate

| Metric | Gold | NQ benchmark |
|---|---|---|
| OR-**high** break holds to close | **74.3%** (110/148), CI 66.7–80.7% | 82.0% |
| OR-**low** break holds to close | **67.7%** (86/127), CI 59.2–75.2% | 70.0% |

**The setup works in gold, but weaker on the upside.** The downside figure is nearly identical to NQ (67.7% vs 70.0%); the upside is ~8 points lower.

Notably, gold's upside/downside asymmetry (74.3 vs 67.7 = 6.6 points) is much smaller than NQ's (82.0 vs 70.0 = 12 points), **despite gold being in a +119% bull market** — a stronger uptrend than NQ had over the same window.

That matters: in NQ, the OR asymmetry proved trend-driven (the 2022 bear test flipped it). In gold, a violent uptrend did *not* produce the same asymmetry, suggesting gold's breakout behaviour is less trend-sensitive than NQ's.

## 2.2 OR projection targets — nearly identical to NQ

| Multiple | GC upside | GC downside | NQ upside | NQ downside |
|---|---|---|---|---|
| **1.0x OR** | 27.6% | 28.7% | 28.7% | 28.6% |
| **1.5x OR** | 17.8% | 18.2% | 15.6% | 17.8% |
| **2.0x OR** | 11.8% | 12.0% | 9.0% | 11.8% |

**This is the most striking convergence in the entire comparison.** Two completely different instruments — an equity index and a precious metal, with different session structures and different drivers — produce **essentially the same OR projection decay curve.**

Both show the same halving pattern: ~28% at 1x, ~17% at 1.5x, ~11% at 2x. Gold runs marginally higher at extended multiples, reaching 2x-OR slightly more often.

**Interpretation:** the Opening Range as a *unit of measurement* appears to capture something general about how intraday ranges distribute, rather than something specific to equity index futures. That makes it far more likely to be a genuine structural property than a curve-fit artifact. This is real cross-instrument validation.

---

# PART 3 — SESSION OPENING-BLOCK BREAKOUTS

Does a one-sided break of a session's first 30 minutes hold to that session's close?

| Session | Gold | NQ | Difference |
|---|---|---|---|
| **Asia** | **78.5%** (175/223), CI 72.6–83.4% | 68.8% | **+9.7 — gold much better** |
| London | 69.3% (178/257), CI 63.4–74.6% | **79.5%** | −10.2 — gold much worse |
| NY PM | 67.3% (181/269), CI 61.5–72.6% | 69.6% | −2.3 — similar |
| NY Lunch | 59.6% (198/332), CI 54.3–64.8% | 59.3% | +0.3 — identical |
| NY AM | 57.0% (180/316), CI 51.5–62.3% | 60.8% | −3.8 — similar, both weak |

## The ranking inverts

**In NQ, London is the best session (79.5%) and Asia is mid-tier (68.8%). In gold, Asia is the best (78.5%) and London is mid-tier (69.3%).** The two instruments' top sessions are near mirror images.

**Why this is plausible rather than random:** gold has deep physical and investment demand in Asian hours — Shanghai and Indian physical markets, Japanese investment flows. An Asian-session breakout in gold reflects genuine regional participation. NQ's Asian session is mostly thin positioning ahead of the US open.

**Confirmed in both instruments:** **NY AM is the worst opening-block breakout session** — 57.0% in gold, 60.8% in NQ. Both are the most-watched session; both are the least directionally reliable. The "most exciting session is the least reliable" finding now holds across two asset classes.

**Practical takeaway for gold:** the highest-probability session breakout is the **20:00–20:30 ET Asian open**, at 78.5% with n=223.

---

# PART 4 — SWEEP BEHAVIOUR: THE FADE FAILS IN GOLD TOO

| Test | Gold | NQ |
|---|---|---|
| Asia range swept → NY AM **reverses** | **35.0%** (127/363), CI 30.3–40.0% | 31.6% |
| London range swept → NY AM **reverses** | **33.0%** (124/376), CI 28.4–37.9% | 26.0% |

**The "sweep the liquidity then reverse" pattern fails in gold at essentially the same rate it fails in NQ.** Both show reversal about one time in three — meaning **continuation is roughly twice as likely as reversal**.

Now tested across:
- NQ bull years (2023–26): 26–32%
- NQ bear year (2022): 27.8%
- NQ flat year (2018): 26–32%
- **Gold (2023–26): 33–35%**

Six years, three market regimes, two asset classes — the fade-the-sweep setup has never once approached 50%. This is about as thoroughly refuted as a pattern can be with this kind of data.

## Sweep frequency reflects gold's even session weighting

| | Gold | NQ |
|---|---|---|
| NY AM takes Asia high | 56.0% | 68.0% |
| NY AM takes Asia low | 49.8% | 63.9% |
| NY AM takes **either** side | **94.7%** | **99.4%** |

For NQ I flagged the 99.4% figure as **mechanically trivial** — NY AM's range is 2.26x Asia's, so it engulfs the smaller range by geometry alone. Gold's 94.7% is meaningfully lower, exactly as predicted by its flatter session profile (1.13x).

**The mechanism explanation holds up: sweep rate is a function of relative session size, not of liquidity-hunting behaviour.**

---

# PART 5 — SESSION CARRYOVER: COIN FLIPS AGAIN

| Test | Gold | NQ (bull years) |
|---|---|---|
| London → NY AM | 47.9% (205/428) | 48.2% |
| Asia → NY AM | 50.3% (217/431) | 52.0% |
| NY AM → NY PM | 50.6% (217/429) | 49.3% |

**All three are coin flips in gold, matching NQ almost exactly.**

Recall the NQ finding: carryover was a coin flip in bull years and in flat 2018, but appeared at 61.6% in 2022's sustained one-way decline — leading to the conclusion that it's a **trend-strength effect, not a structural one**.

Gold rose +119% over this period, which sounds like a strong trend — but that was a grinding multi-year advance, not a persistent one-way move like 2022's collapse. Carryover stayed absent, which is **consistent with** the trend-strength explanation rather than contradicting it.

**Conclusion holds across instruments:** session-to-session directional carryover is not a usable setup. It appears only in violently persistent trends, where it functions as a regime indicator.

---

# PART 6 — INTRADAY RANGE STRUCTURE

| Metric | Gold | NQ |
|---|---|---|
| Morning-range vs day-range correlation | **r=0.919** | r=0.783 |
| Median % of day's range made by 11:30 | **83.8%** | 79.8% |

**Gold's morning range predicts its full-day range even more tightly than NQ's does** — r=0.919 is the highest correlation found anywhere across this entire body of work, NQ included.

By 11:30 ET, the median gold session has already established **83.8% of its entire daily range**. Gold's afternoon is even more of a spent force than NQ's.

**This is arguably gold's single most usable finding.** By late morning you have a very high-confidence estimate of the day's total available range — directly informing targets and sizing.

---

# PART 7 — OTHER PARAMETERS

## First-10-minute direction persistence

| Gold | NQ |
|---|---|
| **59.5%** (266/447), CI 54.9–64.0% | 67.3% |

Weaker in gold, though still above a coin flip — the confidence interval excludes 50%, so it's a real if modest effect.

## 10:00–10:30 reversal window
Threshold scaled proportionally (13.3% of average daily range = $4.40 in gold, matching NQ's 40-point threshold on a ~300-point range).

| Gold | NQ |
|---|---|
| **36.9%** (166/450), CI 32.6–41.4% | 30.6% |

Gold shows a slightly higher reversal rate in this window. Both sit in the 30–37% band, meaning in both instruments roughly **two out of three days produce no confirmed reversal** there.

## Overnight range 50% consequent encroachment

| Gold | NQ |
|---|---|
| **54.9%** (235/428), CI 50.2–59.6% | **75.8%** |

**This is the largest divergence between the two instruments, and it is real, not a data artifact.** I re-ran it restricted to sessions with ≥120 overnight bars (median coverage is 186 of ~186 possible), and the result barely moved.

**Interpretation:** NQ reliably returns to its overnight midpoint — a genuine value-area magnet effect. Gold does so only marginally more often than chance. Gold's overnight session carries real informational content (Asian physical demand, European macro) rather than positioning noise to be retraced, so its overnight range behaves as a legitimate directional move rather than a range to be filled.

**Do not port the NQ 75.8% overnight-midpoint expectation to gold. It does not transfer.**

## Weekly lookback
*(computed only on genuinely consecutive week pairs with ≥4 sessions each, to avoid coverage gaps)*

| Metric | Gold | NQ |
|---|---|---|
| Prior week's HIGH revisited | 46.4% (26/56), CI 34.0–59.3% | 63.7% |
| Prior week's LOW revisited | 25.0% (14/56), CI 15.5–37.7% | 38.0% |

Both lower than NQ. The **high-over-low asymmetry is preserved** (46.4% vs 25.0%), consistent with gold's strong uptrend — matching the NQ finding that revisit asymmetry follows the prevailing trend. Sample is small (n=56) after filtering; treat as directional only.

## Day of week

| Day | n | Avg range | Avg net | % up |
|---|---|---|---|---|
| Monday | 82 | $29.12 | +$1.08 | 50.0% |
| Tuesday | 93 | $31.59 | +$0.73 | 46.2% |
| Wednesday | 93 | $35.08 | +$0.72 | 48.4% |
| **Thursday** | 91 | **$36.30** | +$0.64 | 52.7% |
| Friday | 91 | $31.85 | **+$1.25** | 50.5% |

**Gold's day-of-week profile is remarkably flat** — every day sits between 46% and 53% up rate, with no meaningful directional bias.

Compare NQ, where Monday (+36.2 pts, 60% up) and Thursday (−27.4 pts, 49% up) were near-mirror opposites. **Gold shows no such pattern.** Thursday is the widest-range day in both instruments — the only day-of-week feature that transfers.

*Caveat: partially affected by the odd-month coverage bias, though weekday distribution is roughly even within covered months.*

---

# PART 8 — SUMMARY: WHAT TRANSFERS AND WHAT DOESN'T

## ✅ Transfers cleanly (validated across both instruments)

| Finding | Gold | NQ |
|---|---|---|
| **OR projection decay curve** | 27.6 / 17.8 / 11.8% | 28.7 / 15.6 / 9.0% |
| **Sweep-fade fails; continuation wins** | 33–35% reversal | 26–32% reversal |
| **Session carryover is a coin flip** | 47.9–50.6% | 48.2–52.0% |
| **NY AM is the worst breakout session** | 57.0% | 60.8% |
| **Morning range predicts day range** | r=0.919 | r=0.783 |
| **Most of day's range set by 11:30** | 83.8% | 79.8% |
| **OR breakout works (weaker in gold)** | 74.3 / 67.7% | 82.0 / 70.0% |

## ❌ Does NOT transfer — gold-specific behaviour

| Finding | Gold | NQ | Why |
|---|---|---|---|
| **Best breakout session** | **Asia 78.5%** | London 79.5% | Gold has real Asian physical demand |
| **Overnight midpoint retrace** | **54.9%** | 75.8% | Gold's overnight move carries information, isn't noise |
| **Session weighting** | NY AM = 1.13x Asia | NY AM = 2.26x Asia | Gold is genuinely 24-hour |
| **Day-of-week bias** | flat, none | Monday/Thursday split | — |
| **Peak volume time** | 08:30 & 10:00 ET | 09:30 ET | Gold trades macro data, not the equity open |

## ⛔ Cannot be assessed from this file
Monthly seasonality, quarterly bias, day-of-month, month-half effect — **all invalidated by the odd/even month coverage gap.** For gold seasonality, use the separate 16-year daily-bar analysis, which found **August (p=0.028) and January (p=0.049)** as the only significant months.

---

# PART 9 — PRACTICAL GUIDE FOR TRADING GOLD

**Highest-probability setups, in order:**

1. **Asian opening-block breakout (20:00–20:30 ET) — 78.5%.** Gold's best directional setup, with no NQ equivalent in that session. Requires a clean one-sided break.
2. **Morning range as a day-range forecast — r=0.919.** By 11:30 ET, ~84% of the day's range is already made. The strongest predictive relationship available in gold.
3. **OR breakout (9:30–10:00) — 74.3% up / 67.7% down.** Works, but weaker than in NQ.
4. **OR projection targets — 28% / 18% / 12%** at 1x / 1.5x / 2x. Nearly identical to NQ; use the same framework.
5. **London opening-block breakout — 69.3%.** Solid, but do *not* expect NQ's 79.5%.

**Do not do these in gold:**
- **Don't fade overnight sweeps** — continuation wins ~2:1, same as NQ
- **Don't expect the overnight midpoint to fill** — 54.9%, near a coin flip, unlike NQ's 75.8%
- **Don't use session direction carryover** — coin flip
- **Don't trade the NY AM open expecting reliable follow-through** — 57.0%, the weakest session
- **Don't assume NY is where the action is** — Asia's range is 88% of NY AM's

---
*All confidence intervals are 95% Wilson score intervals. Reversal thresholds scaled to instrument volatility (13.3% of average daily range). Contract roll days excluded from gap and overnight calculations. Calendar-based statistics omitted due to documented coverage bias.*
