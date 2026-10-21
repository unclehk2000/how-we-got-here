# COT Four-Market Breadth — NQ, ES, RTY, YM

## Data

- **Source:** CFTC Traders in Financial Futures (futures-only) reports for NASDAQ MINI, E-MINI S&P 500, RUSSELL E-MINI and DJIA x $5.
- **Coverage:** NQ, ES and YM run Jan 2015 → Sep 2026. RTY starts Aug 2017, when the E-mini Russell moved to CME.
- **Verification:** every asset-manager and leveraged-fund long and short reconciles exactly with the CFTC's own week-on-week change field. That is 9,248 values with 0 mismatches.
- **File:** `COT_TFF_NQ_ES_RTY_YM_2015_2026.csv`.

**Prices and timing.** NQ prices cover 2018 and 2022–26; ES covers 2023–26. "Same week" means the Tuesday→Tuesday window the report describes. "Week after" means the first Monday open after the Friday release through to the next Monday open; that is the earliest anyone could act. Reports delayed by the Oct–Dec 2025 shutdown are excluded from the week-after figures.

## Results

**Breadth** = how many of the four markets show asset managers' net position (% of open interest) rising week on week.

| Breadth | NQ same week | NQ week after | ES same week | ES week after |
|---|---|---|---|---|
| 0/4 adding | −2.54%, 22% up | +0.47%, 52% up | −1.40%, 21% up | +0.78%, 62% up |
| 1/4 | −0.88%, 43% | +0.09%, 52% | −0.29%, 51% | +0.12%, 53% |
| 2/4 | +0.75%, 69% | −0.06%, 57% | +0.49%, 67% | +0.31%, 69% |
| 3/4 | +1.21%, 69% | +0.21%, 51% | +0.82%, 72% | +0.50%, 63% |
| 4/4 adding | +2.75%, 91% | +0.29%, 66% | +1.90%, 91% | +0.26%, 76% |
| Spearman ρ | **+0.51 (p < 0.0001)** | **+0.03 (p 0.68)** | **+0.47 (p < 0.0001)** | **+0.05 (p 0.51)** |

**Checklist rule.** Bullish when NQ and ES asset managers are both adding and RTY and YM are not reducing; bearish is the mirror image.

| | Same week | Week after |
|---|---|---|
| NQ hit rate | **83.5%** (p < 0.0001) | **55.7%** (p 0.37) |
| ES hit rate | **84.3%** (p < 0.0001) | **54.0%** (p 0.67) |

**"All four aligned" traded long/short in the week after:**

| | Trades | Hit | Mean return | Always long, same weeks |
|---|---|---|---|---|
| NQ | 79 | 55.7% | −0.13% | 58.2% up, +0.39% |
| ES | 50 | 54.0% | −0.34% | 68.0% up, +0.56% |

**Paper method, pooled NQ + ES** (Sanders, Boris & Manfredo 2004; weekly position change → next week's return, N = 430):
- Asset-manager change: t −0.05 (p 0.96).
- Leveraged-fund change: t +0.52 (p 0.61).

## Reading

When all four markets line up, the signal "confirms" the move 84% of the time, but only for the week the report describes, which has already happened by Friday's release. Positioning follows price: asset managers add across every index in the same weeks that equities rise. Once the report is public, aligned breadth calls the next week 54–56% of the time and loses money against simply being long on the same weeks.

The bullish 4/4 reading on its own is 66% up for NQ (n = 35) and 76% for ES (n = 21). That sits above the base rates but is not significant at these sample sizes, and it is a long-only observation, not a directional edge.

## Latest report (29 Sep 2026, released 2 Oct)

| | Asset manager net % OI | Weekly change |
|---|---|---|
| NQ | +25.8 | +0.55 |
| ES | +47.7 | −1.74 |
| RTY | +9.3 | +1.33 |
| YM | +17.0 | +0.81 |

Breadth is 3/4. ES asset managers reduced while the other three added.

Script: `cot4.py`. It needs `hydra.py`, the NQ/ES 1-min files and the COT CSVs.
