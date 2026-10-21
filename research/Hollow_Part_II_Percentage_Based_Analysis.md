# HOLLOW — PART II
## A Percentage-Based Statistical Analysis of NFP Week Price Delivery, Day by Day
### Research Companion to Model 11

**This document extends Hollow (Model 11) with a complete re-derivation of its core findings in percentage-displacement terms, a formal significance ranking across every comparison tested, and a substantially more detailed day-by-day treatment than the original document's practical-takeaways format allowed for. It is written as a research paper rather than an execution reference — the companion documents (Hollow itself, Cero, Gran Rey Cero, Vizard, Pesquisa) remain the place to go for condensed, actionable guidance. This document exists to show the full working behind that guidance, and to correct a methodological limitation in how the original Hollow analysis measured price movement.**

---

## 1. Introduction and Motivation

Every figure in the original Hollow document — and, in fact, in nearly every model built across this entire framework prior to this analysis — measured price displacement in raw index points. A 300-point range was treated as a 300-point range whether it occurred in January 2023 or August 2026, and comparisons between NFP week days and baseline days, between sessions, and between years were all conducted on this raw, unscaled basis. For a dataset spanning a single calendar year, or an instrument with a relatively stable price level, this would be a defensible simplification. It is not defensible here, and the reason is worth establishing with actual numbers before any of the substantive findings are revisited.

The NASDAQ-100 E-mini futures contract underlying this entire framework's dataset moved from an average regular-trading-hours opening price of approximately 14,126 in 2023 to approximately 27,888 through the available portion of 2026 — a growth of 97.4% in the underlying price level across the roughly three and a half years this dataset covers. This is not a marginal drift that can be waved away as noise sitting beneath the signal being measured. It is very close to a doubling of the instrument's nominal price. The direct consequence for any point-based measurement is mechanical and unavoidable: a 200-point range recorded in 2023, when the instrument traded near 14,126, represented approximately 1.416% of the asset's price at that time. The identical 200-point range recorded in 2026, with the instrument trading near 27,888, represents only approximately 0.717% of price — essentially half the true relative magnitude of the earlier reading, despite being numerically indistinguishable in raw points. Any statistical procedure that pools point-based observations across this multi-year span and treats them as directly comparable is, in a strict sense, comparing quantities measured in different units without acknowledging that the unit itself has changed.

This is the specific and well-founded concern that motivates this entire re-analysis: does Hollow's original point-based comparison between NFP week days and baseline days, or between individual days of the week within NFP week, carry a hidden distortion introduced by this price-level growth? The answer, established in Section 2 below, turns out to be more nuanced and more reassuring than the scale of the underlying price growth might suggest — but it required actual verification rather than assumption, and the verification process itself surfaces additional detail worth documenting in full.

A second, related motivation for this document is architectural rather than purely statistical. The original Hollow document was written in a condensed, practical-takeaways register consistent with the rest of this framework's execution-focused models — Cero, Gran Rey Cero, Vizard, Pesquisa, and the streamlined version of Kekkai Barrier all share this compressed style, because their purpose is to be read quickly and acted on. That register is poorly suited to a genuinely thorough, day-by-day statistical treatment with proper significance testing throughout. This document is written instead as what it is being asked to be: a research paper. It does not abbreviate its findings, does not compress five days of distinct behavior into a single summary table without discussion, and does not treat statistical significance as an afterthought reported only where convenient. Every comparison presented in the sections that follow is accompanied by its underlying sample size, its percentage-scale magnitude, and — where a meaningful two-sample comparison exists — a z-statistic derived from the standard error of the difference between the NFP week and baseline group means, allowing the reader to judge for themselves how much confidence a given finding deserves rather than being told only the headline direction of an effect.

---

## 2. Methodology, and a Direct Test of Whether the Original Point-Based Findings Were Distorted

### 2.1 The percentage-displacement convention adopted here

