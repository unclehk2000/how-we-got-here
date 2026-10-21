# MODEL 13B — "SŌGYO: NY AM"
### The CE1/CE2 twin zone as a wall in NY AM (09:30–10:59 ET) · NQ 1,077 days (2018, 2022 – Aug 2026) · ES 673 days (2023 – Aug 2026)

---

## 1. What is being tested

**The zone.**
- CE1 = (prior 16:14 close + 09:30 open) / 2.
- CE2 = (prior 16:59 close + 09:30 open) / 2.
- Z = the middle of the two.
- Only aligned days with a gap of at least 0.10% are used.

**The wall.**
- **Holds:** after the first NY AM touch of Z, price trades back to the 09:30 open before it reaches the full gap fill.
- **Breaks:** price reaches the full fill first.
- Z sits exactly halfway, so a driftless market gives **50%**.
- 87% of races resolve before 11:00. The rest are scored by which side of Z the 10:59 bar closes on.
- **Stricter version:** "5-min wall" = no 5-minute close beyond the far edge of the zone for the rest of NY AM.

**"Consolidating in the gap"** is read as price working between the open and the wall without closing through it.

**Placebos.** The same race at the 0.375 and 0.625 fractions of the gap on the same days. If a factor lifts those as much as the zone, it describes the day, not the zone.

**Foothold trade.**
- Entry: on the first NY AM touch of Z, in the gap direction. On a gap-up day that means a long off the zone below.
- Stop: the 0.75 level, i.e. 0.25 × gap beyond Z.
- Target: the 09:30 open, which is 2R.
- Exit: 10:59 if neither stop nor target is hit.
- Measured in R, before costs (about 0.04R round trip on NQ).

---

## 2. Factors tested (all known at 09:30)

| Group | Factor | Definition |
|---|---|---|
| Gap | Gap size | \|open − prior close\| in ATR(14 RTH ranges) |
| | Zone width | \|CE2 − CE1\| in ATR |
| | Settlement direction | whether the 16:14→16:59 move went toward today's open |
| True day open | Open vs TDO | 09:30 open minus the 00:00 open, signed in the gap direction, in ATR |
| | TDO between | TDO lies between the open and the zone |
| | Zone–TDO distance | \|Z − TDO\| in ATR |
| CBDR | CBDR size | prior-day 14:00–20:00 range, in ATR |
| | Zone in CBDR | Z inside the CBDR |
| | Zone position | depth of Z inside the CBDR, in CBDR units |
| Session sweeps | London swept Asia | London (02:00–04:59) took the Asia (20:00–23:59) high / low |
| | Overnight swept PDH / PDL | 18:00–09:29 took the prior RTH high / low |
| Ranges | Asia range, overnight range | in ATR |
| | 07:00–09:29 | range and direction (Byakugan window) |
| | Overnight midpoint | its distance to Z |
| | 08:30 | 08:30–08:34 range in ATR (news proxy) |
| NDOG / NWOG | NDOG | 16:59 close → 18:00 open: size, and Z distance to its CE |
| | NWOG | Friday 16:59 → Sunday 18:00: size, Z distance to its CE, still unfilled at 09:30 |
| Prior day | Zone / open in prior range | Z or the open inside the prior RTH range |
| | Prior-day direction | prior day closed in the gap direction |
| | Prior-day state | Expansion / Retracement / Reversal / Consolidation |
| Calendar | Day of week | |
| Intraday | Touch minute | minute of the first NY AM touch |

---

## 3. Base rates

| | NQ | ES |
|---|---|---|
| Zone touched in NY AM | 64.8% (median minute 6) | 63.4% (median minute 14) |
| **Wall holds** | **52.1%** (n 698) | **45.0%** (n 427) |
| 5-min wall (no 5-min close through) | 20.5% | 19.8% |
| Placebo 0.375 / 0.625 | 54.2 / 49.3% | 50.0 / 45.1% |

Unconditionally the zone is a coin flip in NQ and slightly *weaker* than a coin flip in ES. Four times in five, price closes a 5-minute bar through it.

---

## 4. Carry asymmetry: foothold vs ceiling

