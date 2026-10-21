# ARDL Equation — Run on NQ Time-and-Price Data

Δs_t = c + Σφ_iΔs_{t−i} + Σβ_jΔ(i−i*)_{t−j} + Σγ_kΔcis_{t−k} + Σδ_ℓΔσ_{t−ℓ} + Ση_m f_{t−m} + λ′z_t + ε_t

**Data:** NQ, ES, DXY 1-min/5-min, Jan 2023 – Aug 2026, 838 NQ trading days (2026 coverage: 13 Feb – 20 Aug, gap 3–10 Apr). One contract per day by volume; 14 roll days excluded from overnight terms. Barchart CT shifted to ET.

---

## 1. How each term was mapped

The equation is a currency model. Two of its inputs (rate differential, cross-currency basis) do not exist for an equity index future and had to be proxied. The proxies are stated so nothing here is mistaken for the original FX specification.

| Term | Original meaning | NQ mapping used |
|---|---|---|
| Δs_t | FX spot return | NQ RTH return, 9:30 open → 16:14 close (%) |
| φ_iΔs_{t−i} | Own lags | Prior RTH returns |
| β_jΔ(i−i*) | Interest-rate differential | **Proxy:** DXY % move (dollar strength embeds the rate differential; no rate data in the dataset) |
| γ_kΔcis | Cross-currency basis | **Proxy:** NQ-minus-ES relative move (cross-index basis between correlated contracts) |
| δ_ℓΔσ | Volatility change | Δ log range % (RTH for lags, overnight for j = 0) |
| η_m f | Order flow | NQ overnight move, prior RTH close → 9:30 open |
| λ′z_t | Controls | Weekday dummies, NFP, FOMC (CPI omitted — the verified CPI date list was lost in a workspace reset and was not re-entered from memory) |

**Making it forecastable:** the j = 0 terms use only the portion of day t completed before 9:30 (overnight DXY, overnight NQ−ES spread, overnight vol change, overnight NQ move). Every regressor is known at the RTH open, so the model is a genuine pre-open forecast, not a contemporaneous fit.

**Estimation:** OLS, Newey-West (HAC, 5 lags) standard errors. Lag lengths chosen by BIC on 2023–24 only. Out-of-sample: expanding window, refit monthly, Jan 2025 → Aug 2026.

---

## 2. Return specification — significant in-sample, fails out-of-sample

BIC selected p = 1, q = 2. Full sample n = 741, R² = 0.083 (adj 0.059).

| Term | Coef | t (HAC) |
|---|---|---|
| φ — prior RTH return | −0.300 | −2.32 |
| β — overnight DXY (j=0) | +0.057 | +0.33 |
| **β — prior-day DXY RTH move (j=1)** | **−0.466** | **−3.06** |
| γ — overnight NQ−ES spread | +0.705 | +1.83 |
| δ — overnight vol change | −0.160 | −2.35 |
| η — overnight NQ move | −0.343 | −2.16 |
| λ — NFP / FOMC / weekdays | all \|t\| < 1.6 | — |

Joint block tests (χ², HAC): φ p = 0.020, β p = 0.020, η p = 0.010, γ p = 0.23, δ p = 0.11, λ p = 0.22.

Read in-sample: reversal of the prior RTH session, fade of the overnight move, and a dollar effect (DXY up yesterday → NQ RTH down today).

**Walk-forward, 312 days:**

| | Result |
|---|---|
| OOS R² vs expanding-mean forecast | **−0.041** |
| Corr(forecast, actual) | 0.016 |
| Directional hit rate | 53.1% (CI 47.5–58.5%) |
| Always-long hit rate | 54.5% |
| Sign-of-forecast strategy, total | +11.6% vs always-long +19.1% |

Forecast quintiles do not rank outcomes (top quintile realised −0.04%). **Verdict: no usable directional edge.** In-sample significance came from fitting 19 parameters to noise-dominated returns.

**The DXY term specifically:** run alone, prior-day DXY gives OOS R² +0.007 and a 56.7% hit rate — the only single term with a positive out-of-sample result. But its coefficient is unstable by year (2023 +0.02, 2024 −0.26, 2025 −0.36, 2026 −0.77, none individually significant). Treat it as a regime-dependent lean that has strengthened since 2024, not a constant law.

---

## 3. Volatility specification — the equation works here

Same structure, dependent variable = log RTH range %, regressors in absolute value. BIC selected p = 3, q = 0. Full sample n = 765, **R² = 0.351**.

| Term | Coef | t (HAC) |
|---|---|---|
| φ — range lag 1 / 2 / 3 | +0.230 / +0.289 / +0.133 | +6.1 / +8.1 / +3.7 |
| δ — overnight vol change | +0.091 | +3.29 |
| η — \|overnight NQ move\| | +0.133 | +3.07 |
| λ — FOMC day | **+0.350** | +4.76 |
| λ — Monday / Thursday | −0.109 / +0.115 | −2.25 / +2.48 |
| β (\|DXY\|), γ (\|NQ−ES\|) | not significant | — |

**Walk-forward, 324 days:** OOS R² **0.422**, corr 0.645.

| Forecast quintile | Realised RTH range |
|---|---|
| Q1 (lowest) | 0.96% |
| Q2 | 1.08% |
| Q3 | 1.45% |
| Q4 | 1.47% |
| Q5 (highest) | **2.30%** |

