# Gold vs Silver — Quantitative Time & Price Analysis

**Datasets:** GC and SI continuous, 5-minute bars, Jan 2023 – Aug 2026
**Usable sessions:** Gold **450** · Silver **453**
**Period performance:** Gold **+119.4%** ($1,847 → $4,052) · Silver **+189.5%** ($23.80 → $68.89)

---

# ⚠️ PART 0 — A CRITICAL CONSTRAINT ON THIS COMPARISON

## The two files have near-complementary coverage gaps

| Month | Gold usable days | Silver usable days |
|---|---|---|
| Jan | **76** | 8 |
| Feb | 8 | **69** |
| Mar | **78** | 8 |
| Apr | 7 | **75** |
| May | **79** | 8 |
| Jun | 8 | **73** |
| Jul | **79** | 8 |
| Aug | 5 | **77** |
| Sep | **42** | 6 |
| Oct | 6 | **68** |
| Nov | **56** | **53** |
| Dec | 6 | 0 |

Gold's intraday data is dense in **odd** months; silver's in **even** months. This follows from each metal's contract expiry cycle and how the continuous series was assembled.

## Consequence: only 65 days have usable data for BOTH metals — and 53 are in November

**This makes true paired analysis impossible.** The following cannot be computed from these files:

- Gold/silver ratio dynamics
- Cross-metal correlation
- Lead-lag relationships (does silver follow gold intraday?)
- Divergence signals between the two
- Relative strength analysis

Any of those computed on 65 days concentrated in one month would be meaningless, and I'd rather say so than produce a number that looks authoritative.

**What IS valid:** each metal has ~450 independent sessions. Running the identical parameter suite on each and comparing the resulting *statistics* is legitimate — that's a distribution-level comparison, not a paired one. That is what this document does.

**Also unusable:** monthly, quarterly, day-of-month, and month-half statistics for both metals, for the same coverage reason.

---

# PART 1 — THE FUNDAMENTAL VOLATILITY DIFFERENCE

Raw prices aren't comparable ($4,052 vs $68.89), so everything below is normalised as **percentage of price**.

| Metric | Gold | Silver | Ratio |
|---|---|---|---|
| Avg daily RTH range | **1.01%** | **2.19%** | **Silver 2.17x** |
| Median daily RTH range | 0.88% | 1.79% | Silver 2.03x |

**Silver is roughly 2.2x as volatile as gold on a percentage basis.** This is the single most important number for anyone sizing positions across the two — identical dollar risk requires roughly half the position size in silver.

## Session structure, normalised

| Session | Gold (% of price) | vs Asia | Silver (% of price) | vs Asia |
|---|---|---|---|---|
| Asia | 0.588% | 1.00x | 1.369% | 1.00x |
| London | 0.546% | 0.93x | 1.150% | 0.84x |
| **NY AM** | **0.699%** | **1.19x** | **1.524%** | **1.11x** |
| NY Lunch | 0.404% | 0.69x | 0.836% | 0.61x |
| NY PM | 0.428% | 0.73x | 0.847% | 0.62x |

**Both metals show the same structural shape: extremely flat session weighting.** NY AM is only 1.19x Asia in gold and 1.11x in silver.

For context, NQ's NY AM is **2.26x** its Asian session. Both metals are genuinely 24-hour instruments in a way equity index futures are not — Asian and London hours carry nearly the same weight as New York.

**Silver's session profile is marginally flatter than gold's**, meaning silver is, if anything, even less New York-centric.

---

# PART 2 — OPENING RANGE (9:30–10:00 ET)

## 2.1 Breakout hold rate — the metals are mirror images

| Direction | Gold | Silver |
|---|---|---|
| OR-**high** break holds | **74.3%** (110/148), CI 66.7–80.7% | **69.2%** (99/143), CI 61.2–76.2% |
| OR-**low** break holds | **67.7%** (86/127), CI 59.2–75.2% | **76.7%** (112/146), CI 69.2–82.8% |

**The asymmetry inverts between the two metals.** Gold's upside breaks are more reliable than its downside (74.3% vs 67.7%). Silver is the opposite — downside breaks hold better (76.7% vs 69.2%).

**This is genuinely counterintuitive** given silver rose *more* than gold over the period (+189.5% vs +119.4%). If breakout asymmetry simply followed trend, silver should show the stronger upside bias. It shows the reverse.

**Honest caveat:** the confidence intervals overlap substantially (gold high 66.7–80.7 vs silver high 61.2–76.2). The inversion is suggestive rather than conclusively established. What *is* solid: both metals show the OR breakout working in both directions at roughly 67–77%.

