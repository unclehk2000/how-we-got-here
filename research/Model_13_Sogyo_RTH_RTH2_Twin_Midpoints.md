# MODEL 13 — "SŌGYO" (Sōgyo no Kotowari, the Twin Fish)
### RTH 0.5 and RTH2 0.5 gap midpoints · NQ 1,255 days (2018, 2022 – Aug 2026) · ES 854 days (2023 – Aug 2026)

---

## Why this name
Ukitake's twin blades take an attack in through one sword and send it back out through the other. That matches the idea being tested: two midpoints, one from each session close, working as a pair.

**The verdict up front.** Price treats the two midpoints as one level. The RTH2 midpoint adds nothing measurable to the RTH midpoint. Neither one draws price, holds price or turns price better than any other fraction of the gap. What the pair *is* good for is pricing targets, by gap size and by time of day (Section 6).

---

## 1. Definitions

| | Session | Close used |
|---|---|---|
| RTH | 09:30 – 16:14 ET (14:30 – 21:14 UK) | close of the 16:14 bar |
| RTH2 | 09:30 – 16:59 ET (14:30 – 21:59 UK) | close of the 16:59 bar (the 17:00 settlement close) |

> **CE1 (RTH 0.5) = (prior RTH close + today's 09:30 open) / 2**
> **CE2 (RTH2 0.5) = (prior RTH2 close + today's 09:30 open) / 2**
> CE2 − CE1 = ½ × the prior day's 16:14 → 16:59 settlement-window move

**Day selection.**
- Kept: days where the prior close and today's open are on the same contract.
- Dropped: early-close days and roll switches.

**Two kinds of day.**
- **Aligned:** both midpoints sit on the same side of the open. The *near* level is the one closer to the open, the *far* level the other.
- **Split:** the open lands between the two closes, so the midpoints sit on opposite sides.

---

## 2. Geometry: how far apart are the twins?

**Table 1.**

| | NQ | ES |
|---|---|---|
| Median \|RTH gap\| | 0.426% | 0.271% |
| Median \|settlement-window move\| (16:14 → 16:59) | 0.052% | 0.034% |
| 90th percentile settlement move | 0.207% | 0.122% |
| **Median distance CE1 ↔ CE2** | **0.026% ≈ 3.8 pts** | **0.017% ≈ 0.9 pts** |
| Aligned days | 95.8% | 94.6% |
| Split days | 4.2% (53) | 5.4% (46) |
| Near level = CE2 (settlement moved toward today's open) | 50.7% | 49.6% |

On a median day the two midpoints are **about 4 NQ points apart**. That is inside one 1-minute bar's range at the open. For them to behave as two separate tools, price would have to tell apart levels a few ticks apart.

---

## 3. Is the 0.5 special? Ladder test

**Method.** Levels were placed at fractions of each gap, measured from the open: 0.25, 0.375, 0.5, 0.625 and 0.75. For each level, after its first touch: does price move k% back toward the open before it moves k% beyond the level? The touch bar itself is excluded from the race.

**Table 2.** Hold rate, ±0.10%. Gaps of at least 0.04% only: NQ n ≈ 1,180, ES n ≈ 780.

| Gap | 0.25 | 0.375 | **0.5** | 0.625 | 0.75 |
|---|---|---|---|---|---|
| NQ, RTH gap | 53.6 | 53.3 | **53.7** | 52.0 | 48.4 |
| NQ, RTH2 gap | 53.9 | 53.3 | **52.3** | 53.2 | 50.2 |
| ES, RTH gap | 49.5 | 52.0 | **53.6** | 53.0 | 53.0 |
| ES, RTH2 gap | 49.9 | 50.1 | **51.8** | 51.5 | 51.7 |
| NQ touch rate (RTH gap) | 81.6 | 77.0 | **73.0** | 69.0 | 63.9 |

- **Hold rates:** at the 0.5 they sit within ±2 points of the neighbouring fractions. With about 860 touches, one standard error is 1.7 points.
- **Touch rate:** it falls smoothly with distance from the open, with no step at 0.5.
- **At ±0.05% and ±0.20%:** the same picture. The best 0.5 reading is NQ RTH ±0.05% at 55.2% vs 52–53% for its neighbours, which is not significant.

**Mirror placebo.**
- **Method:** the same distance from the open, but on the side *away* from the prior close.

| | Midpoint touch rate | Mirror placebo |
|---|---|---|
| NQ | CE1 77.6%, CE2 76.6% | 75.4% / 75.8% |
| ES | 78.4% / 78.7% | 72.1% / 72.2% |

- **NQ:** the midpoints are no more likely to be touched than a level the same distance on the other side.
- **ES:** there is a mild pull toward the prior close, about 6 points.

---

## 4. Do the two work better together?

**Table 3.** Aligned days.

| | NQ | ES |
|---|---|---|
| Near level touched in RTH | 79.0% | 80.7% |
| Far touched, given near touched | 96.0% | 96.6% |
| Full RTH gap fill | 60.7% | 62.5% |

**Wide-zone days** (top quartile of separation: NQ ≥ 0.050%, ES ≥ 0.032%). This is where "two levels" could matter.

| Hold ±0.10% after first touch | RTH 0.375 | CE1 | CE2 | RTH 0.625 |
|---|---|---|---|---|
| NQ, wide days (n 213–236) | 52.3 | 56.8 | 52.2 | 53.5 |
| ES, wide days (n 136–155) | 56.5 | 55.6 | 55.2 | 52.2 |
| NQ, near vs far level of the pair | near 55.9 / far 53.1 | | | |

Even when the settlement window has pushed the twins apart, neither level stands out from the placebo fractions on the same days. The far level does not hold better than the near one either. One SE is about 3.3 points at these n.

**Settlement-window direction:**

| | Settlement moved toward today's open | Away |
|---|---|---|
| NQ full RTH fill | 60.2% | 61.3% |
| NQ RTH closes beyond the open in gap direction | 50.5% | 49.2% |
| ES full RTH fill | 60.3% | 64.6% |

No usable difference.

**The 10:00 test.** Has the zone been touched by 10:00?

| | NQ: touched 09:30–09:59 | NQ: not touched | ES: touched | ES: not touched |
|---|---|---|---|---|
| n | 711 | 491 | 430 | 378 |
| RTH closes beyond the open in gap direction | 39.8% | 64.4% | 42.1% | 54.5% |
| **10:00 → 16:14 return, signed in gap direction** | −0.082% | +0.036% | −0.019% | −0.078% |

- **The close-direction split looks strong, but it is mechanical.** A day that has already retraced half its gap by 10:00 has further to go to close beyond the open.
- **The tradable part is the 10:00 → close return.** It is small, flips sign between NQ and ES, and never exceeds the 0.02–0.03% drift of simply being long.

**Split days** (open between the two closes; NQ 53, ES 46):

| | NQ | ES |
|---|---|---|
| CE1 touched | 45.3% | 34.8% |
| CE2 touched | 47.2% | 23.9% |
| Both touched | 22.6% | 8.7% |

When the twins straddle the open, price usually takes one side and leaves the other. The samples are too small to say which.

---

## 5. Mechanical trades

**Setup for both rules.** Aligned days, gap ≥ 0.10%, levels taken from the pair. Returns are in % of the open, before costs. Each rule was also run with the same logic at the 0.375 and 0.625 pairs, and with CE1 alone.

**Rule A — fade the far level.**
- Entry: limit at the far level, positioned for a hold.
- Target: the open.
- Stop: 0.25 × the gap beyond the far level.

**Rule B — break the far level.**
- Entry: the first 1-minute close beyond the far level, going with the fill.
- Target: the prior RTH close.
- Stop: back at the near level.

**Table 4.**

| | NQ A: n · win · mean · t | NQ B: n · win · mean · t | ES A | ES B |
|---|---|---|---|---|
| **CE1 + CE2 pair (the model)** | 793 · 33.9% · −0.009% · −0.97 | 698 · 27.5% · −0.004% · −0.79 | 506 · 31.4% · −0.006% · −0.71 | 459 · 29.2% · +0.005% · +1.07 |
| CE1 alone | 793 · 33.7% · −0.009% · −1.01 | 698 · 27.5% · −0.004% · −0.79 | 506 · 31.2% · −0.006% · −0.76 | 459 · 29.2% · +0.005% · +1.07 |
| 0.375 pair (placebo) | 853 · 41.5% · −0.001% · −0.12 | 768 · 22.9% · +0.002% · +0.33 | 542 · 39.7% · −0.007% · −1.10 | 514 · 23.0% · +0.006% · +1.20 |
| 0.625 pair (placebo) | 741 · 28.2% · −0.009% · −0.85 | 610 · 35.7% · +0.002% · +0.27 | 463 · 25.3% · −0.015% · −1.77 | 406 · 36.2% · +0.001% · +0.22 |

**Reading.**
- **Adding RTH2 changes nothing.** The pair and CE1 alone are identical to three decimal places.
- **No version is distinguishable from zero** (\|t\| ≤ 1.2).
- **Placebo fractions do as well or better.**
- **Costs:** after about 0.01% round trip, every version loses.

---

## 6. What the twins are good for: a target map

Treat CE1 and CE2 as one zone, a few points wide. Its value is as a **target with a known probability**, by gap size and time of day. Use it to set or judge take-profits for setups from other models (Kekkai Barrier, Byakugan, Cero).

**Table 5.** Probability the zone has been touched by each time. Aligned days; the near level marks entry into the zone.

| By | 09:35 | 09:45 | 10:00 | 10:30 | 11:00 | 12:00 | 16:14 |
|---|---|---|---|---|---|---|---|
| NQ near level | 38% | 52% | 59% | 66% | 70% | 74% | **79%** |
| NQ far level | 30% | 44% | 52% | 61% | 65% | 69% | 76% |
| NQ full RTH fill | 16% | 25% | 33% | 41% | 45% | 51% | 61% |
| ES near level | 31% | 44% | 53% | 66% | 70% | 74% | **81%** |
| ES full RTH fill | 12% | 22% | 28% | 39% | 46% | 52% | 62% |

**Table 6.** By gap size (NQ, |RTH gap| quintiles).

| \|Gap\| | ≤ 0.17% | 0.17 – 0.34% | 0.34 – 0.56% | 0.56 – 0.94% | > 0.94% |
|---|---|---|---|---|---|
| Zone touched in RTH | 92.5% | 91.2% | 80.8% | 71.2% | 59.3% |
| Full RTH fill | 85.9% | 76.7% | 59.2% | 50.4% | 31.5% |
| Median minute of zone touch | 0 | 2 | 7 | 14 | 45 |

**Conditional decay:**

| | Touched later in RTH: NQ | ES |
|---|---|---|
| Not touched by 10:00 | 48.7% (CI 44–53) | 58.7% |
| Not touched by 11:00 | 30.8% (CI 26–36) | 35.3% |

**Stability:** NQ zone touch rate by year was 80.0, 79.5, 80.5, 80.4 and 79.4% for 2018 and 2022–2025, and 70.4% for 2026 (partial year).

---

## 7. The zone as a barrier, across the four delivery states

**The test.** Z is the middle of the twin zone, halfway between today's open and the midpoint of the two prior closes. So once price touches Z, the open (trading *away*, i.e. the barrier is respected) and the full gap fill (trading *through*) are the same distance away.
- **Null:** a driftless market goes either way 50% of the time.
- **Scoring:** the race starts on the bar after the first touch. 96% of races resolve by 16:14; the rest are scored by which side of Z the RTH close sits on.
- **Placebos:** the same symmetric race at the 0.375 and 0.625 fractions on the same days.
- **Sample:** aligned days with a gap of at least 0.10% (NQ 1,086 days, 824 touched; ES 683 days, 518 touched).

**The four states** are classified on RTH range vs its trailing 20-day average:

| State | Rule |
|---|---|
| Expansion | range > 125% of average and \|net\| > 55% of range |
| Consolidation | range < 75% of average |
| Reversal | close opposite to the prior day and range ≥ average |
| Retracement | everything else |

Frequencies here: NQ 38.7 / 31.9 / 14.8 / 14.6% (Retracement / Consolidation / Expansion / Reversal), close to the original 41.7 / 29.7 / 13.5 / 15.0%.

**Table 7.** Barrier respected: price trades away to the open before the full fill. "Placebo" columns are the same race at the 0.375 / 0.625 fractions.

| State | NQ n | NQ away % (95% CI) | NQ placebo .375 / .625 | ES n | ES away % (95% CI) | ES placebo .375 / .625 |
|---|---|---|---|---|---|---|
| **Same day (known only after the close)** | | | | | | |
| Expansion | 98 | **34.7** (26–45), p 0.003 | 44.7 / 29.2 | 70 | **32.9** (23–44), p 0.006 | 41.4 / 30.9 |
| Retracement | 292 | 53.3 (48–59) | 52.4 / 52.8 | 190 | 41.6 (35–49) | 44.4 / 46.4 |
| Reversal | 116 | 48.3 (39–57) | 47.6 / 38.0 | 81 | 50.6 (40–61) | 50.0 / 48.0 |
| Consolidation | 226 | **60.6** (54–67), p 0.002 | 59.1 / 60.7 | 159 | 55.3 (48–63) | 58.0 / 53.1 |
| **Prior day (known before the open)** | | | | | | |
| Expansion | 98 | 52.0 (42–62) | 54.9 / 44.8 | 63 | 46.0 (34–58) | 43.3 / 42.4 |
| Retracement | 274 | 51.3 (45–57) | 54.5 / 50.6 | 190 | 46.3 (39–53) | 49.0 / 43.4 |
| Reversal | 106 | 53.8 (44–63) | 53.1 / 45.0 | 67 | 43.3 (32–55) | 54.8 / 55.4 |
| Consolidation | 219 | 51.4 (45–58) | 48.5 / 50.0 | 158 | 46.8 (39–55) | 47.0 / 47.3 |
| **All days** | 824 | 52.0 (49–55) | 52.7 / 49.4 | 518 | 46.1 (42–50) | 49.2 / 46.9 |

**Reading.**
1. **Consolidation days are where the barrier holds.** NQ 60.6% is significant even after correcting for 16 tests; ES 55.3% is not. But the placebo levels hold just as often on the same days (59–61% NQ, 53–58% ES). On a range-bound day *any* level halfway to the gap fill is respected, because reaching the fill means extending the day's range and reaching the open does not. The rate also swings by year: 67, 51, 77, 50, 57 and 79% for 2018 and 2022–26.
2. **Expansion days are where it fails.** The zone is traded through about two-thirds of the time (34.7% / 32.9% respected). The 0.625 placebo fails just as badly.
3. **Retracement and Reversal days sit at the coin flip** in NQ. ES Retracement leans toward *through* (41.6%).
4. **What you can actually know at the open — yesterday's state — changes nothing.** Every row is 43–54%, inside its interval of 50% and level with the placebos. This holds even though Consolidation follows Consolidation 44% of the time, because that persistence is too weak to carry the effect.

**Real-time proxy, known at 10:30.** The first-hour range (09:30–10:29) vs its 20-day average, scoring only zone touches at or after 10:30:

| First-hour range | NQ: days that become Consolidation | NQ away % (n) | NQ placebo .375 / .625 | ES away % (n) |
|---|---|---|---|---|
| Narrow (bottom third) | 59% | 57.1 (63) | 52.1 / 57.0 | 53.1 (49) |
| Normal | 31% | 58.5 (41) | 48.1 / 48.0 | 52.6 (38) |
| Wide (top third) | 6% | 58.3 (36) | 45.7 / 48.8 | 56.7 (30) |

- **What the proxy tells you:** a narrow first hour is a usable early read that the day will be a Consolidation day (59% vs a 32% base).
- **The barrier rate doesn't follow it.** It is about the same in all three tiers.
- **One lead is worth noting.** Late touches (after 10:30) are respected 57.9% of the time in NQ (n 140, p 0.08) against about 50% for the placebos. That falls short of significance and is weaker in ES (54%, n 117). Treat it as a hypothesis, not a rule.

**Barrier verdict:** the zone acts as a barrier only on days that turn out to be Consolidation days, and so does every other level, so it is the day type doing the work. Nothing known before or early in the session lifts adherence above the coin flip by a usable margin.

---

## 8. Checklist

1. **Pre-open.** Mark the prior 16:14 close (C1) and 16:59 close (C2). At 09:30, compute CE1 = (C1 + O)/2 and CE2 = (C2 + O)/2.
2. **Draw one zone** between CE1 and CE2. Expect it to be a few points wide; it is one level, not two.
3. **Check for a split day.** If the open sits between C1 and C2, it is a split day (about 5%). Expect only one side to be visited; don't target both.
4. **Read the gap size off Table 6.** Below 0.34% the zone is a near-certain early visit (91–93%, median within 2 minutes). Above 0.94% it is closer to a coin flip (59%), with a median wait of 45 minutes.
5. **Use the zone as a take-profit or a scale-out level** for a setup from another model. Never use it as an entry trigger on its own: Table 4 shows fades and breaks there lose to costs.
6. **Re-price at 10:00.** If the zone is untouched, cut its probability to about 49% (NQ). At 11:00, cut it to about 31%. Move targets in rather than hoping.
7. **Full gap fill (C1) is a separate, lower-probability target:** 61% on the day, 33% by 10:00 for NQ. Size any runner to that.
8. **Ignore the settlement-window direction** (whether C2 moved toward or away from the open). It changes nothing measurable.
9. **Don't treat the zone as a barrier to fade.** It is respected about 52% of the time in NQ and 46% in ES, whatever yesterday's delivery state. If the session is visibly ranging (narrow first hour, Consolidation behaviour), expect it to hold about 60% of the time, but expect the same of any level in that range. On an expansion-type day, expect it to break (about 65%).

---

## 9. Bottom line

**Is the RTH2 midpoint a second tool?** No. It sits a median 3.8 NQ points from the RTH midpoint, and every test (touch, hold, break, wide-zone days, settlement direction) gives the same result with or without it.

**Is the gap midpoint itself a reaction level?** No more than the 0.375 or 0.625. Hold rates are about 53% at all of them.

**Is it a barrier price trades away from?** Only on Consolidation days (NQ 60.6%), and placebo levels match that. Yesterday's delivery state gives no edge (43–54%).

**What it is good for:** a time- and gap-size-priced **target**. On that use it is stable across every year tested.

**Probability that a separate RTH2-midpoint effect would show up with more data:** about 5%. With 1,255 NQ days, a 5-point difference in hold rate would have been about two standard errors. The observed difference was under 2 points, and it never pointed the same way in NQ and ES.

---
*Statistics: Wilson 95% intervals for rates; trade t-statistics are mean / (s.d. / √n). Scripts: `Sogyo/` — `bars.py` (1-min loader), `twin.py` (levels), `stats2.py` (ladder test), `cond.py` (conditional tables), `bt.py` (trades), `barrier.py` + `barrier_tab.py` (barrier by delivery state), `early.py` (10:30 proxy).*
