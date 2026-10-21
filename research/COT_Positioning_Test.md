# COT Positioning vs NQ — Backdated Test

## Data

**Positioning:** CFTC Traders in Financial Futures, futures-only, NASDAQ MINI (code 209742). 613 weekly reports, 6 Jan 2015 → 29 Sep 2026, saved in `COT_NQ_TFF_2015_2026.csv`. The data came from the CFTC public API. Every value was then checked against the CFTC's own week-on-week change fields. All 2,448 asset-manager and leveraged-fund position values reconcile exactly.

**Prices:** NQ 1-min, 2018 and 2022 – Aug 2026.
- **Tested sample:** 261 report weeks with a complete forward window.
- **Excluded:** reports dated 30 Sep – 31 Dec 2025. The government shutdown delayed their publication, so they were not available in real time.

**Timing.** A report dated Tuesday is published on Friday at 15:30 ET. Each test enters at the first RTH open after publication (Monday 09:30) and exits 1 or 4 weeks later at the RTH open. In-sample correlation using the Tuesday date would be look-ahead.

**Features** (25 in total; each tested against 3 targets, 54 tests):
- **Net positioning, % of open interest:** asset managers (AM) and leveraged funds (LEV).
- **COT index:** Williams 0–100 over 26, 52 and 156 weeks.
- **Z-scores:** over 52 and 156 weeks.
- **Changes:** 1-week and 4-week changes in net % OI.
- **Raw position counts.**

## Results

### Direction: no edge

| Best feature → next-week return | ρ | NW t | p | 2018/22 | 2023–26 |
|---|---|---|---|---|---|
| LEV gross long count | 0.099 | 2.12 | 0.034 | 0.25 | 0.03 |
| AM z-score (156w) | 0.054 | 0.83 | 0.40 | −0.13 | 0.02 |
| AM net % OI | 0.045 | 0.81 | 0.42 | −0.14 | −0.03 |
| LEV net % OI | −0.003 | 0.09 | 0.93 | 0.02 | 0.08 |

- The Bonferroni threshold for 54 tests is p < 0.00093. No directional feature comes close, at either the 1-week or the 4-week horizon.
- The only nominal hit (LEV long count, p 0.034) comes entirely from 2018/2022 and is zero in 2023–26.
- Most signs flip between the two regimes.

**COT-index extremes → next week:**

| Signal | n | 1-week return | Up weeks | 4-week return | p vs rest |
|---|---|---|---|---|---|
| Unconditional | 261 | +0.22% | 58% | +0.83% | — |
| AM 52w index ≥ 80 | 85 | +0.47% | 64% | +1.41% | 0.39 |
| AM 52w index ≤ 20 | 43 | −0.28% | 49% | −0.93% | 0.27 |
| LEV 52w index ≥ 80 | 21 | −0.60% | 52% | −2.55% | 0.58 |
| LEV 52w index ≤ 20 | 62 | +0.37% | 65% | +0.76% | 0.72 |

The signs match the textbook reading: follow asset managers and fade leveraged funds. But no row is significant.

The AM extremes are also regime labels rather than independent signals. Every week with the 156w index ≥ 80 falls in 2023–26, and every week ≤ 20 falls in 2018/2022. "Asset managers at an extreme long" here largely means "bull market", which the drift already captures.

### Range: looks strong, but is volatility persistence

On its own, AM net positioning predicts next-week range strongly: ρ = −0.43 for the 156w index, NW t −5.4, far past Bonferroni. LEV positioning shows the opposite sign (ρ +0.28).

Once the past 4 weeks' realised range is controlled for, the effect almost disappears:

| Next-week range model | R² |
|---|---|
| Past 1w + 4w range | 0.485 |
| + AM 156w index | 0.492 (t −1.53) |
| + AM net % OI | 0.489 (t −1.26) |

Walk-forward with yearly refits, 2023–2026: adding COT worsens out-of-sample MSE by 13.6% pooled. Asset managers carry the largest net long when markets are calm. COT measures the volatility regime after the fact; it does not forecast it. The HYDRA range model already captures the same information more directly.

## Current positioning (report 29 Sep 2026, published 2 Oct)

| Group | Net % OI | 52w index | 156w index | Weekly change |
|---|---|---|---|---|
| Asset managers | +25.8% | 50 | 59 | +0.6 pt |
| Leveraged funds | −9.1% | 60 | 60 | +1.6 pt |

Both groups sit mid-range, so no extreme-positioning reading applies.

## What would make the test conclusive

261 weeks gives about 50% power to detect a true correlation of 0.12. That is small but tradable for weekly positioning, so a real edge could still be hiding below the noise floor.

Extending the sample to 2010–2026 gives about 800 weeks and roughly 90% power at the same effect size:

1. **Weekly prices.** Barchart weekly history back to 2010. The cash Nasdaq-100 ($IUXX) is preferable because it has no contract rolls; NQ nearby weekly also works. Run `cot_lab.py --weekly file.csv`.
2. **COT history.** The 2010–2014 reports are needed for the lookback windows. They come from the same CFTC source and reconcile the same way.

ES, RTY and YM give three more independent tests of the same hypothesis. Effects that hold across all four indices would be far more credible than anything from one market.

`cot_lab.py` runs the full test either from 1-min files (`--minute`) or from a weekly export (`--weekly`). It prints:
- correlations with Newey-West p-values and the Bonferroni threshold;
- the COT-index extreme tables;
- the range test with the past-volatility control;
- the latest positioning snapshot.
