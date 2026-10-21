# Bala and Hollow × HYDRA: NFP day, NFP week and the day after FOMC

The data is NQ and ES front-month futures, 1-minute bars in ET, Jan 2018 – Oct 2026 (ES to Aug 2026). It uses the same protocol as the FOMC study behind Vizard:
- **Train:** 2018–24.
- **Locked test:** 2025–26.
- **Replication:** ES.
- **ADR20:** mean high − low of the 20 prior trading days.

**Rule for a ✓:** p < 0.05 over 2018–26, and the same side in 2018–24 and 2025–26.

| Event | Days (NQ) | Train / test | Snapshot | Model |
|---|---|---|---|---|
| NFP release day | 97 | 80 / 17 | 08:29 | Bala (6, formerly Cero) |
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

**Bala (NFP day, formerly Cero):**
- The PO3 candles, the VIX and DXY cards and the checklist are gone; Gran Rey Cero keeps the PO3 candles and its own VIX and DXY cards.
- Tally only.
- A new NFP stages card:
  - **SETUP at 08:29:** month, month open, prior day, 18:00, the week into the release, VIX.
  - **EXPECT:** stage 1 (08:30–08:50), stage 2 (08:50–09:30), NY AM, the range after 08:30 and the next session, by month position.
  - **LIVE on NFP day:** stage 1 and stage 2 against DXY, with BIG at 0.42; NY AM; the big-DXY row (✓); the 08:30–09:00 expansion (✓ +0.19× vs +0.02–0.03× ADR).
- ES adds the held Monday rule: the next RTH went NFP's way only 36% vs 48%.

**Hollow:**
- The same clean-up as Bala.
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

## Files

`hydra_cal/`:
- `build.py`: the three tables;
- `fish_gen.py`: HYDRA, output in fish_nfp / fish_wk / fish_fa .txt / .json;
- `direct_gen.py`: the pre-specified groups;
- `card_stats.py`: every card number, with its held flag;
- `dxy_cal.py`: the DXY study.

`calgen/`:
- `gen_data.py` and `gen_tips.py`: the packed card data and tooltips;
- `build_cal.py`: assembles Bala and Hollow on the Vizard v2 template.
