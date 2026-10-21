# SEPTEMBER 2022 — A FORENSIC CASE STUDY
## High-Time-Frame Structure, Day-by-Day Phenotypes, Economic Calendar Correlation, and Full Session-on-Session Price Delivery

**This document is a complete empirical dissection of a single calendar month — September 2022 — chosen because it sits inside the extended dataset built for this framework's FOMC (Vizard) model and represents one of the most economically eventful, and one of the worst, months of the 2022 bear market. Every day, every session, and every key reference level (RTH open/high/low/close, NDOG, NWOG, previous-day high/low, previous-week high/low) is tracked individually. Where the source data has genuine gaps or holiday distortions, that is stated plainly rather than smoothed over.**

---

## 1. Data Integrity Notes — Read This Before Anything Else

Two irregularities in the underlying data need to be on the table before any interpretation begins.

**September 5, 2022 (Labor Day) was a market holiday, not a genuine trading day, despite appearing in the raw feed.** The data shows only 210 minutes of thin, low-volume Globex-continuation activity between 9:30 and 12:59 ET, with no further prints afterward — there was no real regular session, no genuine closing settlement, and no meaningful price discovery that day. It has been excluded from every state classification, session comparison, and statistical calculation in this document. Where it is mentioned at all, it is labeled explicitly as a holiday.