**Does the full equation beat plain lagged volatility?** Yes, by a measurable margin, on the identical 324 days:

| Spec | OOS MSE improvement vs AR(3)-only |
|---|---|
| AR(3) lagged range only | baseline (OOS R² 0.367) |
| + calendar controls z_t | +2.8% |
| + overnight flow, vol change, proxies (full equation) | **+8.7%** (OOS R² 0.422) |

An FOMC day adds ~+0.35 to log range (≈ 42% wider), consistent with Vizard. The overnight move and overnight vol change carry real information about how far the RTH session will travel.

---

## 4. Conclusions

1. **Direction:** the equation does not forecast NQ RTH direction out-of-sample (OOS R² −4%, hit rate below always-long). Do not trade it for bias.
2. **Range:** the same equation forecasts RTH range strongly (OOS R² 0.42; Q5 days run 2.4× the range of Q1 days) and beats a pure lagged-volatility benchmark by 8.7% MSE.
3. **Practical use:** compute the pre-open range forecast and scale stops/targets by it. This matches the framework's recurring finding — Byakugan's 7–9am range (r = 0.40), Hollow's settlement window, Full Bringer's FOMC-range carry (r = 0.52) — that magnitude is predictable while direction mostly is not.
4. **Proxy caveat:** β and γ are proxies. A faithful test of the original terms would need daily Treasury yields (2y/10y vs Bund/JGB) and futures calendar basis or cost-of-carry data, neither of which is in the current dataset.

---

## 5. NQ is a carry-charge market — what that changes

US index futures are priced off cost of carry, not left free to float: **F = S · e^((r − q)·T)**, where r is the financing rate and q the index dividend yield. That is the same arbitrage relationship that sets FX forward points from the interest-rate differential. So the equation's β term has a real NQ counterpart, and DXY was the wrong stand-in for it.

| FX term | Carry-market counterpart |
|---|---|
| Δ(i − i*) | Δ(r − q): the implied financing rate net of dividends, read from the calendar spread |
| Δcis (basis) | Futures minus fair value, F − S·e^((r−q)T). Needs the cash NDX, which is not in the dataset |

### Measured carry (two contracts trading in the same minutes)

| Window | Calendar spread | Implied carry (annualised) |
|---|---|---|
| NQH26 → NQM26, 13 Mar 2026 | 211 pts | 3.45% |
| NQM26 → NQU26, 10 Jun 2026 | 280 pts | 3.90% |
| NQM26 → NQU26, 18 Jun 2026 (expiry week) | 317 pts | 4.23% |

Fed funds was 3.50–3.75% and the NDX yields well under 1%, so r − q on policy rates is roughly 3%. Implied carry ran about a point above that: the futures were priced off a financing rate richer than policy rates. Carry also widened 0.33 points through the June roll week, as rolling longs bid the deferred contract.

The roll jumps in the 2023–25 continuous files (−217 to +599 pts) are **not** usable carry estimates. Every switch happens across a weekend, so each jump also contains the weekend's price move.

### Three structural consequences for this framework

1. **The continuous files are not back-adjusted.** Each quarterly switch steps price by the calendar spread, about 1–1.5% (roughly 200–320 NQ points). Single-session statistics (ranges, session nets, RTH returns, everything in Sections 2–3) are unaffected. Comparisons that cross a switch are not like-for-like: NWOGs on switch weekends, prior-week highs and lows in the week after a switch, monthly net moves, and the 60-day NDOG/NWOG persistence work, where older gaps can sit across a switch. The September 2022 case study has been corrected for this.
2. **Every quarterly expiration Friday is missing.** The files stay on the expiring contract until the Sunday after expiry, and that contract settles at the 9:30 open, so third Fridays have no RTH session. 13 of the 14 in 2023–26 are absent (19 June 2026 was Juneteenth). No statistic in this framework includes a quad-witching session.
3. **Basis decay is a deterministic drift.** The front contract converges to cash at about F·(r − q)/365: roughly 3 points a day at current levels (about 0.011%), or about 270 points over a quarter. That is negligible against a ~1.4% RTH range, but material for multi-week futures drift statistics, which lag cash by about 0.08% a week.

### Does the contract cycle affect intraday behaviour?

| Window | RTH range | RTH return |
|---|---|---|
| Roll period (expiry − 8 days → expiry), n = 83 | 1.44% | +0.05% |
| Rest of cycle | 1.48% (p = 0.76) | +0.06% (p = 0.88) |

Adding a roll-period dummy to the volatility model gives t = −0.37. RTH range by days to expiry is flat (1.23–1.38% across all buckets). **The carry cycle leaves no measurable trace on intraday range or direction**, so Sections 2–3 stand as they are.

### Where carry belongs in the equation

Implied carry moves slowly: it shifts with rate expectations and roll flows, not intraday. As a daily RTH regressor it would be nearly constant, so the correct horizon is weekly: Δ(carry) week on week → next-week range. Testing that needs data this workspace doesn't have:

- Daily settlements for the front and next contract on NQ, ES, RTY and YM (Barchart per-contract daily history, the same format as the NQU24 daily files)
- Daily SOFR (FRED)
- Optionally, the cash NDX/SPX, to measure basis to fair value directly