## 2.2 OR projection targets — extremely close

| Multiple | Gold up | Gold down | Silver up | Silver down |
|---|---|---|---|---|
| **1.0x OR** | 27.6% | 28.7% | 24.3% | 28.0% |
| **1.5x OR** | 17.8% | 18.2% | 15.5% | 18.1% |
| **2.0x OR** | 11.8% | 12.0% | 9.5% | 11.9% |

**The downside columns are nearly identical** (28.7/18.2/12.0 vs 28.0/18.1/11.9). Gold runs slightly higher on the upside at every multiple.

Both metals reproduce the same decay curve — roughly **28% → 18% → 12%**, each step cutting the probability by about a third.

**This now holds across three instruments** (gold, silver, and NQ at 28.7/15.6/9.0). The Opening Range as a projection unit appears to describe something general about intraday range distribution rather than an instrument-specific quirk. That is meaningful cross-validation.

---

# PART 3 — SESSION OPENING-BLOCK BREAKOUTS

Does a clean one-sided break of a session's first 30 minutes hold to that session's close?

| Session | Gold | Silver |
|---|---|---|
| **Asia (20:00–20:30)** | **78.5%** (175/223), CI 72.6–83.4% | **80.8%** (156/193), CI 74.7–85.8% |
| **London (02:00–02:30)** | 69.3% (178/257), CI 63.4–74.6% | **79.9%** (215/269), CI 74.7–84.3% |
| NY PM (13:30–14:00) | 67.3% (181/269) | 65.7% (190/289) |
| NY AM (09:30–10:00) | **57.0%** (180/316) | **57.9%** (195/337) |
| NY Lunch (11:30–12:00) | 59.6% (198/332) | 55.3% (176/318) |

## Three findings here

**1. Asia is the strongest session for both metals.** Gold 78.5%, silver 80.8%. Both are the highest-probability directional setup available in their respective instruments. This is a genuine precious-metals characteristic — Asian physical demand (Shanghai, India) and Japanese investment flow create real participation in those hours.

**2. Silver's London session is dramatically better than gold's** — 79.9% vs 69.3%, a 10.6-point gap with non-overlapping confidence intervals (74.7–84.3 vs 63.4–74.6). This is a real, statistically distinguishable difference. **Silver gives you two strong sessions (Asia AND London); gold gives you one.**

Plausible mechanism: London is the historic centre of physical silver trade (LBMA silver fix), and silver's industrial demand component generates European-hours flow that gold lacks.

**3. NY AM is the worst session for both metals — 57.0% and 57.9%.** Nearly identical, and both barely above a coin flip.

Combined with the NQ finding (60.8%), the most-watched session of the day is the least directionally reliable in **all three instruments tested**. This is one of the most consistent results in the entire body of work.

---

# PART 4 — SWEEP BEHAVIOUR: THE FADE FAILS IN BOTH METALS

| Test | Gold | Silver |
|---|---|---|
| Asia range swept → NY AM **reverses** | 35.0% (127/363), CI 30.3–40.0% | 37.3% (134/359), CI 32.5–42.4% |
| London range swept → NY AM **reverses** | 33.0% (124/376), CI 28.4–37.9% | 32.4% (115/355), CI 27.7–37.4% |

**Both metals reverse only about one time in three.** Continuation is roughly twice as likely as reversal in both.

The "sweep the liquidity then reverse" setup has now been tested across:

| Instrument / regime | Reversal rate |
|---|---|
| NQ bull (2023–26) | 26–32% |
| NQ bear (2022) | 27.8% |
| NQ flat (2018) | 26–32% |
| Gold (2023–26) | 33–35% |
| **Silver (2023–26)** | **32–37%** |

**Three instruments, three market regimes, six years — never once approaching 50%.** If you are fading sweeps as a default, the data across every test says you are systematically on the wrong side.

## Sweep frequency confirms the geometric mechanism

| | Gold | Silver | NQ |
|---|---|---|---|
| NY AM takes either side of Asia range | 94.7% | 92.5% | **99.4%** |
| NY AM takes either side of London range | 95.9% | 95.0% | 98.7% |

NQ's near-certain 99.4% was flagged earlier as **mechanically trivial** — its NY AM range is 2.26x Asia's, so it engulfs the smaller range by geometry. Both metals, with much flatter session profiles (1.11–1.19x), come in lower at 92.5–95.9%.

**The prediction held.** Sweep rate is a function of relative session size, not of liquidity-hunting behaviour. This is now confirmed across three instruments with different session structures.