The hypothesis: in a carry-charge market the zone should work better as a **foothold** (zone below price on a gap-up, longs off it) than as a **ceiling against buyside** (zone above price on a gap-down).

**Table 1.**

| | NQ hold % (n) | NQ trade R (t) | ES hold % (n) | ES trade R (t) | NY AM long 09:30→10:59, same days (NQ / ES) |
|---|---|---|---|---|---|
| Gap up: zone below = foothold, long | 49.6 (365) | +0.086 (1.2) | 44.7 (237) | −0.117 (−1.4) | **−0.27% / −0.17%** |
| Gap down: zone above = ceiling, short | 54.8 (333) | +0.185 (2.4) | 45.3 (190) | +0.047 (0.5) | **+0.36% / +0.23%** |

**The data runs the other way in NQ and is flat in ES.**
- **Intraday gap mean reversion dominates the morning.** Gap-up mornings drift down (−0.27%) and gap-down mornings drift up (+0.36%).
- **The carry drift is too small to matter here.** About 0.07% a week, which is under 0.01% over one NY AM. That is more than 25 times smaller than the gap effect.
- **Where carry does show up:** over weeks and months, as a reason to stay long overall. It doesn't show up as a foothold bias at a mid-gap level inside 90 minutes.

---

## 5. Which factors matter?

**Single factors.** Each factor's top third was compared with its bottom third, for the zone and for the placebos. 31 factors means a Bonferroni bar of p < 0.0016.

**Table 2.** Strongest NQ factors (n = 698 touched days).

| Factor | Hold, low group | Hold, high group | p | Placebo shift | Zone-specific shift |
|---|---|---|---|---|---|
| Gap size (≤ 0.17 vs ≥ 0.35 ATR) | 55.6% | 43.3% | 0.008 | −12.6 | +0.3 |
| Overnight range (≤ 0.50 vs ≥ 0.72 ATR) | 57.3% | 45.7% | 0.012 | −10.1 | −1.5 |
| Zone depth inside CBDR (low vs high) | 50.0% | 60.5% | 0.022 | +11.9 | −1.4 |
| Overnight trend in gap direction | 54.1% | 44.2% | 0.033 | −8.8 | −1.0 |
| Zone far from NDOG CE | 55.4% | 45.9% | 0.042 | −7.0 | −2.5 |
| London swept Asia high | 56.7% | 48.9% | 0.042 | −3.6 | −4.2 |

**Reading Table 2.**
- **No factor clears Bonferroni** in either market.
- **The NQ factors describe the day, not the zone.** The placebo levels move just as much, so the zone-specific shift is about 0 for every leading factor.
- **The ES leaders are different factors altogether.** In order: prior day closed in the gap direction (p 0.015), NWOG size, NWOG unfilled.
- **What doesn't matter:** TDO position, CBDR size, PDH/PDL sweeps, the 08:30 news range, 07:00–09:29 direction, day of week and settlement direction. All have p ≥ 0.08 in NQ, most above 0.3.

**Machine learning.** Gradient boosting and an L1 logistic model were refitted each year on all earlier years. Out-of-sample years: NQ 2023–26, ES 2025–26.

| | NQ AUC | NQ hold, top vs bottom third | ES AUC |
|---|---|---|---|
| Gradient boosting, zone | 0.555 | 56.7% vs 48.7% (base 51.7%) | 0.482 |
| L1 logistic, zone | 0.490 | 49.3% vs 49.3% | 0.502 |
| Gradient boosting, placebo 0.375 / 0.625 | 0.509 / 0.509 | — | 0.476 / 0.450 |
| Model's top-third days: zone vs placebos on the same days | 56.7% vs 55.3 / 56.2% | | 46.5% vs 47.9 / 50.0% |

**The rule the machine learning finds, NQ.** A depth-2 decision tree on all touched days splits on two factors only:

| NQ condition | Wall holds | n | Placebos, same days | By year (2018, 22, 23, 24, 25, 26) |
|---|---|---|---|---|
| **Gap ≤ 0.68 ATR and overnight range ≤ 0.45 ATR ("quiet")** | **63.5%** | 178 | 57.0 / 58.9% | 68, 56, 60, 62, 69, 75 |
| Gap ≤ 0.68 ATR, overnight range > 0.45 ATR | 50.6% | 473 | 48.5 / 46.8% | 50, 52, 55, 56, 44, 44 |
| Gap > 0.68 ATR | **23.4%** | 47 | 14.9 / 36.1% | — |

- **Out of sample:** refitted each year, the tree's selected days held **56.1%** (n 164) vs 49.1% for the rest.
- **The zone's own premium on quiet days is about 5 points.** 63.5% vs about 58% for the placebos, which is under 1.5 standard errors.
- **In ES the same rule doesn't hold** (46.7%, n 92), and ES's own tree failed out of sample (40.4%).

---

## 6. The foothold trade

**Table 3.** Mean R (t) by entry fraction, same stop and target logic (stop 0.25 gap beyond, target the open). Expected R is zero at every level under no drift.

| Entry level | NQ all | NQ 2018 / 2022 | NQ 2023–24 | NQ 2025–26 | ES all |
|---|---|---|---|---|---|
| 0.25 | +0.007 (0.2) | +0.062 | −0.013 | −0.037 | +0.010 |
| 0.375 | +0.124 (2.9) | +0.133 | +0.182 | +0.038 | +0.040 |
| **0.5 (Sōgyo zone)** | **+0.133 (2.5)** | +0.088 | **+0.306** | **−0.039** | **−0.044** |
| 0.625 | −0.030 | −0.080 | +0.079 | −0.108 | −0.087 |
| 0.75 | −0.051 | −0.041 | −0.062 | −0.052 | −0.127 |

**Reading Table 3.**
- **The positive NQ figure is not specific to the zone.** The 0.375 level earns the same.
- **It comes almost entirely from 2023–24** (+0.31R at the zone). It is negative in 2025–26.
- **It doesn't carry over to ES** (−0.04R).
- **After costs of about 0.04R,** the zone trade nets about +0.09R in NQ on a pooled t of 2.5, picked from 10 level/market cells. That is the profile of a period effect, not a structural one.

---

## 7. Sōgyo NY AM parameter card (confluence, NQ only)

| Parameter | Value | What to expect |
|---|---|---|
| Instrument | **NQ** | ES shows no zone effect in any configuration |
| Window | 09:30–10:59 | 65% of days touch the zone, median by 09:36 |
| **Green context** | gap ≤ 0.68 ATR **and** overnight (18:00–09:29) range ≤ 0.45 ATR | wall holds ~**56% out of sample** (63.5% in-sample), every year 56–75% |
| Neutral context | gap ≤ 0.68 ATR, overnight range > 0.45 ATR | coin flip (about 51%) |
| **Red context** | gap > 0.68 ATR | wall breaks about **3 times in 4** (holds 23%, n 47); treat the zone as a waypoint to the fill |
| Direction | Gap-down (zone above) holds slightly better than gap-up (zone below): 54.8% vs 49.6% | morning gap fade beats the carry drift intraday |
| Ignore | TDO, CBDR size, PDH/PDL sweeps, 08:30 range, NWOG/NDOG, prior-day state, day of week, settlement direction | none moved the zone beyond the placebos |

---

## 8. Checklist (NQ, pre-open to 11:00)

1. **Pre-open.** Mark the prior 16:14 and 16:59 closes and compute CE1, CE2 and Z at 09:30. Skip split days, where the open lies between the two closes.
2. **Measure the gap and the overnight range** (18:00–09:29), both in ATR (the average of the last 14 RTH ranges).
3. **Pick the context.**
   - Red (gap > 0.68 ATR): no wall; expect continuation through the zone toward the fill.
   - Green (gap ≤ 0.68 and overnight ≤ 0.45 ATR): the zone is a valid confluence for a reaction back toward the open.
   - Anything else is neutral: don't weight the zone.