**September 16, 2022 (the month's quad-witching Friday) has no RTH session in this data — because it was expiration day, not because of a data fault.** The continuous file follows NQU22 until it expires. NQU22's final settlement is set at the 9:30 open on the third Friday, so it has no RTH session that day, and the file does not switch to NQZ22 until the Sunday evening open on 18 September. The same mechanism removes every quarterly expiration Friday from the 2023–2025 continuous files used across this framework. The switch also means price steps from one contract to the next across that weekend: NQZ22 traded above NQU22 by the calendar spread (the cost of carry), so any comparison spanning 15 → 19 September mixes two contracts.

With those two exclusions, September 2022 contributed **20 genuine, fully-formed RTH trading sessions** to this analysis.

---

## 2. High-Time-Frame Context

September 2022 opened with NQ's RTH price at 12,172.25 and closed the month at 11,080.75 — a net decline of **8.97% for the month**, one of the sharper single-month drawdowns in the dataset this framework draws from. This was not a smooth, linear decline. It was a month with a genuine early-month relief rally that was then overwhelmed by three separate, back-to-back macro catalysts that arrived roughly a week apart from each other, each one deepening the decline rather than allowing consolidation between them. The month's own internal week-by-week structure, detailed in Section 4, maps this arc precisely.

The month's **total range** — from its single highest RTH print (12,766.50, set on September 12) to its lowest (11,024.25, set in the final session on September 30) — spans **1,742.25 points, or 14.4% of the month's opening price.** This is a genuinely wide-ranging month by any standard, and the section below shows exactly which days and which specific catalysts were responsible for that width.

---

**Carry note:** the 1 September open is NQU22 and the 30 September close is NQZ22. NQZ22 carried a premium over NQU22 (the cost of carry), so the −8.97% figure understates the same-contract decline and the 14.4% monthly range mixes the two contracts. Weeks 1–3 are entirely NQU22 and Weeks 4–5 entirely NQZ22, so every within-week figure below is like-for-like. The Week 4 sweep of the prior week's low compares NQZ22 with NQU22 levels. The premium works *against* a sweep, so the sweep still holds.

---

## 3. Economic Calendar Overlay

Four scheduled events fell within or adjacent to September 2022, and the correlation between these dates and the month's largest single-day moves is, without exaggeration, close to perfect.

| Date | Event | RTH % move that day | State |
|---|---|---|---|
| **Friday, Sep 2** | August Non-Farm Payrolls | **−2.279%** | Expansion |
| **Tuesday, Sep 13** | August CPI (the month's defining shock) | **−2.695% — the single largest move of the month** | Expansion |
| Friday, Sep 16 | Quarterly expiration (NQU22 settles at the 9:30 open — no RTH in the continuous file) | — | — |
| **Wednesday, Sep 21** | FOMC decision (75bp hike, third consecutive) | **−2.222%** | Expansion |
| Friday, Sep 30 | August PCE inflation (month-end) | −0.945% | Retracement |

**Three of the four analyzable scheduled catalysts this month produced the month's three largest single-day percentage declines, and all three were independently classified as "Expansion" days by this framework's own state classifier before any calendar information was even consulted.** This is a genuinely clean result: the classifier has no knowledge of the economic calendar built into it — it only looks at a day's range relative to its own trailing 20-day average and the proportion of that range that converted into net directional movement. That NFP, CPI, and FOMC each independently triggered the same classification, on the same three days the calendar says they should have, is about as strong a validation of both the state-classification framework and the CPI/NFP/FOMC models built elsewhere in this project as a single month can offer.

The September 13 CPI session deserves specific note beyond its ranking as the month's largest move: this was the release that came in meaningfully hotter than consensus expected, and the RTH decline of −2.695% substantially understates the true violence of that day — as Section 5's session breakdown shows, the overnight-into-release window absorbed the worst of it before the RTH session even opened, a pattern directly consistent with Gran Rey Cero's own finding that CPI's damage frequently concentrates outside the conventional NY AM window.

---

## 4. Week-by-Week Phenotype Analysis

| Week | Trading days | Open → Close | Net % | Week range % | Daily states |
|---|---|---|---|---|---|
| Week 1 (holiday-shortened, NFP week) | Sep 1–2 | 12172.25 → 12122.00 | **−0.413%** | 3.646% | Reversal, Expansion |
| Week 2 (Labor Day shortened) | Sep 6–9 | 12128.25 → 12589.75 | **+3.805%** | 5.638% | Retracement, Reversal, Retracement, Retracement |
| Week 3 (CPI week, Sep 16 gap) | Sep 12–15 | 12650.25 → 11944.00 | **−5.583% — the month's worst week** | 7.114% | Consolidation, Expansion, Consolidation, Reversal |
| Week 4 (FOMC week) | Sep 19–23 | 11819.75 → 11376.00 | **−3.754%** | 7.712% — the month's widest week | Retracement, Retracement, Expansion, Consolidation, Retracement |
| Week 5 (month-end) | Sep 26–30 | 11352.00 → 11080.75 | **−2.389%** | 5.191% | Retracement, Retracement, Expansion, Reversal, Retracement |

**The month's own phenotype arc is a genuine relief-rally-then-capitulation shape.** Week 1 opens the month with a mild pullback into NFP. Week 2 is the month's only genuinely positive week — a substantial +3.805% relief rally that recovered essentially all of Week 1's decline and then some, pushing NQ to its monthly high of 12,766.50 on September 12, the Monday that opened Week 3. **That high was set the trading day immediately before the CPI release** — the market's single most bullish moment of the month arrived one day before its single most damaging one. Week 3 then delivers the month's worst single week (−5.583%), driven overwhelmingly by the September 13 CPI shock, and Weeks 4 and 5 never recover — each closes lower than it opened, with FOMC week (Week 4) contributing the month's widest range of any week (7.712%) without managing a positive close, and the final week grinding the month out to its lowest close.

### NWOG Tracking

| Transition | Prior Friday close | Following Monday/Tuesday open | NWOG | NWOG % |
|---|---|---|---|---|
| Sep 2 → Sep 6 (Labor Day) | 12122.00 | 12128.25 | +6.2 | +0.052% |
| Sep 9 → Sep 12 | 12589.75 | 12650.25 | +60.5 | +0.481% |
| Sep 15 → Sep 19 | 11944.00 (NQU22) | 11819.75 (NQZ22) | n/a | **Not a valid NWOG** — spans the U22→Z22 contract switch and Friday's session |
| Sep 23 → Sep 26 | 11376.00 | 11352.00 | −24.0 | −0.211% |

**Correction:** an earlier version of this document reported a −1.040% gap into FOMC week as the month's largest NWOG. That figure compared NQU22's Thursday close with NQZ22's Monday open. It mixes two contracts separated by the calendar spread, and it also skips Friday's session, so it is not a weekly opening gap and has been withdrawn. Because NQZ22 traded at a premium to NQU22, the true same-contract decline over those days was larger than −124 points, not smaller. The size of that premium can't be recovered from this file, so no corrected figure is given.

### Previous-Week High/Low Sweep Behavior

| Week | Prior week's H/L | This week's sweep behavior | First swept on |
|---|---|---|---|
| Week 2 | 12461.50 / 12017.75 | Both swept | **Sep 6 (Tuesday)** — swept the low first |
| Week 3 | 12613.75 / 11930.00 | Both swept | **Sep 12 (Monday)** — swept the high first |
| Week 4 | 12766.50 / 11866.50 | Only the low swept | **Sep 19 (Monday)** — swept the low |
| Week 5 | 12140.50 / 11229.00 | Only the low swept | **Sep 29 (Thursday)** — took until deep in the week |

Every single week of the month, without exception, saw its previous week's low taken out. The previous week's high was only reached twice (Weeks 2 and 3) — both during the month's early relief-rally phase — and was never reached again once the CPI-driven decline took hold in Week 3. This is itself a clean, month-long confirmation of the broader bear-market character: sell-side liquidity was consistently attacked and consumed; buy-side liquidity, once the decline began in earnest, simply stopped being reached at all.

---

## 5. Day-by-Day Full Breakdown

Every trading day is presented with its state classification, percentage move, range, NDOG, previous-day high/low sweep status, and complete five-session breakdown. All session ranges and net moves are in raw points; percentage figures are expressed against that day's own RTH open.

### Week 1

**Thursday, September 1 — State: Reversal | −0.413% net for the two-day week so far**
RTH open 12172.25, close 12260.75, **+0.727%**, range 2.315% of price. NDOG −131.0 (gapped down from the prior session). Swept the previous day's low; did not reach its high.

| Session | Range | Net |
|---|---|---|
| Asia | 170.2 | −133.8 |
| London | 124.0 | +20.2 |
| NY AM | 171.2 | −119.2 |
| NY Lunch | 105.5 | +64.2 |
| **NY PM** | **227.5** | **+147.0** |

The day's entire recovery is concentrated in NY PM — the session opened under continued pressure from Asia and NY AM, and the entire +0.727% RTH gain came from a single afternoon push.

**Friday, September 2 — State: Expansion | NFP DAY | −2.279%**
RTH open 12404.75, close 12122.00. Range 3.396% of price — the month's second-widest single day. NDOG +144.0 (gapped up overnight, then fully reversed intraday). Swept the previous day's high; did not reach its low.

| Session | Range | Net |
|---|---|---|
| Asia | 65.0 | −31.2 |
| London | 188.5 | +138.2 |
| NY AM | 189.0 | −7.8 |
| **NY Lunch** | **304.5** | **−258.2** |
| NY PM | 129.2 | −14.0 |

The overnight/London session actually ran bullish into the release (+138.2), and NY AM itself was nearly flat on net (−7.8) despite a real 189-point range — the damage this day was overwhelmingly a **NY Lunch phenomenon**, not a NY AM one, with −258.2 points delivered in that window alone. This is a specific, useful confirmation of Cero's own finding that NFP's disruption frequently continues well past the initial NY AM window rather than resolving there.

### Week 2

**Tuesday, September 6 — State: Retracement | −0.977%**
Open 12128.25, close 12009.75. Range 1.971%. NDOG +6.2 (negligible gap). Swept the prior day's low (this was also the day that took out the entire prior week's low, 12017.75).

| Session | Range | Net |
|---|---|---|
| Asia | 122.0 | +27.2 |
| London | 127.5 | −34.8 |
| **NY AM** | **239.0** | **−24.8** |
| NY Lunch | 171.0 | −120.5 |
| NY PM | 103.0 | +27.5 |

**Wednesday, September 7 — State: Reversal | +1.773%**
Open 12039.75, close 12253.25. Range 2.299%. NDOG +30.0. Swept the prior day's high.

| Session | Range | Net |
|---|---|---|
| Asia | 112.8 | −30.2 |
| London | 107.2 | +50.2 |
| NY AM | 98.8 | +36.5 |
| NY Lunch | 125.0 | +77.5 |
| **NY PM** | **155.2** | **+98.2** |

A clean, steadily building bullish day — every session from London onward contributes positively, with the largest single contribution again arriving in NY PM.

**Thursday, September 8 — State: Retracement | +1.345%**
Open 12175.75, close 12339.50. Range 2.166%. NDOG −77.5 (gapped down, fully reversed). Swept the prior day's high.

| Session | Range | Net |
|---|---|---|
| Asia | 46.8 | +22.5 |
| London | 180.5 | −114.8 |
| **NY AM** | **226.0** | **+164.8** |
| NY Lunch | 241.8 | −67.0 |
| NY PM | 117.5 | +68.8 |

The single largest session contribution of the whole relief rally sits here: **+164.8 points in NY AM alone**, more than offsetting a genuinely bearish London session that preceded it.

**Friday, September 9 — State: Retracement | +1.393%**
Open 12416.75, close 12589.75. Range 1.597% — the tightest range of the relief-rally week. NDOG +77.2. Swept the prior day's high.

| Session | Range | Net |
|---|---|---|
| Asia | 85.5 | +44.8 |
| London | 125.8 | +25.2 |
| **NY AM** | **154.5** | **+142.2** |
| NY Lunch | 86.2 | +26.5 |
| NY PM | 54.8 | +2.2 |

Every single session this day is positive — a genuinely rare, fully one-directional session-by-session profile, and NY AM again carries the bulk of the day's net progress (+142.2 of the day's total +173.0-point range-to-net conversion).

