# COT Wave — Travelling-Sinusoid Oscillator, Asset-Manager Follow-Up and the 70% Search
### NQ · ES (prices on hand) · YM · RTY (COT only, prices pending)

---

## 0. Status of the data

| | COT (CFTC TFF, verified) | Weekly prices used |
|---|---|---|
| NQ | Jan 2015 – 29 Sep 2026 | 274 weeks from the 1-min files: 2018, 2022–Aug 2026 (Jan–mid-Feb 2026 missing) |
| ES | Jan 2015 – 29 Sep 2026 | 190 weeks: 2023 – Aug 2026 |
| YM | Jan 2015 – 29 Sep 2026 | **none yet** |
| RTY | Aug 2017 – 29 Sep 2026 | **none yet** |

**Week definitions.**
- **Week bar:** Sunday 18:00 ET open → Friday close, roll-adjusted (one contract per day).
- **COT timing:** a report dated Tuesday is released on Friday at 15:30 ET. It is first used for the week that opens on the following Sunday.
- **Delayed releases:** if a federal holiday falls in the report week, the release is assumed to slip to Monday and the report is pushed back one more week.
- **Shutdown:** the Oct–Dec 2025 reports are treated as unavailable, and the last released report is carried forward through that period.

**Rerunning with full data.** When the Barchart weekly exports for NQ, ES, YM and RTY are dropped into uploads (any file with `nq`/`es`/`ym`/`rty` and `weekly` in the name), `panel.py` uses them in place of the 1-min files. The commands in Section 9 rerun everything.

**What the interim sample limits.**
- **Validation:** 2023 only for weekly models, since NQ 2018 alone is too short to train on before 2022.
- **Test:** 2024 – Aug 2026, about 176 weeks pooled.

---

## 1. The COT Wave — equation

For any weekly series x (asset-manager net % OI, leveraged-fund net % OI, or log price), take the trailing window of W weeks at every week t. Fit by weighted least squares:

> **x(s) = c₀ + c₁·s + a·sin(2πs/T) + b·cos(2πs/T),  s = 0 … W−1**

The period T is scanned over a grid (8–52 weeks for W = 52; 6–26 for W = 26; 13–78 for W = 104), and the best-fitting T is kept. The linear term strips out trend, so the sinusoid describes only the oscillation around it.

At the last point of the window:

| Quantity | Formula | Meaning |
|---|---|---|
| Amplitude | A = √(a² + b²) | size of the cycle (% OI or log-price units) |
| Phase | θ = 2π(W−1)/T + atan2(b, a), taken mod 2π | position in the cycle; 90° = crest, 270° = trough |
| **Oscillator** | **O = sin θ ∈ [−1, +1]** | the RSI-like reading; +1 at crest, −1 at trough |
| Velocity | V = cos θ | > 0 rising, < 0 falling |
| One-week projection | Δ̂ = A·[sin(θ + 2π/T) − sin θ] | the wave's forecast for next week's change |
| Weeks to next crest | ((π/2 − θ) mod 2π)·T/2π | turning-point clock |

**Why it is "travelling".** A, T and θ are re-estimated every week from data up to the prior Friday only, so the wave drifts with the market and has no look-ahead. On a synthetic noisy sine, the fitter recovers the true period exactly (20 weeks) and the phase to within 0.04 rad.

**The machine-learning refinement** operates at three levels:
1. **Choice of wave.** Window, period band and series were treated as hyperparameters.
2. **Combination.** The wave outputs (O, V, Δ̂, T, R² for price, asset managers and leveraged funds) were fed, with COT levels, changes and price momentum, into logistic and gradient-boosted classifiers.
3. **Selection.** Each model was refitted every calendar year on an expanding window and selected on validation years. It was then scored once on test years it had never seen (Section 5).

![NQ wave oscillators](wave_NQ.png)

**Figure 1.** NQ weekly cumulative log return, with weeks where the 52-week price wave sat at its crest (O > 0.92, orange ▼) or trough (O < −0.92, black ▲). Below are the 52-week price-wave oscillator and the 52-week asset-manager COT-wave oscillator. All fits are causal. The flat stretch in late 2025 is the shutdown carry-forward. In trending stretches the price wave marks "crests" all the way up the trend (2023, mid-2025), because a single sinusoid around a straight line cannot tell a trend leg from a cycle top.