---

# PART 5 — SESSION CARRYOVER: COIN FLIPS EVERYWHERE

| Test | Gold | Silver |
|---|---|---|
| London → NY AM | 47.9% (205/428) | 50.9% (219/430) |
| Asia → NY AM | 50.3% (217/431) | 50.4% (215/427) |
| NY AM → NY PM | 50.6% (217/429) | 50.7% (214/422) |

**All six tests are coin flips.** Silver's three results cluster remarkably tightly at 50.4–50.9%.

This matches NQ's bull-year and flat-year results, and reinforces the earlier conclusion: directional carryover between sessions appeared *only* in NQ's 2022 sustained one-way decline (61.6%), making it a **trend-strength indicator rather than a tradeable setup**.

Both metals rose sharply over this period (+119% and +190%), but as grinding multi-year advances rather than persistent one-way moves — and carryover stayed absent, consistent with that interpretation.

---

# PART 6 — INTRADAY RANGE STRUCTURE

| Metric | Gold | Silver |
|---|---|---|
| Morning-range vs day-range correlation | **r=0.919** | **r=0.839** |
| Median % of day's range made by 11:30 ET | 83.8% | **87.6%** |

**Both metals show exceptionally strong morning-range predictiveness**, with gold's r=0.919 the highest correlation found anywhere across this entire body of work (NQ was 0.783).

**Silver establishes even more of its range earlier** — a median 87.6% of the full day's range is complete by 11:30 ET, the highest figure of any instrument tested.

**Practical implication for both metals:** by late morning you have a high-confidence estimate of the day's total available range. In silver especially, the afternoon offers very little additional room — roughly 12% of the day's range remains after 11:30.

This is the strongest shared finding between the two metals and the most directly actionable for target-setting.

---

# PART 7 — OTHER PARAMETERS

## First-10-minute direction persistence

| Gold | Silver |
|---|---|
| 59.5% (266/447), CI 54.9–64.0% | 61.7% (274/444), CI 57.1–66.1% |

Similar in both; both real (CIs exclude 50%) but modest. Both weaker than NQ's 67.3%.