4. **In green context only,** treat the first NY AM touch of the zone as a place where *another* model's entry (Kekkai Barrier, Bankai, Byakugan) gains confluence. Expect a return to the open before the full fill about 56–64% of the time.
5. **Stop placement if trading the reaction:** beyond the 0.75 level (0.25 gap past Z). Target the open. Exit by 10:59.
6. **Don't buy the zone on a gap-up just because NQ is a carry market.** Gap-up mornings drift down on average (−0.27% by 10:59).
7. **If the zone is untouched by 10:00, the chance it is reached at all later in the session falls to about 49%** (Model 13, Table 5), and lower within NY AM. Don't chase it.

---

## 9. The flipped wall (the 9 Oct 2026 example)

**The example.**
- RTH close 30,990.50 (16:14), RTH2 close 31,021.25 (16:59), 09:30 open 31,167.00.
- That gives **CE1 = 31,078.75** and **CE2 = 31,094.13**: a 15.4-point zone, top-quartile width.
- Price drove *through* the zone toward the fill (low ≈ 31,000 by 09:50). It then came back up twice (about 10:30 and 10:55–11:00), and each time the zone capped it and sent price back into the lower half of the gap.

That is a different behaviour from Sections 1–9, which test the *first* touch from the open side. Here the zone acts as a **flipped wall**: support turned resistance on a gap-up, or resistance turned support on a gap-down.

**Test** (09:30–11:59; it uses both NQ and ES):
- **Through:** price trades 0.125 × gap beyond the far edge of the zone, toward the fill. NQ 61%, ES 58% of aligned days; median minute 13 (NQ).
- **Retest:** the first later return to that far edge from the fill side. This happens on about 90% of through-days; median minute 19 (NQ).
- **Wall:** from the retest, price moves 0.25 × gap further toward the fill before it moves 0.25 × gap back toward the open. The race is symmetric around the retest point, so it is 50% under no edge.
- **Decoys:** zones of the *same width* centred on the 0.375 and 0.625 fractions, run through the identical procedure.

**Table 4.**

| | NQ wall % (n, CI) | NQ decoys .375 / .625 | ES wall % (n, CI) | ES decoys |
|---|---|---|---|---|
| All through-and-retest days | **52.9** (598, 49–57) | 48.5 / 48.3 | **53.8** (364, 49–59) | 48.2 / 50.9 |
| **Wide zone (top quartile)** | **56.6** (144, 48–64) | 49.7 / 44.5 | **54.7** (85, 44–65) | 45.4 / 50.6 |
| Narrow zone | 51.8 (454) | 48.1 / 49.6 | 53.6 (279) | 49.1 / 51.0 |
| Gap up: zone caps a rebound (vs buyside) | 51.9 (317) | 51.6 / 46.9 | 54.0 (210) | 49.2 / 44.3 |
| Gap down: zone as foothold after a rally | 54.1 (281) | 45.0 / 50.0 | 53.6 (154) | 46.9 / 60.1 |
| Gap > 0.68 ATR | 68.6 (35) | 72.7 / 60.0 | 68.2 (22) | 67.7 / 68.8 |
| Retest before 11:00 / 11:00–11:59 | 53.1 / 52.0 | — | 55.0 / 43.1 | — |

**Paired against the decoys on the same days:**

| | Days | Zone | Decoys | Difference | p |
|---|---|---|---|---|---|
| Pooled | 952 | 53.0% | 50.6% | **+2.4 pts** | 0.12 |
| NQ | 591 | | | +3.4 pts | 0.08 |
| ES | 361 | | | +0.8 pts | 0.75 |
| **Wide zone, pooled** | 226 | **55.3%** | 49.0% | **+6.3 pts** | **0.031** |

The wide-zone p is one of about 7 subgroups tested; Bonferroni needs p < 0.007.

**By year:**
- All NQ through-and-retest days: 54, 54, 52, 55, 46 and 60% (2018, 2022–26).
- NQ wide-zone days: 56, 61, 62, 59, 46 and 56%.