---

## 2. Does the wave find peaks and troughs?

**Pivot definition:** a pivot high (low) is the highest (lowest) weekly level within ±3 weeks. Pivots are known only in hindsight and are used here purely for scoring. A "pivot hit" means a pivot within ±1 week of the reading.

**Table 1.** Sign of the one-week projection Δ̂ vs the actual week, and pivot hit rates at wave extremes.

| Wave | Use | NQ hit% (n) | NQ long% | ES hit% (n) | ES long% | NQ: pivot high at crest / base | NQ: pivot low at trough / base |
|---|---|---|---|---|---|---|---|
| Price, 26w | follow | 48.6 (222) | 56.3 | 48.2 (164) | 59.8 | 13.0 / 21.6 | 41.3 / 27.0 |
| Price, 52w | follow | 48.0 (175) | 58.9 | 56.5 (138) | 59.4 | 19.2 / 22.3 | 22.7 / 29.1 |
| Price, 104w | follow | 54.8 (126) | 56.4 | 52.3 (86) | 57.0 | 18.2 / 19.0 | 27.3 / 28.6 |
| AM COT, 26w | follow | 50.7 (274) | 55.1 | 50.0 (190) | 60.0 | 16.2 / 21.9 | 34.6 / 28.5 |
| AM COT, 52w | follow | 51.8 (274) | 55.1 | 57.9 (190) | 60.0 | 14.9 / 21.9 | 41.7 / 28.5 |
| LEV COT, 26w | fade | 52.9 (274) | 55.1 | 56.8 (190) | 60.0 | 30.6 / 21.9 | 21.4 / 28.5 |
| LEV COT, 52w | fade | 49.3 (274) | 55.1 | 54.7 (190) | 60.0 | 30.4 / 21.9 | 24.1 / 28.5 |

**Reading.**
- **Direction:** no wave beats always-long on the same weeks in either market. The best is ES AM-52w at 57.9% vs 60.0% long.
- **Crests:** wave crests are *less* likely than average to be real pivot highs. The cause is the trend artefact in Figure 1.
- **Troughs:** some trough readings look better than base (NQ AM-52w trough 41.7% vs 28.5%). But n is 22–46 per cell across 14 cells, and none of these survives a multiple-test correction.

**Phase octants of the NQ 52-week price wave → that week's return:**

| Octant (θ) | 0–45° | 45–90° | 90–135° (just past crest) | 135–180° | 180–225° | 225–270° | 270–315° (just past trough) | 315–360° |
|---|---|---|---|---|---|---|---|---|
| n | 21 | 21 | 28 | 31 | 20 | 13 | 30 | 11 |
| Mean % | −0.68 | +0.26 | +0.72 | +0.51 | +0.58 | +1.07 | +0.64 | +1.66 |
| Up % | 43 | 52 | 64 | 55 | 60 | 77 | 60 | 73 |

There is no crest-sells / trough-buys pattern. Weeks just past the crest were among the better ones.

---

## 3. The asset-manager follow-up, extrapolated

**Table 2.** Rule → the trading week after release (n = weeks traded).

| Rule | NQ n | NQ hit% | NQ long% same weeks | ES n | ES hit% | ES long% |
|---|---|---|---|---|---|---|
| Follow AM Δ1w | 274 | 52.2 | 55.1 | 190 | 53.2 | 60.0 |
| Follow AM Δ4w | 274 | 52.6 | 55.1 | 190 | 47.4 | 60.0 |
| Fade LEV Δ1w | 274 | 49.3 | 55.1 | 190 | 57.9 | 60.0 |
| AM 52w index ≥ 80 long / ≤ 20 short | 140 | 56.4 | 53.6 | 95 | 59.0 | 55.8 |
| LEV 52w index ≤ 20 long / ≥ 80 short | 85 | 58.8 | 58.8 | 71 | 52.1 | 62.0 |
| Follow AM only when AM and LEV move in opposite directions | 152 | 51.3 | 55.9 | 129 | 58.1 | 58.1 |
| Follow RTY AM Δ1w | 274 | 53.7 | 55.1 | 190 | 51.1 | 60.0 |
| Follow AM Δ1w only above 10w SMA | 169 | 49.1 | 59.2 | 129 | 54.3 | 61.2 |
| AM adding → long; else flat | 140 | 57.1 | 57.1 | 85 | 64.7 | 64.7 |

