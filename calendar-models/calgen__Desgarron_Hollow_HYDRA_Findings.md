# Desgarrón and Hollow × HYDRA: NFP day, NFP week and the day after FOMC

The data is NQ and ES front-month futures, 1-minute bars in ET, Jan 2018 – Oct 2026 (ES to Aug 2026). It uses the same protocol as the FOMC study behind Vizard:
- **Train:** 2018–24.
- **Locked test:** 2025–26.
- **Replication:** ES.
- **ADR20:** mean high − low of the 20 prior trading days.

**Rule for a ✓:** p < 0.05 over 2018–26, and the same side in 2018–24 and 2025–26.

| Event | Days (NQ) | Train / test | Snapshot | Model |
|---|---|---|---|---|
| NFP release day | 97 | 80 / 17 | 08:29 | Desgarrón (6, formerly Cero) |
| NFP week, Monday–Thursday | 320 | 257 / 63 | 09:29 | Hollow (11) |
| Day after FOMC | 65 | 53 / 12 | 09:29 | Hollow (12, Full Bringer) |

The NFP-week sample uses Vizard's day type 5, so it excludes days that are also CPI or FOMC days.

**Features:**
- **All three events:** position in the month's, the week's and the prior day's range; distance from the month and week opens; 5- and 20-day trend; ADR; distance to the ATH; VIX against its 20-day average.
- **NFP day:** Asia range, London move, the 07:00–08:29 dealing range, and the week into the release.
- **NFP week:** the overnight, the RTH gap, the NWOG, and days to NFP.
- **Day after FOMC:** the FOMC day's stage 1, stage 2, move after 14:00, range and close position.

## A. HYDRA fishing and the locked test (NQ)

Each event got 400 random heads on top of its base features. The cut was Benjamini–Hochberg at 10% per target, against 20 circularly shifted nulls. Survivors (up to 40 per target) went to 2025–26 and to ES. A whole-net ridge logistic was scored against 200 shuffled-label nulls.

**NFP day** (0 of the 12 direction targets survived in a way that held):

| Target | Survivors | Null mean (max) |
|---|---|---|
| Stage 1 up / stage 2 up / NY AM up / RTH up | 0 / 0 / 0 / 0 | 1.4 / 3.2 / 1.2 / 3.1 |
| New day high / low after 08:30 | 26 / 24 | 6.7 (60) / 8.6 (57) |
| \|NY AM\| | 102 | 0.4 (4) |
| Range after 08:30 | 119 | 0.3 (6) |
| Monday's range | 172 | 0.3 (3) |

- **Locked test:** 69 of 179 held with ES on the same side. All 69 are sizes or extremes: Monday's range 31, new high 17, range after 08:30 12, new low 9. None is a direction.
- **Whole net:** beat its null on NY AM up (AUC 0.80) and on new high after 08:30 (0.83). With 12 targets, one chance beat is expected; the new-high result is the distance effect below.

**NFP week Monday–Thursday:**
- **Direction:** NY AM up had 7 survivors against a null mean of 11.2; RTH up and the settlement window had 0.
- **Locked test:** 222 of 399 held. They cover the RTH range, the gap's 50% by 10:00 and in NY AM, the next day's range, new highs and lows, the full gap fill, the open-side quarter, the settlement range and |NY AM|.
- **Whole net:** beat its null on every gap and extreme target (AUC 0.73–0.82) and on none of the direction targets (0.41–0.61).

**Day after FOMC:**
- **Locked test:** 36 of 205 held: RTH takes the FOMC high 17, new high after 09:30 7, gap filled 6, gap 50% in NY AM 4, FOMC low 2.
- **Direction:** no NY AM, RTH or continuation head held.

**Reading:**
- **No direction:** on none of the three days does anything known at the snapshot call the direction.
- **What repeats:**
  - how big the day gets (range after the release, NY AM, the next day);
  - which extreme gets taken;
  - how the RTH gap behaves.
- **Much of the extreme and gap structure is distance:**
  - a price already near its overnight high is likelier to make a new high;
  - a small gap fills more often than a big one.
  These effects are real and repeat out of sample, but they are not peculiar to the event. The cards show them as odds for the group today falls in, not as event signals.

## B. Pre-specified groups (what the cards show)