**Reading.**
- **This is the closest Sōgyo comes to a zone-specific effect.** Of everything tested, it is the only behaviour where the zone beats equal-width decoys in *both* markets and in most years.
- **It is strongest when the two midpoints are genuinely apart.** That is a wide settlement-window move, as in your example: about +6 points over the decoys.
- **It is small.** As a symmetric 1:1 trade off the retest it is worth about **+0.065R** before costs pooled, and about **+0.11R** on wide-zone days. NQ costs are about 0.03–0.04R at this stop size.
- **Carry asymmetry is not visible here either.** The zone as a foothold on a gap-down (NQ 54.1%) is within noise of the zone as a cap on a gap-up (51.9%).
- **Big-gap days** show high wall rates (68%), but the decoys match them. That is a day-type effect.

**Repeat retests.** Does a wall that has rejected once keep rejecting? Each race is conditional on the previous retest holding, 09:30–11:59.

| | 1st retest | 2nd | 3rd |
|---|---|---|---|
| NQ, zone | 53% (580) | 55% (226) | 54% (91) |
| NQ, zone, wide-zone days | 57% (142) | 52% (61) | 59% (28) |
| NQ, decoys .375 / .625 | 48 / 48% | 57 / 48% | 46 / 46% |
| ES, zone | 54% (352) | 60% (141) | 42% (69) |

**Each retest is roughly a fresh 53–57% event.** Earlier rejections don't make the next one more likely; a 9 Oct-style triple rejection happens on about 1 in 10 retest days. Treat the third touch with the same 1:1 odds as the first, not as a stronger wall.

**Flipped-wall parameter card (NQ):**

| Step | Rule |
|---|---|
| 1 | Zone width ≥ about 0.05% of price (about 15 pts at 30k). Otherwise CE1 ≈ CE2 and there is no wall to speak of. |
| 2 | Price trades through the zone toward the fill, at least 0.125 × gap past its far edge (typically by about 09:43). |
| 3 | Wait for the first return to the far edge from the fill side (typically by about 09:49; 90% of through-days get one). |
| 4 | Expect rejection back toward the fill about **55–57%** of the time. Stop 0.25 × gap back inside the zone toward the open; target 0.25 × gap toward the fill (1:1). Or use the retest as confluence for another model's entry. |
| 5 | Stop trading it after 11:59. ES retests after 11:00 fail more often than they hold (43%). |

---

## 10. Verdict

| Question | Answer |
|---|---|
| Is there a factor that gives CE1/CE2 a *zone-specific* edge? | No. Every factor that moves the hold rate moves the 0.375 / 0.625 placebos just as much. ML out-of-sample AUC is 0.49–0.56, and placebo AUCs are about the same. |
| When does the zone act as a wall in NY AM? | NQ, small gap with a quiet overnight: 63.5% in-sample, 56% out of sample. That is mostly the day type; about 5 points of it are the zone's own. |
| Does carry make it a foothold for longs? | No. Inside NY AM the gap fade dominates. Foothold longs: 49.6% hold, +0.09R. Ceiling shorts: 54.8%, +0.19R. |
| Does the zone act as a wall after price trades *through* it and comes back (your 9 Oct example)? | Slightly, and in both markets: 52.9% NQ, 53.8% ES vs about 49% for equal-width decoys. On wide-zone days it is 55.3% vs 49.0% (+6.3 pts, p 0.03 before multiple-test correction). This is the one zone-specific lead in the whole Sōgyo study. |
| Does the foothold trade make money? | NQ +0.13R gross (t 2.5), but only in 2023–24, no better than the 0.375 level, and negative in 2025–26 and in ES. |

**My numbers:**
- **About 15%** that the green-context NQ filter keeps a zone-specific premium of 5 points or more in future data.
- **About 10%** that the foothold trade is a durable edge after costs.
- **About 30%** that the wide-zone flipped wall holds a premium of 5 points or more over decoys in new data. It is the best candidate to track live.
- **Use:** confluence and context only, NQ only.

---
*Scripts (`Sogyo/`): `nyam_features.py` (features and outcomes), `scan.py` (factor scan), `ml_nyam.py` (walk-forward ML), `tree.py` (decision rules), `foothold.py` and `decoy_trades.py` (trades). Statistics: two-proportion z-tests, Bonferroni across 31 factors, walk-forward refits by calendar year, AUC out of sample.*