**Extrapolating the horizon.** I regressed the return over the next k = 1, 2, 4, 8 and 13 weeks on 10 COT terms, with Newey-West errors at lag k. That is 100 tests, so the Bonferroni bar is |t| ≥ 3.48.

| Market | Term | k = 1 | k = 2 | k = 4 | k = 8 | k = 13 |
|---|---|---|---|---|---|---|
| NQ | AM Δ1w | t 0.46 | −0.34 | −0.57 | −0.36 | 0.58 |
| NQ | AM-wave projection (52w) | 0.17 | −0.17 | −0.05 | 0.64 | 0.84 |
| NQ | LEV-wave projection (52w) | 0.16 | 0.14 | 0.12 | −0.03 | 0.47 |
| ES | AM Δ1w | −0.43 | 0.02 | −1.43 | −0.89 | −1.27 |
| **ES** | **AM-wave projection (52w)** | 2.29 | 2.72 | **3.61** | **3.70** | −0.46 |
| ES | LEV-wave projection (52w) | 0.01 | −0.53 | −1.70 | −2.70 | −2.64 |

**One result clears Bonferroni.**
- **Finding:** in ES, when the 52-week asset-manager wave projects that asset managers are about to *add*, the next 4–8 weeks are higher: +1.1% per s.d. at 4 weeks, +1.5% at 8 weeks.
- **Caveats:**
  - It rests on ES 2023–26 only (183 overlapping observations, about 23 independent 8-week blocks).
  - It is absent in NQ (t ≈ 0).
  - The non-overlapping 8-week hit rate equals the long base rate (69.6% vs 69.6%).
- **Status:** a lead, not a finding. It is **pre-registered here**: the full 2015–2026 rerun will test exactly this term, at these horizons, in all four markets, with no re-tuning.

**The weekly follow-AM edge is about +2 points below being long** (52–53% vs 55–60%). The textbook signs appear on extremes (follow AM highs, fade LEV highs), but those are bull-market labels, as found in the earlier COT tests.

---

## 4. NQ–RTY relationship (COT side; price side pending)

**Correlation of weekly changes in net % OI (477 weeks, Aug 2017 – Sep 2026):**

| | ES | NQ | RTY | YM |
|---|---|---|---|---|
| Asset managers vs NQ | 0.58 | 1.00 | 0.29 | 0.18 |
| Leveraged funds vs NQ | 0.36 | 1.00 | 0.28 | 0.12 |

**Findings.**
- **Weak co-movement.** RTY asset-manager flow is only loosely tied to NQ flow (0.29 vs 0.58 for ES). The two books are run largely independently.
- **No lead–lag.** RTY AM changes → NQ AM changes has Granger p of 0.11–0.32 at lags 1–4. The reverse is 0.13–0.89.
- **The spread mean-reverts.**
  - Spread = NQ AM net minus RTY AM net % OI. Long-run mean 7.8 pts.
  - Weekly reversion coefficient −0.052 (t −3.87), a **half-life of 13 weeks**.
  - Now 16.5 pts: 52-week range 9.8–33.5, z −0.84.
  - This is the one structurally stable NQ–RTY positioning feature.
- **No price edge from it so far.**
  - Following RTY AM changes for NQ: 53.7% vs 55.1% long.
  - The rotation term (NQ AM Δ minus RTY AM Δ) was included in every search round and never entered a surviving model.

**Not testable until RTY prices arrive:**
- Weekly return correlation and rolling beta.
- Cointegration of log NQ vs log RTY, and the half-life of the price spread.
- Weekly SMT: NQ makes a new 13-week high without RTY.
- Whether a stretched positioning spread predicts NQ/RTY relative performance, i.e. a pair trade.

---

## 5. Build and rebuild: the search for 70%

**How each round works.**
- **Variants:** feature-group combinations (12) × models (4: two strengths of logistic regression, shallow and deep gradient boosting) × confidence bands (|P − 0.5| > 0, 0.03, 0.06, 0.10) × mode (long/short, or long/flat).
- **Selection:** on validation; then scored once on test.
- **Null:** the whole search is rerun 20 times with each market's returns circularly shifted by a random 26+ weeks, to show how good the best variant looks with no signal at all.
- **Edge:**
  - Long/short mode: hit rate minus always-long's hit on the same weeks.
  - Long/flat mode: hit rate minus the unconditional up-rate.

