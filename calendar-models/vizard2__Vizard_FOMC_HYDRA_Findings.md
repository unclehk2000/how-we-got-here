# Vizard × HYDRA: what the FOMC data supports adding to the stages card

NQ and ES front-month futures, 1-minute bars in ET, Jan 2018 – Oct 2026 (ES to Aug 2026). That gives 67 FOMC decision days per symbol.
- **Train:** 2018–24 (54 days).
- **Locked test:** 2025–26 (13 days).
- **Features:** everything knowable at 13:59, 29 base features. They cover position in the month, the week and the prior day; distance from the month and week opens; the move and range since 18:00, overnight, NY AM and lunch; the RTH gap; 5- and 20-day trend; ADR; distance to the ATH; VIX; and SEP meeting.
- **ADR20:** mean high − low of the 20 prior trading days, in points.
- **Stages:** stage 1 = 14:00 open → 14:29 close (statement); stage 2 = 14:30 open → 16:14 close (press conference to the RTH close).

**Rule for a ✓:** p < 0.05 over 2018–26, and the same side in 2018–24 and 2025–26.

## A. HYDRA fishing (NQ, 2018–24)

There were 411 heads: 29 base features plus random products, differences, maxima and thresholds. Each was tested against 13 targets with HC3 standard errors and at least 8 days on each side. The cut was Benjamini–Hochberg at 10%. The null is the same search on circularly shifted targets (20 shifts).

| Target | Survivors | Shifted null, mean (max) |
|---|---|---|
| Stage 1 up | 8 | 1.3 (7) |
| Stage 2 up | 0 | 2.5 (22) |
| 14:00 → 16:14 up | 0 | 2.0 (22) |
| Stage 2 continues stage 1 | 1 | 4.8 (51) |
| Next NY AM up | 0 | 4.0 (16) |
| New day high after 14:00 | 2 | 2.9 (7) |
| **New day low after 14:00** | **56** | 5.0 (32) |
| **\|Stage 1\| (ADR)** | **13** | 0.9 (4) |
| \|Stage 2\| (ADR) | 1 | 0.8 (10) |
| **Range after 14:00 (ADR)** | **12** | 1.1 (7) |

Not shown: next NY AM with stage 2 (0 survivors), next NY AM with 14:00 → 16:14 (3, null mean 4.2), extension up after 14:00 (0).

- **Direction:** survivors sit at the level of the shifted nulls.
- **Size and risk:** survivors clear them: |stage 1|, the range after 14:00, and whether the day's low breaks after 14:00.

## B. Locked test (2025–26) and the whole net

- **Locked test:** the train survivors went into it, up to 40 per target (80 in all). None held in 2025–26 (same sign, one-sided p < 0.05) with the same sign on ES. **0 of 80.**
- **Whole net:** a ridge logistic on the 29 base features, fit on 2018–24, scored within the shuffled-label nulls on 2025–26:

| Target | AUC 2025–26 | Null 95th percentile |
|---|---|---|
| Stage 1 up | 0.28 | 0.83 |
| Stage 2 up | 0.38 | 0.76 |
| 14:00 → 16:14 up | 0.52 | 0.74 |
| Next NY AM up | 0.41 | 0.74 |
| New day high after 14:00 | 0.68 | 0.78 |

**Reading:** nothing at 13:59 calls the direction after 14:00. The size structure is real in training, but 13 test days are too few to confirm any single head. So the card shows sizes as descriptions, and gives a ✓ only to pre-specified groups that held in both periods.

## C. Pre-specified groups at 13:59

These are your two questions (the month's premium / discount and the distance from the month's open), plus the size heads HYDRA pointed at.
- Premium = top quarter of the month's range so far; discount = bottom quarter.
- Over / under = more than 1 ADR from the month's open.

**By month position: median |stage 1|, |stage 2| and range after 14:00 (ADR), and how often a new day low came after 14:00**

| | n | \|S1\| | \|S2\| | Range after 14:00 | New low after 14:00 |
|---|---|---|---|---|---|
| NQ discount | 7 | 0.27 | 0.48 | 1.38 | 71% |
| NQ middle | 29 | 0.15 | 0.47 | 0.90 | 52% |
| NQ premium | 31 | 0.13 | 0.29 | 0.74 | 45% |
| ES discount | 7 | 0.32 | 0.52 | 1.48 | 100% |
| ES middle | 26 | 0.15 | 0.51 | 0.95 | 62% |
| ES premium | 34 | 0.15 | 0.29 | 0.77 | 56% |

A stretched month into the statement (discount) came with the biggest reactions, and a premium with the smallest.

**Results that held (✓): all on ES**

| ES setup at 13:59 | Result | Others | 2018–24 | 2025–26 | p |
|---|---|---|---|---|---|
| Month premium (n 34) | 16:14 close above the 14:00 price **65%** | 36% | 69% vs 36% | 40% vs 38% (barely) | 0.02 |
| Month discount (n 7) | new day low after 14:00 **100%** | 58% | 100% | 100% (2 days) | 0.03 |
| > 1 ADR over the month's open (n 33) | range after 14:00 **0.67** ADR | 1.12 | 0.69 vs 1.18 | 0.63 vs 0.74 | 0.001 |
| > 1 ADR over the month's open (n 33) | \|stage 2\| **0.25** ADR | 0.53 | 0.34 vs 0.59 | 0.18 vs 0.43 | 0.004 |
| > 1 ADR under the month's open (n 8) | next NY AM up **88%** | 43% | 80% | 3 of 3 | 0.02 |
| SEP meeting (n 33) | \|stage 1\| **0.29** ADR | 0.10 | 0.33 vs 0.09 | 0.14 vs 0.11 | < 0.001 |