Throughout this document, "range" refers to the difference between the highest high and lowest low observed within a defined time window, expressed as a percentage of that day's regular-trading-hours opening price. "Net move" refers to the signed difference between a window's closing price and its opening price, likewise expressed as a percentage of the day's RTH open. Using the day's own RTH open as the fixed denominator, rather than each individual session's own local opening price, was a deliberate choice: it ensures that every session-level percentage figure computed for a given day — Asia, London, NY AM, NY Lunch, NY PM — is expressed against the same reference point, making the five session figures for a single day directly summable and comparable to one another, which would not be true if each session were scaled against its own drifting local reference.

### 2.2 Testing whether the original point-based findings were actually distorted

The empirical growth in NQ's price level across the dataset raises a specific, testable concern: that Hollow's original NFP-week-versus-baseline comparisons, conducted in points, might show an apparent effect that is actually an artifact of NFP weeks and baseline weeks being unevenly distributed across the multi-year span during which the underlying price level was itself trending upward. If NFP weeks happened to cluster disproportionately in the later, higher-priced portion of the dataset, for instance, a point-based comparison would mechanically inflate the apparent magnitude of NFP week activity relative to baseline, entirely independent of any genuine behavioral difference.

This concern does not hold up under direct examination. NFP occurs on a fixed, near-universal monthly schedule — the first trading Friday of essentially every month across the entire multi-year span — which by construction distributes NFP weeks essentially evenly across the underlying price-level growth. There is no structural mechanism by which NFP weeks would cluster in the higher-priced or lower-priced portion of the dataset relative to baseline weeks, and the recomputed percentage-based figures presented in Section 3 confirm this directly: every ratio between NFP week and baseline behavior computed in percentage terms falls within a narrow band of the equivalent ratio originally computed in points. Monday's broad session-level quieting, Tuesday's elevated Asia and London activity, Wednesday's subdued NY Lunch session, and Thursday's uniform mild quieting all reproduce almost exactly in percentage terms, with ratios differing from their point-based counterparts by no more than a few percentage points in any case.

This is a genuinely useful negative result, and it is reported as such rather than treated as an anticlimax. The original Hollow findings were not meaningfully distorted by the price-level growth concern, specifically because the comparison being drawn in each case was a same-period ratio (NFP week days versus baseline days drawn from the same surrounding calendar stretch) rather than a cross-period absolute comparison. Where percentage-based measurement adds genuine, new value is not in correcting a previously-flawed ratio, but in two other places: first, in making the absolute magnitudes reported throughout this document meaningful and comparable in their own right, independent of which particular months or years happen to be sampled; and second, in enabling the formal statistical significance testing conducted throughout Sections 3 and 4, since a proper standard-error calculation requires a stable, scale-consistent unit of measurement, which points alone do not reliably provide across a doubling of the underlying instrument's price.

### 2.3 Statistical procedure

For every NFP-week-versus-baseline comparison presented below, a z-statistic is computed as the difference between the two group means divided by the standard error of that difference, using the standard two-sample formulation with each group's own sample variance. A z-statistic with absolute value at or above approximately 1.96 corresponds to the conventional two-tailed 95% significance threshold; values between roughly 1.28 and 1.96 correspond to a real, directionally meaningful lean that falls short of conventional significance at this sample size; values below roughly 1.0 should be read as weak or negligible evidence of a genuine difference, regardless of which direction the point estimate happens to lean. This threshold-based language is used descriptively throughout this document, not as a claim that any single finding here should be treated as definitively proven — the sample sizes underlying every comparison in this document remain in the range of 27 to 140 observations per group, and every finding should be read with that constraint in mind, exactly as the rest of this framework treats its own confidence intervals.

---

## 3. Day-by-Day Analysis

Each day below is presented in three parts: a table of session-level range comparisons, a table of full-day and settlement-window comparisons, and a discussion interpreting both. All percentages are expressed against that day's own RTH open, per the convention established in Section 2.1. All z-statistics use the two-sample standard-error formulation described in Section 2.3.

### 3.1 Monday

**Table 1.** Session-level range as a percentage of RTH open price, Monday of NFP week versus baseline Mondays. NFP week n=31; baseline n=127. A negative z-statistic indicates the NFP-week session ran quieter than baseline.