**Table 3.** Rebuild log.

| Round | Target | Variants | Hit ≥ 70% on validation | Best validation hit | Same model on **test** | Test base (always long) | Test Sharpe vs always-long |
|---|---|---|---|---|---|---|---|
| 1 | Next week (both modes) | 232 | 10 | **83.3%** (n 30, long/flat, everything + deep GBM) | **57.2%** (n 159) | 58.0% | 0.85 vs 1.03 |
| 1b | Next week, long/short only | 165 | 0 | 64.2% | best-edge pick: 56.1% (n 198) | 59.1% on its weeks | 0.79 vs 1.03 |
| 2 | Next 4 weeks (non-overlapping) | 218 | 31 | **84.2%** (n 19, COT changes + GBM) | **69.2%** (n 52) | 68.3% | 1.42 vs 1.30 |
| 3 | Sparse logistic "equation", all features | 1 | — | — | 56.4% long/short; 58.1% long/flat | 58.0% | 0.94 / 1.01 vs 1.03 |

**Table 4.** What happened to every variant that cleared 70% on validation.

| Target | Variants ≥ 70% on validation | ≥ 70% on test | Median test hit | Median test edge | Beat always-long Sharpe on test |
|---|---|---|---|---|---|
| Next week | 10 | **0** | 58.1% | +0.2 pt | 4 of 10 |
| Next 4 weeks | 31 | 6 | 67.7% | −0.3 pt | 8 of 31 |

**Reading.**
1. **70% on validation is cheap.**
   - With hundreds of variants and long/flat selection, 10–31 variants reach it.
   - Under the shifted null, the best 4-week variant reaches a median 77.7% hit (95th percentile 93.7%), with a median of 32 variants ≥ 70%. That is as many as with the real data.
2. **70% on unseen data appears only where being long already gets about 70%.**
   - The six 4-week survivors sit on a test period where 68.3% of 4-week blocks were up.
   - Their edge over the base is ±1 point, i.e. the long drift of a carry-charge market.
3. **No weekly variant holds 70% out of sample, and none adds hit rate over being long.** The selected weekly model loses 0.7 points of hit rate and 0.18 of Sharpe against always-long.
4. **Of the rebuilt models, a few long/flat variants match or slightly beat always-long Sharpe** (1.42 vs 1.30 for the 4-week pick). They do it by sitting out some weeks, on 52 independent blocks. That is within noise, and they never call a down week.

**The 70% target has not been reached honestly.** The data on hand says it is not reachable for weekly NQ/ES direction from COT and wave features. The full four-market, 2015–2026 rerun gives roughly 2,300 market-weeks against 464 here and is the decisive test. On this evidence I would put the chance it delivers a weekly out-of-sample edge of even +5 points over always-long at about 10%.

---

## 6. The forecasting equation

This is a sparse (L1) logistic model, fitted on all pooled NQ + ES weeks before 2024, with the penalty chosen on 2023. Each feature is standardised by its pre-2024 mean and s.d.

> **P(up week) = 1 / (1 + e^−z),  z = 0.040 − 0.094·LEVwave26_proj − 0.069·PXwave52_osc − 0.038·vol8**

| Term | β per s.d. | Meaning |
|---|---|---|
| LEV wave (26w) projection | −0.094 | fade the leveraged-fund cycle |
| Price wave (52w) oscillator | −0.069 | slight mean reversion of the price cycle |
| 8-week mean absolute weekly return | −0.038 | calmer markets drift up more reliably |

- **Selected features:** of 56 candidates, the L1 penalty kept three. Every COT level and change term was set to zero.
- **Size of the effect:** a 2-s.d. move in all three terms together shifts P(up) by about 10 points.
- **On 2024–26:** 56.4% long/short (always-long 58.0%); 58.1% long/flat.
- **Use:** it is a tilt, not a signal, and it does not beat the carry benchmark.

---

## 7. Weekly framing — how to use the wave

The oscillator does not forecast direction. It does describe *where each group is in its positioning cycle*, which is useful context for the week. `cotwave.py` prints, after each Friday release:

**Table 5.** Readings for the report of 29 Sep 2026 (released 2 Oct).

| Market | Series | Now | Period (w) | Phase | Osc | Stage | Next-week Δ̂ | Weeks to crest / trough | Fit R² |
|---|---|---|---|---|---|---|---|---|---|
| NQ | AM net % OI | 25.8 | 17 | 140° | 0.64 | past crest, falling | −0.76 | 14.6 / 6.1 | 0.33 |
| NQ | LEV net % OI | −9.1 | 15 | 130° | 0.76 | past crest, falling | −1.93 | 13.3 / 5.8 | 0.45 |
| ES | AM net % OI | 47.7 | 13 | 357° | −0.05 | past trough, rising | +1.10 | 3.3 / 9.8 | 0.25 |
| ES | LEV net % OI | −19.6 | 18 | 239° | −0.86 | falling, below mid | −0.33 | 10.5 / 1.5 | 0.48 |
| YM | AM net % OI | 17.0 | 50 | 69° | 0.94 | rising, above mid | +0.22 | 2.9 / 27.9 | 0.50 |
| YM | LEV net % OI | −6.2 | 25 | 187° | −0.12 | falling, below mid | −1.55 | 18.3 / 5.8 | 0.50 |
| RTY | AM net % OI | 9.3 | 36 | 65° | 0.91 | rising, above mid | +0.33 | 2.5 / 20.5 | 0.77 |
| RTY | LEV net % OI | −26.8 | 52* | 308° | −0.78 | past trough, rising | +0.60 | 20.5 / 46.5 | 0.68 |

\* The period sits on the edge of the search band, so there is no clean cycle inside 8–52 weeks; treat the reading as trend.

**How to read it.**
- **Stage** tells you which side of its cycle each group is on.
- **Weeks to crest or trough** is the cycle clock.
- **R²** says how much of the past year the cycle explains. Below about 0.3, ignore it.
- **The ES AM wave projection (+1.10 now)** is the one term to watch. This is pending the pre-registered full-data test in Section 3.

---

## 8. Verdict

| Question | Answer on the data on hand |
|---|---|
| Can a travelling sine wave characterise COT positioning cycles? | Yes, descriptively. AM/LEV cycles of 13–50 weeks with fit R² of 0.25–0.77. |
| Does it locate price peaks and troughs in advance? | No. Crest readings are less likely than chance to be pivot highs, and trough readings are not significant after correction. |
| Does following asset managers beat the carry-charge benchmark? | No. 52–53% vs 55–60% for always-long, at every horizon from 1 to 13 weeks in NQ. |
| Did rebuilding reach 70%? | Only on validation, and only as often as a no-signal null does. On test, never at weekly horizon; at 4 weeks only by matching a 68% up base. |
| Anything worth carrying forward? | ES AM-wave projection → next 4–8 weeks (t 3.6–3.7), pre-registered. The NQ–RTY AM positioning spread (13-week half-life) is a candidate for the relative-value test once RTY prices arrive. |

---

## 9. Files and rerun

All scripts are in `COT_Wave/`. They need the COT CSV from earlier (`COT_TFF_NQ_ES_RTY_YM_2015_2026.csv`) and whatever prices are in uploads.

```
python3 features.py                 # builds F_{NQ,ES,YM,RTY}.pkl from weekly exports or 1-min files
python3 wave_eval.py NQ ES YM RTY   # Table 1 + octants
python3 am_follow.py NQ ES YM RTY   # Table 2
python3 am_horizon.py NQ ES YM RTY  # horizon regressions (pre-registered ES AM-wave term)
python3 run_all.py NQ,ES,YM,RTY 30 y    # search round 1 + null + locked test
python3 run_all.py NQ,ES,YM,RTY 30 y4   # search round 2
python3 survivors.py NQ,ES,YM,RTY       # Table 4
python3 equation.py NQ,ES,YM,RTY        # Section 6
python3 cotwave.py                      # weekly framing report
```

*Statistics: binomial p for hit rates; Newey-West HAC t at lag = horizon for multi-week regressions; Bonferroni across the 100 horizon tests; shifted-target null for the model search. All COT inputs reconcile exactly with the CFTC change fields (verified in the earlier COT documents).*