## 10:00–10:30 reversal window
*(threshold scaled to 13.3% of each instrument's average daily range — $4.40 gold, $0.132 silver)*

| Gold | Silver |
|---|---|
| 36.9% (166/450), CI 32.6–41.4% | 31.3% (142/453), CI 27.2–35.8% |

Both in the 31–37% band. **In both metals, roughly two out of three days produce no confirmed reversal in this window.**

## Overnight range 50% consequent encroachment

| Gold | Silver | NQ |
|---|---|---|
| **54.9%** (235/428), CI 50.2–59.6% | **62.8%** (275/438), CI 58.2–67.2% | **75.8%** |

**A clear ordering: NQ 75.8% > Silver 62.8% > Gold 54.9%.** Gold's confidence interval nearly touches 50% — the overnight midpoint is barely better than a coin flip as a magnet in gold.

**Interpretation:** the more an instrument's overnight session carries genuine informational content, the *less* its overnight range gets retraced. NQ's overnight is largely positioning noise that gets filled. Gold's overnight session reflects real Asian physical demand and European macro — a legitimate directional move, not a range to be retraced. Silver sits between the two.

**Do not port NQ's 75.8% expectation to either metal.**

## Weekly lookback
*(consecutive week pairs only, ≥4 sessions each, to avoid coverage gaps)*

| Metric | Gold (n=56) | Silver (n=63) |
|---|---|---|
| Prior week's HIGH revisited | 46.4%, CI 34.0–59.3% | 41.3%, CI 30–54% |
| Prior week's LOW revisited | 25.0%, CI 15.5–37.7% | 36.5%, CI 26–49% |

Gold shows a clear high-over-low asymmetry (46.4% vs 25.0%) consistent with its uptrend. **Silver's is nearly symmetric** (41.3% vs 36.5%) despite silver rising *more* — another instance of silver not behaving the way its trend would predict.

Both samples are small after filtering; treat as directional only.

## Day of week

| Day | Gold range | Gold %up | Silver range | Silver %up |
|---|---|---|---|---|
| Monday | $29.12 | 50.0% | $0.807 | **55.7%** |
| Tuesday | $31.59 | 46.2% | $0.884 | 54.2% |
| Wednesday | $35.08 | 48.4% | $0.888 | 47.8% |
| Thursday | **$36.30** | 52.7% | $1.163 | 48.4% |
| Friday | $31.85 | 50.5% | **$1.226** | **46.6%** |

**Gold's day-of-week profile is flat** — 46–53% up rate, no meaningful bias anywhere.

**Silver shows a clearer gradient**: Monday is the most bullish day (55.7% up, +$0.088 avg) and Friday the most bearish (46.6% up, **−$0.253** avg, the largest negative daily average in either metal). Silver's Friday is also its widest-range day ($1.226).

**Volatility builds through the week in silver** — $0.807 Monday rising steadily to $1.226 Friday, a 52% increase. Gold peaks Thursday instead.

*Caveat: partially affected by the coverage bias, though weekday distribution is roughly even within covered months.*

## 30-minute block volatility — where each session's energy sits

**Silver (avg range $ per 30-min block):**

| Session | Block pattern |
|---|---|
| Asia | 0.248 → 0.201 → **0.304** → 0.259 → 0.198 → 0.209 → 0.170 → 0.129 |
| London | 0.216 → 0.192 → 0.211 → 0.189 → 0.203 → 0.178 |
| **NY AM** | **0.410** → 0.345 → 0.308 |
| NY Lunch | 0.244 → 0.208 → 0.204 |
| NY PM | 0.193 → 0.177 → 0.163 → 0.164 → 0.153 |

**Silver's Asia session is bimodal** — it peaks in the *third* block (21:00–21:30 ET) at 0.304, not at the open. That's a genuine structural detail: the strongest Asian activity comes about an hour into the session, not at the bell.

**NY AM decays monotonically** (0.410 → 0.345 → 0.308), same as gold and NQ. **NY PM decays steadily with no closing spike** — unlike NQ, which showed a 23% jump in its final block. Metals have no closing-auction effect.

---

# PART 8 — THE MOST SIGNIFICANT FINDINGS, RANKED

### Tier 1 — Strongest, most actionable

| Rank | Finding | Gold | Silver |
|---|---|---|---|
| 1 | **Asia opening-block breakout** | **78.5%** | **80.8%** |
| 2 | **Silver's London opening-block breakout** | 69.3% | **79.9%** |
| 3 | **Morning range predicts day range** | r=0.919 | r=0.839 |
| 4 | **Most of day's range set by 11:30** | 83.8% | **87.6%** |

**The single best setup available across both metals is the Asian session opening-block breakout** — 78.5% in gold, 80.8% in silver, on samples of 193–223 clean occurrences. Neither metal offers anything comparable in New York hours.

**For silver specifically, London is a second high-probability window** at 79.9% — statistically distinguishable from gold's 69.3%. A silver trader has two strong sessions; a gold trader has one.

### Tier 2 — Solid

| Finding | Gold | Silver |
|---|---|---|
| OR breakout (best direction) | 74.3% up | 76.7% down |
| Overnight midpoint retrace | 54.9% | 62.8% |
| First-10-min persistence | 59.5% | 61.7% |

### Tier 3 — Refuted / no edge

| Finding | Gold | Silver |
|---|---|---|
| Sweep-then-reverse | 33–35% | 32–37% |
| Session carryover | 47.9–50.6% | 50.4–50.9% |
| NY AM opening-block breakout | 57.0% | 57.9% |

---

# PART 9 — PRACTICAL SUMMARY

## Trade these

1. **Asian opening-block breakout (20:00–20:30 ET)** — the best setup in both metals. Silver 80.8%, gold 78.5%. Requires a clean one-sided break.
2. **London opening-block breakout in SILVER (02:00–02:30 ET)** — 79.9%. Do not expect the same from gold (69.3%).
3. **Morning range as day-range forecast** — by 11:30 ET, 84% (gold) / 88% (silver) of the day's range is already made. Set targets accordingly.
4. **OR projection targets** — ~28% / 18% / 12% at 1x / 1.5x / 2x in both metals.

## Avoid these

- **Fading overnight sweeps** — continuation wins ~2:1 in both metals, same as NQ
- **NY AM breakouts for direction** — 57–58%, the weakest session in both
- **Session carryover** — all six tests were coin flips
- **Expecting the overnight midpoint to fill in gold** — 54.9%, barely better than chance
- **Assuming New York is where the action is** — Asia's range is 84–90% of NY AM's in both metals

## Sizing note

**Silver is 2.17x as volatile as gold on a percentage-of-price basis.** Equal dollar risk requires roughly half the notional exposure in silver.

---
*All confidence intervals are 95% Wilson score intervals. Reversal thresholds scaled to each instrument's volatility (13.3% of average daily range). Contract roll days excluded from overnight calculations. Calendar-based statistics and all paired cross-metal analysis omitted due to documented coverage limitations.*