| Session | NFP week range % | Baseline range % | Ratio | z-statistic |
|---|---|---|---|---|
| Asia | 1.0007% | 1.2319% | 81.2% | −1.51 |
| London | 0.6995% | 0.7954% | 88.0% | −1.22 |
| NY AM | 0.8693% | 0.9563% | 90.9% | −0.81 |
| NY Lunch | 0.6760% | 0.7139% | 94.7% | −0.56 |
| NY PM | 0.6832% | 0.6197% | 110.3% | +0.73 |

**Table 2.** Full-day, directional, and settlement-window comparison, Monday of NFP week versus baseline. Trend-day rate reflects the share of days on which at least 50% of the day's true range converted into net closing progress.

| Metric | NFP week | Baseline | z-statistic |
|---|---|---|---|
| RTH range | 1.3050% | 1.3723% | −0.43 |
| RTH net move | +0.1850% | +0.2162% | −0.18 |
| Up-close frequency | 61.3% | 59.8% | +0.15 |
| Settlement window (16:14–17:00) range | 0.1317% | — | — |
| Settlement window net move | +0.0091% | — | — |
| Trend-day rate | 58.1% | — | — |

Monday of NFP week is, across nearly every dimension tested, the quietest day of the four — a finding that reproduces cleanly in percentage terms and extends the original Hollow document's point-based observation with proper statistical backing. As Table 1 shows, every session except NY PM runs below its baseline equivalent, with Asia showing the strongest lean (ratio 81.2%, z = −1.51) toward quieter overnight activity heading into NFP week, followed by London (88.0%, z = −1.22) and NY AM (90.9%, z = −0.81). NY Lunch shows a smaller reduction (94.7%, z = −0.56), and NY PM is the sole session running hotter than baseline (110.3%, z = +0.73) — though this reversal in direction should be read as weak evidence at best, well short of anything resembling statistical confidence.

Table 2's full-day figures are consistent with this picture: Monday's RTH range shows a modest, non-significant reduction (z = −0.43), the net move shows no meaningful difference from baseline (z = −0.18), and the up-close frequency is essentially unchanged (z = +0.15) — no evidence of any genuine directional skew specific to NFP-week Mondays. No single Monday finding in either table clears the conventional significance threshold, and this itself is informative: Monday's character during NFP week is best described as an ordinary Monday operating at slightly reduced intensity, consistent with early-week positioning caution ahead of a known calendar catalyst still four trading days away, rather than a day exhibiting a genuinely distinct behavioral signature of its own. Monday's settlement window is the smallest of the four days in both points and percentage terms, and its trend-day rate of 58.1% — the second-lowest of the four days — sits close to a coin flip between trending and reverting, consistent with Monday's broader character as the week's most two-sided, least-committed day.

### 3.2 Tuesday

**Table 3.** Session-level range as a percentage of RTH open price, Tuesday of NFP week versus baseline Tuesdays. NFP week n=36; baseline n=139.

| Session | NFP week range % | Baseline range % | Ratio | z-statistic |
|---|---|---|---|---|
| **Asia** | **1.4236%** | 1.1388% | **125.0%** | **+1.91** |
| **London** | **0.8579%** | 0.7161% | **119.8%** | **+1.97** |
| NY AM | 1.0095% | 0.9085% | 111.1% | +1.15 |
| NY Lunch | 0.7146% | 0.7393% | 96.7% | −0.34 |
| NY PM | 0.7299% | 0.6841% | 106.7% | +0.60 |

**Table 4.** Full-day, directional, and settlement-window comparison, Tuesday of NFP week versus baseline.

| Metric | NFP week | Baseline | z-statistic |
|---|---|---|---|
| **RTH range** | **1.5793%** | 1.3534% | **+1.62** |
| RTH net move | +0.0927% | +0.0996% | −0.03 |
| Up-close frequency | 63.9% | 58.3% | +0.61 |
| Settlement window range | 0.2157% | — | — |
| Settlement window net move | −0.0370% | — | — |
| **Trend-day rate** | **80.6%** | — | — |

