# NQ Carry–Markov Regression Model
### NQ futures 2023 – Aug 2026 · CFTC TFF positioning · 2-state Markov regimes · regularised regression

---

## 1. Model structure

**Step 1. Carry decomposition.** NQ is priced off spot by cost of carry, F = S·e^{(r−q)T}. A long futures position therefore gives up the carry c = r − q as the contract converges to spot. Each week:

> **r_fut(t) = r_spot(t) − c(t)·Δt + basis noise**

So the model forecasts the carry-adjusted (spot-equivalent) return r_spot = r_fut + c·Δt. It then subtracts the known carry bleed to get the futures forecast. Holding the futures long earns only the equity risk premium over the financing rate. That is the carry-charge benchmark.

**Step 2. Markov regime layer.** Daily returns follow a 2-state hidden Markov chain:

> r_d = μ_s + σ_s·ε_d,  s ∈ {calm, high-vol},  P(s_d = j | s_{d−1} = i) = p_ij

The *filtered* probability P(high-vol | data to Friday close) is carried into the weekly model.

**Step 3. Regression layer** (all regressors known at Friday's close, after the 15:30 ET COT release):

> **r_spot(t) = Σ_s P(s_t | info_{t−1}) · (a_s + b_s′X_{t−1}) + e_t,  e_t ~ N(0, σ²(P_hv))**

The regressors X are:
- **Markov:** P(high-vol).
- **COT:** asset-manager and leveraged-fund net % OI, their 1-week changes, their 52-week z-scores, and the 4-week change in open interest.
- **Carry:** the carry level and a roll-week flag.
- **Price:** last week's return, the 4-week return and 4-week realised volatility.

**Machine learning.** The regression layer is fitted four ways and compared out of sample against the carry benchmark:

| Model | What it is |
|---|---|
| Drift | Intercept only: the carry-charge benchmark's expectation |
| OLS | All 13 regressors |
| Elastic net | L1 + L2 penalty, picked weekly by time-series cross-validation |
| Markov regression | One ridge regression per regime, weighted by regime probabilities and blended by the forecast regime probability |

---

## 2. Data and carry

**Prices.**
- 880 sessions from 4 Jan 2023 to 21 Aug 2026, roll-adjusted, one contract per day.
- That gives 175 complete weeks, Friday close to Friday close.
- Missing: 1 Jan – 12 Feb 2026 and 3 – 9 Apr 2026, which are not in the files on hand.

**COT.** CFTC TFF, NASDAQ MINI, verified against the CFTC change fields. Each report is used from the first week that opens after its Friday 15:30 release. The Oct–Dec 2025 shutdown reports are treated as unavailable.

**Carry path** (implied carry c = EFFR − dividend yield + financing spread):

| | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| Mean carry c, %/yr | 5.10 | 5.21 | 4.28 | 3.70 |
| Weekly bleed, % | ≈ 0.10 | ≈ 0.10 | ≈ 0.08 | ≈ 0.07 |

- **EFFR path:** follows the FOMC decisions through December 2025, effective rate 4.33 → 5.33 → 3.64%.
- **Dividend yield:** 0.70%.
- **Financing spread:** +0.76%, calibrated to two carry measurements taken directly from overlapping contract files:
  - NQH26 → NQM26: **3.48%** (13 Mar 2026).
  - NQM26 → NQU26: **3.90%** (10–17 Jun 2026).
- **2026 assumption:** the EFFR is held at 3.64%. This is unverified past my knowledge horizon.
- **Robustness:** the results are unchanged with carry fixed at a flat 4% (Section 5).

**Weekly averages, 2023–26:**
- Futures return +0.510%.
- Carry bleed 0.090%.
- Carry-adjusted return **+0.600% (s.d. 2.79%, s.e. 0.21%)**.

---

## 3. Markov regimes (daily)

**Table 1.** Full-sample 2-state fit, 880 days.

| | Calm | High-vol |
|---|---|---|
| Mean daily return | **+0.158%** (z 3.9) | **−0.164%** |
| Daily s.d. | 0.98% | 2.22% |
| Probability of staying | 0.979 | 0.893 |
| Expected duration | 47 days | 9 days |

**Table 2.** Stability: walk-forward refits, each using data to the date shown.

| Fit to | σ calm | σ high-vol | μ high-vol |
|---|---|---|---|
| Dec 2023 | 0.94 | 1.20 | +0.16 |
| Dec 2024 | 0.92 | 1.48 | −0.02 |
| Mar 2025 | 0.91 | 1.47 | −0.11 |
| Jun 2025 | 1.06 | 2.80 | −0.31 |
| Jun 2026 | 0.98 | 2.35 | −0.22 |

**Reading the stability table.**
- **The regimes were not distinct until April 2025.** Before that, the two states differed only slightly in volatility, and the 2023 "high-vol" state had a *positive* mean.
- **The April 2025 drawdown defined the high-vol state.** Since then the split has been stable: about 1.0% vs 2.4% daily s.d., with a negative mean in the high-vol state.
- **Practical rule:** the regime layer is reliable for describing risk from mid-2025 onward. It has one real high-vol episode behind it.

---

## 4. The mean equation: what fits in-sample

**Table 3.** OLS on the carry-adjusted weekly return, n = 175, all regressors standardised, Newey-West t (4 lags).

| Term | β (% per s.d.) | t |
|---|---|---|
| Intercept (carry-adjusted drift) | **+0.600** | **2.89** |
| Leveraged-fund net % OI | +1.09 | 1.44 |
| Leveraged-fund z-score (52w) | −1.11 | −1.38 |
| Last week's return | −0.40 | −1.23 |
| OI 4-week change | +0.23 | 1.03 |
| 4-week realised vol | +0.32 | 0.92 |
| Carry level | +0.25 | 0.79 |
| Asset-manager net % OI | −0.19 | −0.75 |
| Asset-manager 1-week change | +0.16 | 0.74 |
| Roll week | −0.12 | −0.60 |
| Others (P_hv, LEV Δ1w, AM z52, 4-week return) | \|t\| ≤ 0.43 | |

**R² = 6.8%, adjusted R² = −0.7%, F-test p = 0.17.** Only the intercept is significant. With 13 regressors on 175 weeks, the in-sample R² is what noise alone would produce.

**Weekly Markov-switching regression.**
- **Specification:** switching intercept, variance and betas on AM Δ, LEV Δ, AM z, last week's return and 4-week vol.
- **Likelihood:** −414.5 vs −423.7 for the linear model (LR 18.4 on 9 extra parameters).
- **Why it is not a regime model:**
  - The stay probabilities are **0.52 and 0.57**. The "regimes" switch almost every week.
  - It splits the sample into up weeks (μ +1.6%) and down weeks (μ −0.5%) after the fact.
  - That is curve-fitting the sign of the outcome, not a persistent state.
  - The LR statistic is also not chi-squared under Markov switching, so it carries no evidential weight.

---

## 5. Out of sample against the carry-charge benchmark

The models were refitted every week on an expanding window. The forecast weeks run from Jan 2024 to Aug 2026 (n = 123). A positive futures forecast means long; a negative one means short or flat.

**Table 4.** Direction.

| Model | OOS R² vs drift | Clark-West t | Hit % | Long/short, sum of weekly % | Long/flat, sum % | Sharpe L/S · L/F |
|---|---|---|---|---|---|---|
| **Drift = always long (benchmark)** | 0 | — | **56.1** | **+41.8** | +41.8 | **0.85** |
| OLS | −25.0% | −0.80 | 51.2 | +30.3 | +36.1 | 0.61 · 0.82 |
| Elastic net | +0.02% | 1.42 | 56.1 | +41.8 | +41.8 | 0.85 · 0.85 |
| Markov regime regression | −15.1% | −1.38 | 48.0 | −20.0 | +10.9 | −0.40 · 0.25 |

**What the cross-validation chose.** The elastic net picked an **all-zero model in 122 of 126 weekly refits**. Its best linear model of next week's NQ return is the intercept, which is the carry-charge benchmark itself. Every model that was allowed to use COT, regime or momentum terms did worse than doing nothing.

**Carry sensitivity:** with carry fixed at 4%/yr, the elastic net again collapses to the drift (OOS R² −0.02%, hit 56.1%). The carry path changes the level of the drift by at most 0.03% a week. It changes nothing about direction.

---

## 6. The variance equation: what does fit

The target is next week's realised volatility (√Σ daily r²). The comparison model is the historical average.

**Table 5.** Volatility, out of sample 2024 – Aug 2026.

| Regressors | OOS R² | Clark-West t | Corr(σ̂, \|r\|) | Inside ±1σ̂ | Inside ±2σ̂ |
|---|---|---|---|---|---|
| Past 4-week vol only | −6.4% | 2.0 | 0.15 | 63% | 91% |
| **Markov P(high-vol) only** | **+11.3%** | — | **0.37** | 60% | 86% |
| P(high-vol) + past vol | +6.9% | 3.24 | 0.29 | 61% | 86% |
| + COT z-scores (AM, LEV) | +7.1% | — | 0.28 | 62% | 85% |

**Fitted equation** (2023–26, Newey-West t):

> **ln σ_wk = 0.621 + 0.486·P_hv   (t 9.2, 3.35; R² 0.105)**
> σ_wk = exp(0.621 + 0.486·P_hv + 0.101) → **2.06%** in the calm state, **3.35%** in the high-vol state

**Reading.**
- **The regime probability fits.** It is the only input that beats the historical average out of sample for next week's risk.
- **COT adds nothing** to the variance forecast either.
- **Returns have fatter tails than a normal distribution.** Gaussian ±1σ̂ bands catch 60% of weeks, not 68%, so `forecast.py` sets its bands from the empirical error multipliers (1.05σ for 68%, 2.11σ for 95%).

**Using the regime to manage a long position:**

| Rule (weekly, OOS) | Sum of weekly % | Sharpe | Max drawdown |
|---|---|---|---|
| Always long | +38.7 | **0.81** | −24.0% |
| Long, sized to target vol (size = median σ̂ / σ̂, cap 2×) | +30.2 | 0.71 | −19.1% |
| Long, flat when P(high-vol) > 0.8 | +19.2 | 0.48 | −17.5% |

The regime layer cuts drawdown but lowers the Sharpe ratio. It goes flat or small after the shock week and misses the rebound. That is the April 2025 pattern, and with one episode it can't be generalised.

---

## 7. The model that fits

> **r_fut(t) = μ − c(t)·Δt + σ(P_hv,t−1)·ε_t**
>
> - **μ = +0.600%/week.** Carry-adjusted drift, i.e. the equity risk premium, 2023–26 (95% CI +0.19 to +1.01).
> - **c(t)·Δt = carry bleed** ≈ 0.07%/week at the current 3.70% implied carry.
> - **ln σ = 0.621 + 0.486·P_hv.** P_hv is the filtered Markov probability, with transitions p_calm→calm = 0.979 and p_hv→hv = 0.893.
> - **ε_t** has fatter tails than normal; use the empirical multipliers.

**Inputs that drop out:** COT positioning, its changes and z-scores, momentum, the roll week and the carry level. They entered neither the mean nor the variance out of sample.

This is a fully specified carry-charge Markov model.
- **Expected return:** the carry benchmark itself.
- **Risk:** set by a hidden Markov regime.
- **What it will not do:** call direction. Every attempt to make the mean depend on COT or regime made forecasts worse than the benchmark.

---

## 8. Current output (`forecast.py`)

The latest data on hand ends 21 Aug 2026. Re-run after adding newer 1-min files.

| | Week after 21 Aug 2026 |
|---|---|
| Last close (NQU26) | 29,353.25 |
| Implied carry / weekly bleed | 3.70% / 0.071% |
| Expected futures return | **+0.53%** |
| P(high-vol) now → 5 days ahead | 0.02 → 0.09 |
| Weekly σ | 2.13% |
| P(up week) | 0.60 |
| 68% band | −1.70% to +2.76% (28,853 – 30,164) |
| 95% band | −3.96% to +5.02% (28,190 – 30,827) |

---

## 9. Verdict

| Question | Answer |
|---|---|
| Does a carry-aware linear model with COT fit NQ 2023–26 returns? | No. In-sample adjusted R² is −0.7%; only the intercept is significant (t 2.9). |
| Does machine learning find something better? | It finds the intercept. The elastic net selected no regressors in 122 of 126 weeks. |
| Do Markov regimes help forecast direction? | No. The regime-weighted regression has OOS R² −15% and a 48% hit rate. |
| Do Markov regimes help with anything? | Yes, risk. Next-week volatility OOS R² is +11.3% and the band forecast is usable. |
| Does it beat the carry-charge benchmark? | No variant does on direction. The benchmark's own expectation (μ − c·Δt) *is* the best-fitting mean. |

**Bottom line:** the model that fits says to expect the carry-adjusted drift and to size your risk by the regime. It does not support calling direction from COT.

---

*Files (`NQ_Carry_Markov/`):*
- `carry_data.py` — data, carry path, COT.
- `markov.py` — regime filter.
- `model.py` — walk-forward direction models.
- `fit_vol.py` and `calib.py` — in-sample fit, variance model, sizing tests.
- `forecast.py` — this week's numbers.
- Supporting modules: `panel.py`, `weekly_px.py`.

*Statistics: Newey-West HAC t; Clark-West test for nested forecasts against the drift; OOS R² after Campbell-Thompson. Markov models estimated by maximum likelihood (Hamilton filter, statsmodels), rejecting degenerate near-zero-variance solutions.*