**NQ: nothing held.** The closest results all failed the 2025–26 half:
- SEP |stage 1|: 0.29 vs 0.08 (p < 0.001), but 0.06 in 2025–26.
- Above PDH, new day low after 14:00: 28% vs 59% (p 0.02).
- Up more than 0.4 ADR since 18:00, new day low after 14:00: 22% vs 61% (p 0.005).
- Premium, range after 14:00: 0.74 vs 0.99 (p 0.08).

**New day high (H) and low (L) after 14:00 by the other locators (descriptive, no ✓)**

| | NQ H / L | ES H / L |
|---|---|---|
| Above PDH | 83% / 28% (n 18) | 93% / 29% (n 14) |
| Inside the prior day | 56% / 61% (n 41) | 60% / 74% (n 47) |
| Below PDL | 75% / 50% (n 8) | 50% / 50% (n 6) |
| Up > 0.4 ADR since 18:00 | 78% / 22% (n 18) | 83% / 25% (n 12) |
| Within ± 0.4 | 63% / 63% (n 46) | 65% / 69% (n 49) |
| Down > 0.4 ADR | 33% / 33% (n 3) | 33% / 83% (n 6) |

**Caution on multiple testing:** about 300 tests went into sections C and D. At p < 0.05 with both halves on the same side, 5–8 passes would be expected by chance. Treat the ✓ rows as the most stable descriptions, not as proven edges. The two with the most days behind them are SEP |stage 1| and over-the-month's-open |stage 2| and range.

## D. Deep DXY

DXY futures, 5-minute, Feb 2023 – Jul 2026: NQ 28 and ES 29 FOMC days. Moves are in DXY's own ADR20.

**The index moved the other way to DXY in the same window**

| | All | DXY move big | DXY move small |
|---|---|---|---|
| NQ stage 1 (big ≥ 0.25 ADR) | 71% (n 28) | **86%** (n 14; 2023–24 90%, 2025–26 75%; p 0.013) ✓ | 57% (n 14) |
| ES stage 1 | 83% (n 29) | **100%** (n 15; 100% / 100%; p < 0.001) ✓ | 64% (n 14) |
| NQ stage 2 (big ≥ 0.5 ADR) | 79% (n 28) | **85%** (n 13; 100% / 67%; p 0.02) ✓ | 73% (n 15) |
| ES stage 2 | 83% (n 29) | **93%** (n 14; 100% / 86%; p 0.002) ✓ | 73% (n 15) |

- **Size:** when DXY's stage-1 move was big, the index's |stage 1| was 0.25–0.26 ADR, against 0.06 when it was small.
- **Typical DXY move:** |stage 1| median 0.25–0.26 and |stage 2| 0.49–0.50 of its ADR20. That is why the thresholds sit at 0.25 and 0.5.

**What did not hold:**
- **No lead inside the stage:** DXY's first 10 minutes against the rest of stage 1 went the other way 69% on ES (p 0.06) and 64% on NQ.
- **No lead across stages:** DXY's stage 1 says nothing about the index's stage 2.
- **4-week DXY trend:** with DXY up over 4 weeks (n 11), stage 2 closed up 27% vs 65% (NQ) and 27% vs 61% (ES). It was consistent in both halves (29% and 25%), but not significant (p 0.05 / 0.08). It is shown without a ✓.

**Reading:** DXY confirms the stage; it does not call it. Once DXY has made a big move, the index going the same way is the rare case. The card colours that red.

## E. What went into the card

**SETUP** (live, then fixed at 13:59 on the FOMC day and kept through the day after):
- the month's range octant with a PREM / MID / DISC pill;
- the distance from the month's open in points and ADR, with an OVER / NEAR / UNDER pill;
- above PDH, inside the prior day or below PDL, with that group's new high / low odds after 14:00;
- the move since 18:00, with the same odds;
- DXY's 4 weeks, with the stage-2 up rate for that side.

**EXPECT** (at today's ADR20, median and 80th percentile):
- |stage 1|, split by SEP (✓ on ES);
- |stage 2| and the range after 14:00 for today's month position;
- the ✓ result for today's setup, when there is one (ES), or "none held".

**LIVE** (FOMC day):
- each stage in points with DXY's move in its ADR20 and the size against the EXPECT median;
- a ⇄ / ⇉ pill that turns BIG at 0.25 (stage 1) and 0.5 (stage 2);
- the big-DXY other-way row (✓);
- the morning-gap fill row (✓ 74% vs 61% NQ, 76% vs 60% ES).

**Day after:** moved to Hollow (Model 12), with the open-side quarter row (✓ NQ 28% vs 18%; ES 26% vs 18%, not held).

**Dropped:**
- the last-N arrow strips and 3-year averages (now the ADR-scaled sizes);
- the next-NY-AM continuation index (no information: index 82–103);
- the day-level DXY row (not held);
- the gap 50% row (not held; still in the gap-50% label tooltip on the chart).

## Files

`hydra_fomc/`:
- `build.py`: features and targets per FOMC day;
- `fish.py`: HYDRA, output in fish_NQ_v3.txt;
- `direct.py`: the pre-specified groups, output in direct.json;
- `dxy.py` and `dxy_lead.py`: the DXY study.