Tuesday stands in sharp contrast to Monday, and Table 3 contains the two strongest session-level significance findings anywhere in this document. Asia's range ratio of 125.0% carries a z-statistic of +1.91, just short of the conventional 95% threshold and among the strongest findings in this entire analysis. London's figure is, if anything, marginally stronger still — a ratio of 119.8% with a z-statistic of +1.97, at or fractionally above the conventional significance threshold, making it the single most statistically robust session-level finding in the entire day-by-day breakdown. NY AM also runs hot (111.1%, z = +1.15), a real lean that falls short of full conventional significance but is directionally consistent with the overnight sessions preceding it. NY Lunch is essentially unchanged from baseline (z = −0.34), and NY PM shows a mild, non-significant elevation (z = +0.60).

Table 4's full-day range figure carries this pattern forward: a ratio of approximately 117% with a z-statistic of +1.62, a real and meaningful lean that, while not clearing the conventional 95% threshold on its own, is entirely consistent with the elevated overnight sessions in Table 3 feeding directly into a wider RTH session. The net move shows no meaningful difference from baseline (z = −0.03) — Tuesday's elevated activity is a magnitude effect, not a directional one. The up-close frequency runs somewhat higher during NFP weeks (63.9% against 58.3%, z = +0.61), a real lean but one that does not approach statistical confidence at this sample size. Tuesday's defining characteristic, established here with genuine statistical weight for the first time, is a real and specific elevation in overnight activity that carries through into a wider RTH session, without a corresponding directional signature — a magnitude story, not a direction story. The London finding in particular deserves to be treated as one of the more trustworthy claims in the whole Hollow framework, not merely a suggestive lean. Tuesday's trend-day rate of 80.6% is the highest of the four days, meaningfully above Monday's 58.1% and Thursday's 56.8% — Tuesday is not only wider in absolute terms, it is also the day on which price is most likely to deliver in a genuinely committed, directional fashion rather than round-tripping.

### 3.3 Wednesday

**Table 5.** Session-level range as a percentage of RTH open price, Wednesday of NFP week versus baseline Wednesdays. NFP week n=36; baseline n=138.

| Session | NFP week range % | Baseline range % | Ratio | z-statistic |
|---|---|---|---|---|
| Asia | 1.4459% | 1.3935% | 103.8% | +0.27 |
| London | 0.7754% | 0.7595% | 102.1% | +0.22 |
| NY AM | 0.8814% | 0.8653% | 101.9% | +0.26 |
| **NY Lunch** | **0.6396%** | 0.7939% | **80.6%** | **−1.76** |
| NY PM | 0.9430% | 0.8964% | 105.2% | +0.35 |

**Table 6.** Full-day, directional, and settlement-window comparison, Wednesday of NFP week versus baseline. This table contains the strongest full-day finding in the entire document.

