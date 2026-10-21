# COT vs NQ/ES — Matched to the 1-Minute Data on Hand

## Data

**1-minute price files available.** No RTY or YM 1-minute files exist; the per-contract NQ files in Downloads only duplicate the continuous files from January onward.

| Market | Coverage | Sessions |
|---|---|---|
| NQ | 2018, 2022 – 20 Aug 2026 | 1,387 |
| ES | 2 Jan 2023 – 28 Aug 2026 | 946 |

**COT truncated to that coverage.** `COT_TFF_NQ_ES_RTY_YM_2015_2026.csv` is cut to the 288 report weeks between 2 Jan 2018 and 25 Aug 2026 that fall inside the 1-minute data, giving 1,152 rows across the four markets. Each row carries coverage flags for NQ and ES. Saved as `COT_truncated_to_1min_coverage.csv`.

**Windows, timed to the minute (ET):**

| Window | From | To |
|---|---|---|
| Report week | Tuesday 15:59 bar, prior week | Tuesday 15:59 bar, report week |
| Post-release (tradable) | Close of the 15:30 bar on release Friday | Same bar on the next release Friday |
| Release reaction | 15:30 | 16:00 on release Friday |
| Weekend gap | Friday 16:14 | Sunday 18:00 open |

**A week is kept only if:**
- both bars exist in the same contract;
- there is no session gap longer than 4 days between them;
- the release wasn't delayed by the Oct–Dec 2025 shutdown.

Weeks containing a contract switch drop out. This leaves 250 NQ and 173 ES report-week windows, and 202 NQ and 133 ES post-release windows.

## Results

| Rule | Report week (already happened) | Release → next release (tradable) | Long-only, same tradable weeks |
|---|---|---|---|
| Follow AM change, NQ | 58.0% (p 0.014) | **53.0% (p 0.44)** | 55.4% up |
| Follow AM change, ES | 61.3% (p 0.004) | **50.4% (p 1.00)** | 54.9% up |
| Fade LEV change, NQ | 58.8% (p 0.006) | **47.5% (p 0.53)** | 55.4% up |
| Fade LEV change, ES | 71.7% (p < 0.0001) | **50.4% (p 1.00)** | 54.9% up |
| 4-market breadth (4/4 long, 0/4 short), NQ | 81.7% (p < 0.0001) | **55.0% (p 0.52)** | 60.0% up |
| 4-market breadth, ES | 81.8% (p < 0.0001) | **47.4% (p 0.87)** | 65.8% up |

### Does the release itself move price?

| | NQ | ES |
|---|---|---|
| 15:30→16:00 move agrees with AM change | 48.7% (n 236, p 0.74) | 43.9% (n 155, p 0.15) |
| Correlation, AM change vs 15:30–16:00 move | −0.06 | −0.06 |
| Mean absolute 15:30–16:00 move | 0.19% | 0.12% |
| Weekend gap agrees with AM change | 49.4% (p 0.90) | 46.1% (p 0.37) |

The release produces no directional reaction in either market. Price neither moves toward the asset managers' change in the half-hour after publication nor gaps that way on Sunday.

### Other tests

**Extremes** (52-week COT index, release→release): no group differs from the rest.
- NQ AM ≥ 80: +0.45%, 62% up (n 73) vs +0.07% (p 0.32).
- NQ LEV ≥ 80: −0.54% (n 16, p 0.32).
- ES: all p ≥ 0.24.

**SBM 2004 pooled NQ + ES** (release→release, clustered by week):
- AM change: t +1.24, p 0.22.
- LEV change: t −0.46, p 0.65.

**By year, NQ follow-AM after release:**

| 2018 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| 46% | 63% | 50% | 42% | 57% | 68% |

Even the good years don't consistently beat being long. 2024: 42% hit vs 65% up. 2026: 68% vs 63%, on only 19 weeks.

## Conclusion

On minute-exact timing over the data actually on hand, the result matches the daily tests and the 2004 paper. COT changes line up with the week the report describes (58–82%) and carry no information from the moment they are published. The release causes no directional move at 15:30, none over the weekend, and none over the following week.

Script: `cot_1min.py`. It needs `hydra.py`, the 1-minute files and the 4-market COT CSV.