### Week 3 — CPI Week

**Monday, September 12 — State: Consolidation | +0.901% — the month's high, set the day before CPI**
Open 12650.25, close 12764.25. Range just 1.018% of price — genuinely tight. NDOG +60.5. Swept the prior week's high (12613.75) — this was the sweep noted in Section 4.

| Session | Range | Net |
|---|---|---|
| Asia | 106.0 | −18.5 |
| London | 115.0 | +42.5 |
| NY AM | 114.8 | +53.0 |
| NY Lunch | 101.2 | +29.0 |
| NY PM | 86.0 | +31.5 |

The RTH high of the entire month — 12,766.50 — was printed in this session's NY PM. Twenty-four hours later, CPI would begin erasing it.

**Tuesday, September 13 — State: Expansion | CPI DAY | −2.695% — the month's single largest move**
Open 12375.00, close 12041.50. Range 3.424% of price. NDOG **−389.2**, by far the largest single gap of the entire month. Did not sweep the prior day's high or low on a closing basis, but the range shows this was the day the prior week's high definitively lost relevance.

| Session | Range | Net |
|---|---|---|
| Asia | 39.2 | +2.5 |
| **London** | **541.2** | **−397.5** |
| NY AM | 217.0 | −146.2 |
| NY Lunch | 74.0 | +23.8 |
| **NY PM** | **252.5** | **−204.2** |

