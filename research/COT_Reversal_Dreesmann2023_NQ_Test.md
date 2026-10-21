# CoT Short-Term Reversal Strategy — NQ Test
### Dreesmann, Herberger & Charifzadeh (2023), *Int. J. Financial Markets and Derivatives* 9(1/2): 76–113

---

## 1. What the paper tests

The paper uses a weekly reversal strategy on the **Legacy** COT report (commercial, non-commercial and non-reportable traders). It was run on 71 US futures markets from 1986 to 2020.

Each group's net position is turned into a 26-week stochastic index:

> index = (net_t − min₂₆) / (max₂₆ − min₂₆)

| Rule | Conditions (all required) |
|---|---|
| Long entry | Commercial index > 0.7 · commercial long ≥ 30% of OI · non-reportable index < 0.3 · 10-week SMA rising |
| Long exit | Non-commercial index > 0.7 **and** 10-week SMA falling |
| Short entry | Commercial index < 0.3 · commercial short ≥ 30% of OI · non-reportable index > 0.7 · 10-week SMA falling |
| Short exit | Non-commercial index < 0.3 **and** 10-week SMA rising |

- **Timing:** the signal is taken at the week's close and filled at the next week's open.
- **Costs:** 0.2% per side.
- **Sizing:** 50% of equity per trade.

**The paper's own Nasdaq-100 result (Table 2 / Table 4):**

| | Annual return | SD | Sharpe |
|---|---|---|---|
| Long-only CoT | 19.19% | 18.13% | 1.06 |
| Long-and-short CoT | 7.34% | 13.04% | 0.61 |
| Their S&P 500 buy-and-hold benchmark | 32.00% | 30.00% | 1.07 |

The authors conclude that the CoT strategy did not beat buy-and-hold in any market or portfolio. They read this as evidence that the COT report helps keep derivatives markets efficient.

### Two problems in the paper

1. **The benchmark is impossible.**
   - The S&P 500 closed 1985 at about 211 and 2020 at about 3,756. That is roughly **8.6% a year** in price terms, not 32%, and with nowhere near 30% annual volatility.
   - Their engine overstates buy-and-hold by about four times. The Sharpe of 1.07 is similarly inflated.
   - So none of the paper's absolute numbers can be used, in either direction: neither "CoT failed" nor "Nasdaq's Sharpe of 1.06 is close."
2. **The printed "commercial index" formula uses non-commercial positions.**
   - This is a typo: the trading rules clearly refer to the commercial index.
   - I used commercial net positions.

---

## 2. Data

**Legacy futures-only COT, E-mini Nasdaq-100 (code 209742), from CFTC Socrata.**

| Check | Result |
|---|---|
| Week-on-week changes vs the CFTC's own `change_in_*` fields | 987 checks, **0 mismatches** |
| Long side and short side each sum to open interest | 144 / 144 weeks |
| Open interest vs the verified TFF file | 159 / 159 weeks identical |

**Coverage.** The CFTC server rate-limited the pull:
- **Obtained:** NQ 2017-Q4, 2018, 2021 and 2026.
- **Not obtained:** 2022–2025 and all ES data.

**Prices.** Weekly prices were built from the 1-minute files:
- One contract per trading day.
- Roll-adjusted: on roll days the return is open-to-close of the new contract.
- Trades run Sunday open to Sunday open.

**What this allows:**
- **NQ 2018** is the only year with both a 26-week COT history and price data.
- **2026** has COT data, but the index only becomes valid from 30 June. That leaves about 7 tradeable weeks before the price data ends, which is too few to use.

---

## 3. Can the TFF report stand in for the Legacy categories? No.

I tested the TFF report against the real Legacy series over the overlapping weeks (n = 144 for levels, n = 69 for index values).

The mapping tested was: asset managers as commercials, leveraged funds as non-commercials, and −(asset managers + leveraged funds) as non-reportables.

| | Correlation |
|---|---|
| Legacy commercial net vs TFF asset-manager net | **−0.45** (index: **−0.69**) |
| Legacy non-commercial net vs TFF leveraged-fund net | +0.33 (index: +0.37) |
| Legacy non-reportable net vs −(AM + Lev) | −0.53 (index: −0.25) |
| Weeks with commercial index > 0.7: Legacy vs proxy | 17 vs 27, **agreeing on 1** |

**In NQ, Legacy "commercials" are mostly dealers, and dealers sit on the opposite side of asset managers.** A TFF version of this strategy would be trading a different signal, so I did not run one.

---

## 4. Result: NQ 2018 (41 tradeable weeks, 16 Mar – 21 Dec 2018)

**How often each condition was met (41 weeks):**

| Condition | Weeks met |
|---|---|
| Commercial index > 0.7 | 14 |
| Commercial long / OI ≥ 30% | 41 |
| Non-reportable index < 0.3 | 5 |
| SMA rising | 22 |
| **All four (long entry)** | **2** |
| **All four (short entry)** | **0** |

**Trades:**
- **One trade.** The long signal came in the week of 20 April 2018 and filled at the open on 22 April. It was still open when the data ends on 21 December.
- **Peak open profit:** +14.8% in late September 2018.
- **Result:**

| | Return |
|---|---|
| CoT strategy, 0.2% cost (paper) | −6.50% |
| CoT strategy, 0.01% cost (realistic for NQ) | −6.32% |
| Always long, same 41 weeks | −11.50% |

**Why it held through the Q4 2018 drop.**
- The long exit needs a non-commercial buying climax (index > 0.7) **and** a falling 10-week SMA in the same week.
- Non-commercials were above 0.7 for 17 weeks from June to October, but the SMA was rising throughout.
- When the SMA turned down in October, non-commercials had already cut back (index 0.52 → 0.06).
- **Across all 35 weeks the trade was open, the two exit conditions were met together in 0 weeks.**
- Non-commercial positioning tracks the trend, so the two conditions tend to be met at different times. Once long, the strategy rarely exits on its own rule. In practice it becomes a long-only hold.

---

## 5. Verdict against the carry-charge benchmark

- **No evidence of an edge.** The 2018 window gives one trade, so it cannot show an edge or rule one out. Beating always-long by 5 points there comes from a single entry date (skipping the first 6 weeks of the window). It is not a repeatable result.
- **The paper's own Nasdaq-100 result does not beat its benchmark.** Its absolute numbers are unreliable anyway (Section 1).
- **The rule set has a structural flaw.** Exits almost never fire, so the long-only version turns into delayed buy-and-hold. That can only match the carry-charge market by luck in its entry date.
- **This is consistent with the earlier COT work:**
  - TFF positioning tests.
  - SBM 2004 Granger tests: positions follow returns.
  - 1-minute release-matched test: about 50–56% after release.

**To finish the test on 2022–2026 (NQ and ES):**
- Attach the CFTC Legacy **Futures Only** annual files for **2022, 2023, 2024 and 2025**.
- They are on cftc.gov, under *Commitments of Traders → Historical Compressed* (`deacot2022.zip` … `deacot2025.zip`).
- They include both NQ (209742) and ES (13874A). `cot_reversal.py` then runs unchanged on about 230 weeks per market.

---
*Files:*
- *COT_Legacy_NQ_209742_2017Q4_2018_2021_2026.csv* — verified Legacy data.
- *cot_reversal.py* — rules, back-test and benchmark.
- *weekly_px.py* — roll-adjusted weekly prices from the 1-minute files.