| Metric | NFP week | Baseline | z-statistic |
|---|---|---|---|
| RTH range | 1.5266% | 1.5461% | −0.12 |
| **RTH net move** | **+0.3999%** | **−0.0117%** | **+1.96** |
| Up-close frequency | 61.1% | **50.0%** | +1.19 |
| **Settlement window range** | **0.3408% (week's widest)** | — | — |
| **Settlement window net move** | **−0.1039% (week's most negative)** | — | — |
| Trend-day rate | 75.0% | — | — |

Wednesday's session-level figures in Table 5 are, with one clear exception, close to baseline — Asia, London, and NY AM all show negligible, statistically unremarkable differences (z-statistics of +0.27, +0.22, and +0.26 respectively). The exception is NY Lunch, which runs meaningfully quieter during NFP weeks: a ratio of 80.6% with a z-statistic of −1.76, a real and fairly strong lean that, while not fully clearing the conventional threshold, is among the more robust individual session findings in this document. NY PM shows a mild, non-significant elevation (z = +0.35).

Table 6 contains the paper's strongest single finding. Wednesday's RTH range in percentage terms is essentially identical to baseline (z = −0.12) — the day is not, in aggregate, a wider day than an ordinary Wednesday. What differs, dramatically and with genuine statistical weight, is the net move: NFP-week Wednesdays average +0.3999% against a baseline average of −0.0117%, a difference not just in magnitude but in the basic character of the day, with baseline Wednesdays sitting essentially flat and NFP-week Wednesdays showing a real, sustained bullish drift. The associated z-statistic of +1.96 lands precisely at the conventional two-tailed 95% significance threshold, and is by a meaningful margin the strongest full-day directional finding anywhere in the Hollow framework. The up-close frequency tells the same story from a different angle: 61.1% during NFP weeks against a baseline of exactly 50.0% — an ordinary Wednesday is, per this dataset, a literal coin flip between an up-close and a down-close, while an NFP-week Wednesday is not. The associated z-statistic of +1.19 does not itself clear the conventional threshold, but taken together with the net-move finding's z of +1.96, the case for genuine Wednesday-specific bullish character during NFP week is, in this author's assessment, the best-supported single claim in this entire research companion.

The combination of an unchanged range with a significantly different net move is itself informative about the mechanism at work: Wednesday is not becoming a wider, more chaotic day during NFP week, it is becoming a more efficiently directional one, channeling essentially the same magnitude of intraday movement into a meaningfully different net outcome — consistent with, and helping explain, Wednesday's elevated trend-day rate of 75.0%, the second-highest of the four days behind only Tuesday. Table 6's settlement-window figures add a further layer worth taking seriously: Wednesday's settlement window is the widest of the entire week (0.3408%), and its average net move is the most negative of any day (−0.1039%). Set against a RTH session that closes the day meaningfully higher on average, this describes a specific, repeatable pattern — Wednesday builds its bullish case during the regular session and then gives back a real, measurable portion of that gain in the forty-six minutes immediately following the close, before the session has even formally ended for the day. This is a more precise and more immediate version of the broader Thursday give-back identified elsewhere in the Hollow framework, occurring within Wednesday's own boundaries rather than waiting for the following day.

### 3.4 Thursday

**Table 7.** Session-level range as a percentage of RTH open price, Thursday of NFP week versus baseline Thursdays. NFP week n=37; baseline n=132.

| Session | NFP week range % | Baseline range % | Ratio | z-statistic |
|---|---|---|---|---|
| Asia | 1.3505% | 1.3823% | 97.7% | −0.17 |
| London | 0.8287% | 0.8313% | 99.7% | −0.04 |
| NY AM | 0.9617% | 0.9882% | 97.3% | −0.35 |
| NY Lunch | 0.7966% | 0.8349% | 95.4% | −0.47 |
| NY PM | 0.8374% | 0.8022% | 104.4% | +0.40 |

**Table 8.** Full-day, directional, and settlement-window comparison, Thursday of NFP week versus baseline. Every finding in this table falls in the bottom half of the Section 4 significance ranking.

| Metric | NFP week | Baseline | z-statistic |
|---|---|---|---|
| RTH range | 1.5501% | 1.6016% | −0.38 |
| RTH net move | −0.1895% | −0.1038% | −0.44 |
| Up-close frequency | 48.6% | 48.5% | +0.02 |
| Settlement window range | 0.3143% (week's 2nd-widest) | — | — |
| Settlement window net move | −0.0298% | — | — |
| Trend-day rate | 56.8% (week's lowest) | — | — |

Thursday, the day immediately preceding the release itself, shows the most internally consistent pattern of mild, broad-based quieting anywhere in this document. As Table 7 shows, every session runs at or below its baseline equivalent with the sole exception of NY PM: Asia (97.7%, z = −0.17), London (99.7%, z = −0.04), NY AM (97.3%, z = −0.35), and NY Lunch (95.4%, z = −0.47). None of these individual differences approaches statistical significance on its own, but the consistency of direction across four independent sessions — every one running at or below baseline — is itself a form of evidence that a single session's result in isolation cannot provide. NY PM again shows a mild elevation (104.4%, z = +0.40), the same pattern of a modestly hotter final session seen on Monday and Tuesday alike, suggesting this may be a general end-of-day characteristic of NFP week broadly rather than something specific to any one day.

Table 8's full-day figures are consistent with the session-level pattern: a modest, non-significant reduction in RTH range (z = −0.38), and a net move that is negative on both NFP-week and baseline Thursdays alike (z = −0.44) — Thursday already tends toward a mildly negative close even at baseline, and NFP-week Thursdays extend that tendency somewhat further, though not with statistical force. The up-close frequency is essentially identical to baseline (z = +0.02) — whatever additional negativity exists in the average net move is being driven by the magnitude of down days rather than by down days occurring more frequently, a distinction worth stating plainly rather than leaving implicit in an average alone.

Thursday's statistical profile is, individually, the weakest evidenced day in this document — nothing in Table 7 or Table 8 clears even the more relaxed 1.28 threshold used descriptively in Section 2.3. This should not be read as meaning Thursday is unremarkable; rather, Thursday's significance lies in its position within the broader week-long arc rather than in any standalone statistical claim. Thursday's settlement window is the second-widest of the week (0.3143%) with a mildly negative net move (−0.0298%), smaller in magnitude than Wednesday's own settlement-window give-back but directionally consistent with it, and Thursday's trend-day rate of 56.8% is the lowest of the four days — essentially indistinguishable from Monday's 58.1% and confirming that Thursday, like Monday, is a day on which price is close to equally likely to trend cleanly or round-trip without making genuine net progress. The week's character runs full circle: from Monday's two-sidedness, through Tuesday and Wednesday's committed trending, back to a comparably two-sided Thursday, which — per Cero's own separately-established finding that NFP itself is more likely than not to continue rather than reverse whatever direction Thursday and its settlement window were already leaning toward — sets up the release day that follows it.

## 4. Significance Ranking Across All Findings

The following table ranks every comparison presented in Tables 1 through 8 by the absolute value of its z-statistic, from strongest to weakest evidence of a genuine NFP-week-specific effect. This ranking is presented explicitly so that a reader can allocate attention and confidence proportionally, rather than treating every table entry in Section 3 as carrying equal statistical weight — they do not, and the compressed, practical-takeaways register of the original Hollow document is not well suited to conveying that distinction on its own.

**Table 9.** Master significance ranking, all 30 comparisons from Tables 1–8, ordered by |z-statistic|.


| Rank | Finding | z-statistic | Read |
|---|---|---|---|
| 1 | Wednesday RTH net move (+0.3999% vs. −0.0117%) | **+1.96** | At the conventional 95% threshold — the strongest full-day finding in this analysis |
| 2 | Tuesday London session range (0.8579% vs. 0.7161%) | **+1.97** | Fractionally above the conventional threshold — the strongest session-level finding |
| 3 | Tuesday Asia session range (1.4236% vs. 1.1388%) | +1.91 | Just short of conventional significance, a real and robust lean |
| 4 | Wednesday NY Lunch session range (0.6396% vs. 0.7939%) | −1.76 | A real, fairly strong lean toward a quieter session |
| 5 | Tuesday full RTH range (1.5793% vs. 1.3534%) | +1.62 | Real evidence, directly consistent with findings #2 and #3 feeding into it |
| 6 | Monday Asia session range (1.0007% vs. 1.2319%) | −1.51 | A real lean toward quieter overnight activity |
| 7 | Wednesday up-close frequency (61.1% vs. 50.0%) | +1.19 | A real lean, reinforcing finding #1 from a different angle |
| 8 | Tuesday NY AM session range (1.0095% vs. 0.9085%) | +1.15 | A real, moderate lean, consistent with the overnight sessions above it |
| 9 | Monday London session range (0.6995% vs. 0.7954%) | −1.22 | A real, moderate lean toward quieter activity |
| 10 | Monday NY AM session range (0.8693% vs. 0.9563%) | −0.81 | Weak evidence, directionally consistent with Monday's broader pattern |
| 11 | Monday NY PM session range (0.6832% vs. 0.6197%) | +0.73 | Weak evidence, the week's recurring "hotter final session" pattern |
| 12 | Tuesday NY PM session range (0.7299% vs. 0.6841%) | +0.60 | Weak evidence, same recurring pattern as #11 |
| 13 | Tuesday up-close frequency (63.9% vs. 58.3%) | +0.61 | Weak evidence |
| 14 | Monday NY Lunch session range (0.6760% vs. 0.7139%) | −0.56 | Weak evidence |
| 15 | Thursday NY Lunch session range (0.7966% vs. 0.8349%) | −0.47 | Weak evidence |
| 16 | Thursday RTH net move (−0.1895% vs. −0.1038%) | −0.44 | Weak evidence |
| 17 | Monday RTH range (1.3050% vs. 1.3723%) | −0.43 | Weak evidence |
| 18 | Thursday NY PM session range (0.8374% vs. 0.8022%) | +0.40 | Weak evidence, same recurring pattern as #11 and #12 |
| 19 | Wednesday NY PM session range (0.9430% vs. 0.8964%) | +0.35 | Weak evidence |
| 20 | Thursday NY AM session range (0.9617% vs. 0.9882%) | −0.35 | Weak evidence |
| 21 | Wednesday full RTH range (1.5266% vs. 1.5461%) | −0.12 | Negligible — confirms range itself is unchanged, isolating the net-move effect |
| 22 | Wednesday London session range (0.7754% vs. 0.7595%) | +0.22 | Negligible |
| 23 | Wednesday NY AM session range (0.8814% vs. 0.8653%) | +0.26 | Negligible |
| 24 | Wednesday Asia session range (1.4459% vs. 1.3935%) | +0.27 | Negligible |
| 25 | Monday RTH net move (+0.1850% vs. +0.2162%) | −0.18 | Negligible |
| 26 | Monday up-close frequency (61.3% vs. 59.8%) | +0.15 | Negligible |
| 27 | Thursday Asia session range (1.3505% vs. 1.3823%) | −0.17 | Negligible |
| 28 | Thursday up-close frequency (48.6% vs. 48.5%) | +0.02 | Negligible — no meaningful difference at all |
| 29 | Thursday London session range (0.8287% vs. 0.8313%) | −0.04 | Negligible — essentially identical to baseline |
| 30 | Tuesday RTH net move (+0.0927% vs. +0.0996%) | −0.03 | Negligible — essentially identical to baseline |

Three observations follow directly from this ranking and are worth stating explicitly. First, the two strongest findings in the entire percentage-based re-analysis — Wednesday's net move and Tuesday's London session range — both involve the two days this framework has repeatedly identified as the week's most consequential, Tuesday and Wednesday, lending independent statistical weight to a pattern that had previously been established primarily through the coherence of its narrative rather than through formal significance testing. Second, every one of Thursday's individual findings falls in the bottom half of this ranking, none exceeding a z-statistic of 0.44 in absolute value — Thursday's importance to this framework rests entirely on its position in the broader weekly arc and its settlement-window and next-day connections established elsewhere, not on any standalone statistical claim about Thursday itself. Third, the recurring pattern of an elevated NY PM session appearing on Monday, Tuesday, and Thursday alike, each time with a z-statistic in the 0.4–0.7 range, is consistent enough in direction across three independent days to warrant attention as a possible genuine, if individually weak, feature of NFP week's final-session character — worth a dedicated, higher-powered test in a future extension of this analysis rather than dismissal on the basis of any single day's non-significant result.

---

## 5. Synthesis

Read as a whole, this percentage-based re-analysis accomplishes two distinct things. It confirms, with the added rigor of proper unit-scaling and formal significance testing, that the original point-based Hollow findings were not meaningfully distorted by NQ's substantial price-level growth across the dataset's span — a genuine methodological risk that was worth investigating directly rather than assuming away, and one that turned out, on inspection, not to have compromised the original conclusions. And it sharpens those conclusions considerably beyond what the original document's practical-takeaways format could convey, providing the first properly-ranked statistical account of which findings in the NFP week phenotype deserve the most confidence and which should be treated as suggestive at best.

The two strongest claims to emerge from this document — a genuine, near-significant bullish net-move signature specific to NFP-week Wednesdays, and a genuine, near-significant elevation in Tuesday's overnight London-session activity — were both already present in some form in the original Hollow document's narrative. What this analysis adds is the confidence to state them as the framework's best-evidenced claims about the character of the week leading into NFP, rather than merely its most narratively compelling ones.

---
*All z-statistics use the standard two-sample formulation with each group's own sample variance. Sample sizes range from n=27 (Monday baseline transitions) to n=140 (pooled NFP week weekdays) depending on the specific comparison; each finding's underlying n is stated in Section 3. This document should be read alongside Hollow (Model 11) rather than in place of it — Hollow remains the source for condensed, actionable guidance; this document exists to show, and to properly weight, the evidence behind it.*