This session table requires an important caveat: **CPI's 8:30 ET release falls inside this framework's "London" session window (02:00–09:30), not NY AM.** The extraordinary 541.2-point London range and −397.5 net move are capturing the CPI shock itself, not genuine European-hours trading — this is the single most violent session-level reading anywhere in this month's data, and it belongs to the release, not the session label. NY AM, arriving after the initial shock, still contributed a further −146.2 points, and NY PM added another −204.2 — this was a day where essentially every session after the release continued pressing in the same direction, with no genuine relief until NY Lunch's brief, minor +23.8 bounce.

**Wednesday, September 14 — State: Consolidation | +0.447%**
Open 12090.50, close 12144.50. Range 1.319%. NDOG +49.0. Did not sweep either prior-day extreme.

| Session | Range | Net |
|---|---|---|
| Asia | 67.8 | −24.2 |
| London | 136.2 | +65.0 |
| NY AM | 134.0 | +45.5 |
| NY Lunch | 73.2 | +1.8 |
| NY PM | 141.0 | +6.2 |

A genuine pause day immediately after the CPI shock — every session range comes in well below the prior day's, consistent with a market digesting rather than extending the prior day's move.

**Thursday, September 15 — State: Reversal | −0.908%**
Open 12053.50, close 11944.00. Range 2.400%. NDOG −91.0. Swept the prior day's low.

| Session | Range | Net |
|---|---|---|
| Asia | 61.5 | −24.5 |
| London | 125.0 | −80.0 |
| **NY AM** | **221.5** | **−116.8** |
| **NY Lunch** | **163.8** | **+121.5** |
| NY PM | 193.5 | −111.2 |

A genuinely two-sided day — NY AM presses hard lower (−116.8), NY Lunch fully reverses it (+121.5), and NY PM reverses again to close the day near its low. This was the final trading day before the September 16 expiration data gap and the long weekend into Week 4.