The cards group each day by the setup at the snapshot:
- the month's discount / middle / premium (bottom / middle / top quarter);
- over / within / under 1 ADR from the month's open;
- above PDH / inside / below PDL (the FOMC day's range on the day after);
- a strong move into the snapshot (beyond ±0.4 ADR);
- VIX beyond ±10% of its 20-day average;
- the week into the release (NFP only, ±0.5 ADR);
- the RTH gap beyond ±0.25 ADR (Hollow).

A ✓ compares the group with the rest of that event's days.

**NFP day, NQ** (range after 08:30 in ADR; new high / low after 08:30):

| Setup at 08:29 | n | Range after 08:30 | New high / low |
|---|---|---|---|
| Discount | 23 | **1.18 ✓** | 57% / **91% ✓** |
| Middle | 34 | 1.06 | 74% / 59% |
| Premium | 40 | **0.84 ✓** | 72% / 62% |
| Under the month's open > 1 ADR | 20 | **1.21 ✓** | 70% / 80% |
| Below PDL | 13 | **1.18 ✓** | **23% ✓** / **92% ✓** |
| Down > 0.4 ADR since 18:00 | 9 | 1.03 | **11% ✓** / 89% |
| Week up > 0.5 ADR into NFP | 39 | **0.81 ✓** | 69% / 64% |
| Week down > 0.5 ADR | 30 | **1.31 ✓** | 67% / 70% |
| VIX > 10% over its average | 28 | **1.23 ✓** | 75% / 75% |
| VIX > 10% under | 21 | **0.69 ✓** | 67% / 71% |

ES matches the range rows (discount 1.36, premium 0.87, week down 1.45, VIX over 1.46, all ✓). It also adds:
- premium days made a new low after 08:30 only 49% vs 73% (✓);
- over the month's open by more than 1 ADR, the first side of the 07:00 range taken after 08:30 won 80% vs 49% (✓).

The disruption story in Model 6 shows up as size: a strong week into NFP meant a smaller reaction, a weak week a bigger one. The day going against the week did not hold (47% overall).

**NFP week Monday–Thursday, NQ:**
- **Gap:**
  - its 50% traded by 10:00 on 84% of days with a small gap vs 38% after a gap up > 0.25 ADR and 43% after a gap down (✓ all three);
  - the whole gap filled by 16:14 on 80% / 40% / 49%.
- **Tuesday:** the gap's 50% by 10:00 came on 74% of NFP-week Tuesdays (✓ against the other NFP-week days). Against ordinary days the held rows from Model 11 stand: Tuesday 71% vs 58% on NQ, Monday 59% vs 46% on ES.
- **Sizes:** RTH range by month position was 0.95 / 0.79 / 0.68 ADR (discount ✓, premium ✓), and by VIX 1.00 / 0.75 / 0.61 (✓ at both ends).

**Day after FOMC, NQ:**
- **FOMC high:** RTH took it on 87% of days with the month in premium vs 35% (✓), and on 19% from a discount (✓).
- **Strong overnight:** after an overnight up > 0.4 ADR, a new high after 09:30 came 87% of the time (✓) and a new low 20% (✓).
- **Gap fill:** a gap up > 0.25 ADR filled 32% of the time vs 60% (✓).
- **Next day's range:** 0.76 ADR from a premium (✓) vs 1.17 from the middle (✓).
- **Open-side quarter:** NY AM held it on 28% vs 18% of ordinary days (✓ NQ, from the Vizard study). This row moved to Hollow with Model 12.

## C. DXY (DXY futures, 5-minute, Feb 2023 – Jul 2026)

The index moved the other way to DXY in the same window. BIG = DXY's move at least its median for that window on those days, in its own ADR20.

| Window | All | DXY BIG | DXY small | Normal days |
|---|---|---|---|---|
| NFP stage 1 (08:30–08:50), NQ | 68% (n 37) | **79%** (n 19; 85 / 67; p 0.019) ✓ | 56% | 65% |
| NFP stage 1, ES | 64% (n 39) | **80%** (n 20; 86 / 67; p 0.012) ✓ | 47% | 62% |
| NFP stage 2 (08:50–09:30), NQ / ES | 69% / 68% | 72% / 74% (p 0.10 / 0.06) | 67% / 61% | 57% / 59% |
| NFP 08:30 → 16:14, NQ / ES | 46% / 49% | 42% / 45% | 50% / 53% | 57% / 60% |
| NFP week RTH, NQ (BIG ≥ 0.26) | 55% (n 121) | **64%** (n 61; 60 / 69; p 0.040) ✓ | 45% | 58% |
| NFP week RTH, ES | 54% (n 127) | **69%** (n 64; 65 / 73; p 0.004) ✓ | 40% | 62% |
| NFP week NY AM, ES (BIG ≥ 0.19) | 60% | **64%** (n 64; 71 / 57; p 0.033) ✓ | 56% | 55% |
| Day after FOMC RTH, NQ (BIG ≥ 0.52) | 63% (n 27) | **93%** (n 14; 89 / 100; p 0.002) ✓ | 31% | 58% |
| Day after FOMC RTH, ES | 63% | 79% (n 14; p 0.057) | 46% | 62% |

On NFP day the dollar relationship lives in the release window. Over the whole day after 08:30 it disappears (46–49%, below ordinary days).

## D. What went into the indicators

**Desgarrón (NFP day, formerly Cero), v2:** see section E. The card and findings now run on NQ + ES + RTY pooled numbers.
- **Chart:**
  - the 07:00–09:00 dealing range is drawn live from 07:00;
  - the ATH is carried right of price;
  - at 08:30, the ATH CE (the 50% between the ATH and the 08:29 close) runs to 17:00.
- **Stages card:**
  - 12 rows (was 20), led by the month's discount / middle / premium in the header pill;
  - SETUP, then EXPECT before 08:30 and LIVE after.
- **Findings pane:** a findings table sits beside the event clock.
- **RTY / M2K:** supported, with its own clock and tally.
- **ES:** keeps the held Monday rule: the next RTH went NFP's way only 36% vs 48%.

**Hollow:**
- The same clean-up as Desgarrón.
- The stages card reads whichever Hollow day is current or next.
- **NFP-week mode:**
  - setup: month, month open, prior day, overnight, gap, VIX, weekday;
  - expect: NY AM, RTH range, settlement window, next day;
  - live: NY AM and RTH against DXY (✓ RTH BIG), and the gap's 50% status.
- **Day-after-FOMC mode:**
  - the FOMC day's own move and range;
  - month (with the FOMC high / low take rates);
  - position against the FOMC day, overnight, gap, VIX;
  - expect: NY AM, RTH, next day;
  - live: NY AM and RTH against DXY (✓ NQ RTH BIG), the open-side quarter (✓ NQ) and the gap.
- The day-after octants and quarter moved here from Vizard.

**Caution on multiple testing:** about 2,000 group tests went into section B across the three events and both symbols, so tens of chance passes are expected. The ✓ rows with the most days behind them are the most dependable: the gap and size rows in NFP week, and NFP's range rows. Treat the small groups (n < 15) as descriptions.

## E. Desgarrón v2: NQ + ES + RTY pooled, NFP day

The sample pools 99 releases from 2018–26: 293 symbol-days (97 NQ, 97 ES, 99 RTY). Training is 240 rows on 80 dates (2018–24); the test is 53 rows on 19 dates (2025–26).

**Method changes from section A:**
- standard errors are clustered by release date;
- the shifted nulls move all three symbols together;
- a ✓ needs p < 0.05, the same side in 2018–24 and in 2025–26, and the same side on each of NQ, ES and RTY.

**HYDRA, pooled:** 406 heads × 18 targets.

**Direction:**
- Survivors against the null mean, with the null maximum in brackets:

| Target | Survivors | Null mean (max) |
|---|---|---|
| Stage 1 | 2 | 6.5 (25) |
| Stage 2 | 1 | 8.6 (73) |
| NY AM | 8 | 2.6 (18) |
| RTH | 0 | 3.9 (53) |
| 08:30 → 16:14 | 5 | 7.5 (49) |

- **Locked test:** 1 of 283 heads held for 08:30 → 16:14. That is a chance count.
- **Whole net:** AUC 0.41–0.65 on the direction targets.
- **Verdict:** pooling did not find a side.

**What held** (locked test plus all three symbols):

| Target | Heads held | Whole-net AUC, 2025–26 |
|---|---|---|
| Monday's range | 38 | |
| Range after 08:30 | 32 | |
| New low after 08:30 | 30 | 0.85 |
| ATH CE touched by 17:00 | 28 | 0.93 |
| New high after 08:30 | 27 | 0.83 |
| First DR side wins | 14 | 0.70 |
| \|NY AM\| | 7 | |

The new-high and new-low heads are mostly distance (preMove, preRng, the London move). The CE heads are mostly the distance to the ATH.

**Pooled groups that held** (range after 08:30 in ADR; new high / low after 08:30):

| Setup at 08:29 | n | Range | New high / low |
|---|---|---|---|
| Month discount | 66 | **1.21 ✓** | **61% ✓** / **91% ✓** |
| Month middle | 101 | 1.06 | 80% / 59% |
| Month premium | 126 | **0.88 ✓** | 79% / **54% ✓** |
| > 1 ADR over / under the month's open | 75 / 56 | **0.90 ✓** / **1.37 ✓** | — / **80% ✓** |
| Above PDH / below PDL | 40 / 36 | 0.93 / **1.29 ✓** | — / **40% ✓**; **36% ✓** / **92% ✓** |
| Up / down > 0.4 ADR since 18:00 | 16 / 26 | — / **1.20 ✓** | — / **25% ✓**; **19% ✓** / **85% ✓** |
| VIX > 10% over / under its average | 84 / 63 | **1.35 ✓** / **0.69 ✓** | — |
| Week up / down > 0.5 ADR | 115 / 93 | **0.82 ✓** / **1.34 ✓** | — / **53% ✓**; — / **76% ✓** |

Next session's range: discount 1.27 ✓ and premium 0.78 ✓ of ADR.

**New rows in the findings pane:**

**ATH CE** = (ATH + 08:29 close) ÷ 2, touched by 17:00:

| CE distance | Touched | n |
|---|---|---|
| ≤ 0.5 ADR | **79%** | 63 |
| 0.5–1 ADR | 23% | 26 |
| 1–2 ADR | 1% | 71 |
| > 2 ADR | 0% | 133 |

- **Within 1 ADR of the ATH:** 79% vs 3% ✓. By symbol: NQ 88%, ES 75%, RTY 73%.
- **Caution:** it was only 50% in 2025–26. Read it as distance: a close target gets hit, a far one does not.

**First side of the 07:00–08:29 range taken after 08:30** went on to be the bigger side 59% of the time:
- VIX > 10% under its average: **79%** vs 54% ✓.
- Week up > 0.5 ADR: **74%** vs 50% ✓.
- Flat week: **46%** vs 65% ✓ (lower).
- **Not held:** a quiet night (range since 18:00 ≤ 0.36 ADR) gave 71% vs 53%, but 67% vs 68% in 2025–26.

**DXY, pooled** (Feb 2023 – Jul 2026); the index went the other way:

| Stage | BIG move (of DXY's ADR20) | Other way | n | Dates | 2023–24 / 2025–26 | NQ / ES / RTY | p | Small move |
|---|---|---|---|---|---|---|---|---|
| Stage 1 | ≥ 0.42 | **82% ✓** | 60 | 20 | 86% / 72% | 80% / 80% / 85% | 0.0015 | 53% |
| Stage 2 | ≥ 0.22 | **71% ✓** | 56 | 19 | 78% / 66% | — | 0.024 | 59% |

Stage 2 had no held rule per symbol. It has one pooled.

**08:30–09:00 expansion:**
- The day's range grew **+0.14 ADR** at the median (mean +0.20) vs 0 (mean +0.03) on ordinary days ✓.
- By half: 2018–24 +0.13, 2025–26 +0.21.
- By symbol: NQ +0.12, ES +0.13, RTY +0.16.

## F. RTY on CPI days

This tests your view that the Russell likes CPI. The data is 1,411 days with all three markets, 95 of them CPI days, 2018–26.

**Size:**
- The 08:30–09:00 expansion was about 11–12× ordinary days in all three. In ADR: NQ 0.25, ES 0.27, RTY 0.33.
- The day's range was ×1.2 in each market's own ADR: NQ 1.21, ES 1.19, RTY 1.22.
- RTY's bigger raw moves (|08:29 → 16:14| 0.78% vs NQ 0.68%) are its normal higher volatility, not a CPI effect.

**Relative performance, RTY − NQ, 08:29 → 16:14:**

| | CPI days | Ordinary days |
|---|---|---|
| Mean | **−0.22%** | −0.01% |
| RTY ahead | 41% of days | 49% of days |
| 2018–24 | −0.24% | −0.02% |
| 2025–26 | −0.13% | +0.02% |

- p 0.022, and the same side in both periods.
- It lagged on CPI up days (−0.33%) and on CPI down days (−0.10% vs +0.24% on ordinary down days).
- **Against ES:** −0.15% vs −0.01% (p 0.07). On down days it was −0.30% vs −0.06%.

**Reading:** on CPI day the Russell reacts no more than NQ or ES once size is put in ADR terms, and it underperforms NQ into the close. That runs against "Russell likes CPI" if "likes" means it rallies or leads. Whether it is undervalued is a valuation question; this intraday data cannot test it.

## Files

`hydra_cal/`:
- `build.py`: the three tables;
- `fish_gen.py`: HYDRA, output in fish_nfp / fish_wk / fish_fa .txt / .json;
- `direct_gen.py`: the pre-specified groups;
- `card_stats.py`: every card number, with its held flag;
- `dxy_cal.py`: the DXY study;
- `fish_pool.py`, `card_pool.py`, `pool_extra.py`, `dr_first.py`: the pooled NQ + ES + RTY study (section E);
- `rty_cpi.py`: section F.

`calgen/`:
- `gen_data.py` and `gen_tips.py`: the packed card data and tooltips;
- `build_cal.py`: assembles Desgarrón and Hollow on the Vizard v2 template.