### Week 4 — FOMC Week

**Monday, September 19 — State: Retracement | +1.844%**
Open 11819.75, close 12037.75. Range 2.119%. NDOG −124.2 (the week's opening gap, discussed in Section 4). Swept the prior week's low (11866.50) as well as the prior day's low.

| Session | Range | Net |
|---|---|---|
| Asia | 94.5 | −63.0 |
| London | 74.8 | −37.2 |
| **NY AM** | **158.8** | **+126.2** |
| NY Lunch | 129.8 | −3.2 |
| **NY PM** | **168.8** | **+93.2** |

The week opens by sweeping the prior week's low within the first session, then reverses hard — NY AM and NY PM together contribute +219.4 points against a combined Asia/London deficit of −100.2.

**Tuesday, September 20 — State: Retracement | +0.269%**
Open 11916.50, close 11948.50. Range 1.636%. NDOG −121.2. Did not sweep either prior-day extreme.

| Session | Range | Net |
|---|---|---|
| Asia | 59.8 | +16.2 |
| London | 176.0 | −145.8 |
| NY AM | 79.0 | +41.2 |
| NY Lunch | 142.0 | −75.2 |
| NY PM | 141.2 | +68.2 |

The day immediately before FOMC — a genuinely choppy, directionless session (five sessions, net moves alternating sign every time), consistent with the broader framework's own finding that pre-FOMC sessions frequently compress before the event itself.

**Wednesday, September 21 — State: Expansion | FOMC DAY | −2.222%**
Open 11962.50, close 11696.75. Range 3.808% of price — the widest single-day range of the entire month. NDOG +14.0 (negligible). Swept both the prior day's high and low — a genuine two-way day before the FOMC-hour move took over.

| Session | Range | Net |
|---|---|---|
| Asia | 48.5 | −31.0 |
| London | 128.2 | +47.8 |
| NY AM | 61.8 | −5.5 |
| NY Lunch | 71.2 | +24.2 |
| **NY PM** | **455.5** | **−277.5** |

**This session table is the cleanest single illustration of Vizard's own core finding anywhere in this document.** Every session before NY PM is small and directionally inconclusive — Asia, London, NY AM, and NY Lunch combined produce a net move of only +35.5 points on a combined range of just 309.7. Then NY PM alone — capturing the 2:00 statement and 2:30 press conference — delivers a 455.5-point range and a −277.5 net move, dwarfing the entire rest of the session combined. This is Vizard's "quiet before, explosive during" signature reproduced almost exactly, on the single day in this dataset built specifically to test it.

**Thursday, September 22 — State: Consolidation | −0.627%**
Open 11642.00, close 11569.00. Range 1.505% — a genuine post-FOMC compression. NDOG −54.8. Swept the prior day's low.

| Session | Range | Net |
|---|---|---|
| Asia | 128.2 | −36.0 |
| London | 199.0 | +16.8 |
| NY AM | 146.8 | −98.0 |
| NY Lunch | 99.8 | +23.5 |
| NY PM | 163.8 | +8.0 |

**Friday, September 23 — State: Retracement | −0.742%**
Open 11461.00, close 11376.00. Range 2.112%. NDOG −108.0. Swept the prior day's low.

| Session | Range | Net |
|---|---|---|
| Asia | 100.2 | −48.5 |
| London | 178.8 | −74.5 |
| NY AM | 132.8 | −82.5 |
| NY Lunch | 129.2 | −59.2 |
| **NY PM** | **164.5** | **+55.5** |

Four consecutive negative sessions before a partial NY PM recovery — this is the week's least contested day, grinding steadily lower with only a late partial bounce.

### Week 5

**Monday, September 26 — State: Retracement | −0.374%**
Open 11352.00, close 11309.50. Range 2.176%. NDOG −24.0. Swept the prior day's high.

| Session | Range | Net |
|---|---|---|
| Asia | 133.2 | −90.5 |
| London | 165.2 | +80.0 |
| **NY AM** | **195.2** | **+106.5** |
| **NY Lunch** | **172.2** | **−134.8** |
| NY PM | 116.2 | −8.2 |

**Tuesday, September 27 — State: Retracement | −1.090%**
Open 11470.50, close 11345.50. Range 2.918%. NDOG +161.0 — the largest gap of the month's final week. Swept both the prior day's high and low.

| Session | Range | Net |
|---|---|---|
| Asia | 124.2 | +103.2 |
| London | 112.2 | +52.0 |
| NY AM | 163.0 | +17.0 |
| **NY Lunch** | **265.5** | **−211.5** |
| NY PM | 121.8 | +71.5 |

A strong overnight/early session (+172.2 through NY AM) gets almost entirely erased by a single, violent NY Lunch reversal (−211.5) — one of the largest single-session reversals of magnitude anywhere in the month outside of the three scheduled-event days.

**Wednesday, September 28 — State: Expansion | +2.003%**
Open 11331.00, close 11558.00. Range 3.067% — the month's third-widest day, and notably not tied to any scheduled release. NDOG −14.5. Swept the prior day's high.

| Session | Range | Net |
|---|---|---|
| Asia | 208.5 | −101.5 |
| London | 214.0 | +70.8 |
| NY AM | 166.5 | +66.5 |
| NY Lunch | 135.5 | +99.5 |
| NY PM | 154.0 | +58.0 |

A genuinely broad-based, multi-session bullish day with no single dominant window — every session from London onward contributes positively, a distinct shape from the single-session-dominated scheduled-event days elsewhere in this document.

**Thursday, September 29 — State: Reversal | −1.401%**
Open 11387.00, close 11227.50. Range 2.729%. NDOG −171.0. Swept the prior day's low — and, per Section 4, this was also the day that finally took out Week 4's prior-week low.

| Session | Range | Net |
|---|---|---|
| Asia | 84.0 | −42.5 |
| London | 170.2 | −115.8 |
| **NY AM** | **243.2** | **−171.0** |
| NY Lunch | 111.5 | −45.0 |
| NY PM | 162.5 | +61.2 |

**Friday, September 30 — State: Retracement | −0.945% | Month-end, PCE inflation data**
Open 11186.50, close 11080.75 — the month's final close and its lowest RTH close. Range 2.977%. NDOG −41.0. Swept the prior day's low.

| Session | Range | Net |
|---|---|---|
| Asia | 94.2 | +6.2 |
| London | 186.5 | −39.5 |
| **NY AM** | **173.5** | **+113.2** |
| NY Lunch | 157.8 | −72.2 |
| **NY PM** | **211.0** | **−152.2** |

The month closes exactly as it spent most of its final three weeks — a brief morning recovery attempt (NY AM +113.2) fully reversed and extended by the afternoon (NY PM −152.2), closing the month at its session, weekly, and monthly low simultaneously.

---

## 6. Synthesis

September 2022, examined at this level of granularity, tells a story with unusual internal consistency for a single calendar month. Three of its four scheduled macro catalysts — NFP, CPI, and FOMC — independently produced the month's three largest single-day percentage moves, and all three were classified as "Expansion" days by a state classifier that has no awareness of the economic calendar whatsoever. The month's week-by-week arc is a clean relief-rally-into-capitulation shape: a mild pullback into NFP, a genuine +3.805% recovery week that pushed price to its monthly high the day before CPI, and then three consecutive negative weeks that never looked back, each one taking out the prior week's low without exception.

At the session level, the two clearest scheduled-event days in this month — CPI on the 13th and FOMC on the 21st — each show a specific, concentrated single-session signature consistent with this framework's own separately-built models: CPI's damage lands overwhelmingly in the session window containing its 8:30 release, and FOMC's NY PM session (455.5-point range against a combined 309.7 points for the other four sessions combined) reproduces Vizard's "quiet before, explosive during" finding almost exactly, on a single real trading day, independent of and prior to that model's own multi-year statistical construction. That a single month, examined in this much depth, so cleanly reproduces findings originally derived from a 43-event, multi-year sample is a meaningful piece of corroborating evidence for the broader framework — not proof on its own, but a genuine, independent data point in the same direction.

---
*Two trading days affecting this analysis carry documented limitations: September 5 (Labor Day) was excluded as a non-trading holiday; September 16 was expiration day for NQU22, which settles at the 9:30 open, so the continuous file holds no RTH session for it. Comparisons spanning 15 → 19 September cross a contract switch and are not like-for-like.*
