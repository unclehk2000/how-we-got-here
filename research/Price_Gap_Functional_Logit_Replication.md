# Su et al. (2022) Price-Gap Model — Replicated on NQ and ES

**Source paper:** *The prediction of price gap anomaly in Chinese stock market: evidence from the dependent functional logit model*, Finance Research Letters 47, 102702.

## What the paper does

- **Data:** SSE Composite 5-minute closes; each day becomes a 52-point cumulative log-return curve.
- **Model:** functional PCA, using either a short-run covariance or a truncation-free Bartlett long-run covariance, followed by a logit on the component scores. Compared against an RBF SVM and GBDT.
- **Target:** whether the next open is ≥ today's high or ≤ today's low (a "price gap"), then each side separately.
- **Reported results:**
  - Gap either side: accuracy 0.584, AUC 0.542.
  - Gap up (HO): AUC 0.650.
  - Gap down (LO): AUC 0.687.
- **Not reported:** the base rate, a confidence interval, or any trading test. The 80/20 split of 2019 leaves about 48 test days.

## Replication on your 1-minute data

| Setting | Here |
|---|---|
| Curve | 78 points: 5-min RTH closes 09:35–16:00 ET, as log return from the 09:30 open |
| Next day | Must be the same contract and within 4 days |
| Validation | Walk-forward with yearly refits. NQ out-of-sample 2023 → Aug 2026 (n 817); ES 2024 → Aug 2026 (n 636) |
| Benchmarks | Majority class; a 4-variable scalar logit (day return, last-hour return, close location in the day's range, log range) |

### Out-of-sample AUC [95% bootstrap CI]

| Target | Event rate | Functional logit (long-run covariance) | Functional logit (short-run) | SVM | GBDT | Scalar logit |
|---|---|---|---|---|---|---|
| NQ gap either side | 40.4% | 0.520 [0.48–0.56] | 0.513 | 0.462 | 0.505 | 0.543 |
| NQ gap up | 25.2% | 0.677 [0.64–0.71] | 0.681 | 0.595 | 0.661 | **0.720** |
| NQ gap down | 15.2% | 0.673 [0.62–0.72] | 0.681 | 0.593 | 0.636 | **0.711** |
| ES gap either side | 38.2% | 0.558 [0.51–0.61] | 0.540 | 0.522 | 0.553 | 0.578 |
| ES gap up | 23.6% | 0.703 [0.66–0.75] | 0.704 | 0.588 | 0.648 | **0.755** |
| ES gap down | 14.6% | 0.635 [0.57–0.68] | 0.618 | 0.514 | 0.570 | **0.677** |

**Accuracy never beats always guessing the more common outcome.** For example, NQ gap-up: 74.4% vs 74.8%.

The paper's ranking (functional logit > SVM/GBDT) reproduces. The long-run covariance makes no difference: 0.677 vs 0.681. But a plain 4-number logit beats the functional model in every case.

## Why the one-sided gaps look predictable

It is geometry: how far the close sits from the day's high or low.

| Close location in day's range | NQ gap up | NQ gap down | NQ overnight mean | ES gap up | ES gap down | ES overnight mean |
|---|---|---|---|---|---|---|
| Q1 (near low) | 5.4% | 34.6% | +0.071% | 5.7% | 29.7% | +0.072% |
| Q2 | 11.3% | 22.7% | +0.050% | 10.9% | 18.9% | +0.064% |
| Q3 | 22.6% | 14.8% | +0.032% | 21.3% | 15.5% | −0.022% |
| Q4 | 32.8% | 7.8% | −0.040% | 33.7% | 8.0% | −0.003% |
| Q5 (near high) | 47.1% | 3.9% | −0.014% | 48.6% | 4.6% | +0.039% |

A close at the high needs only a small overnight rise to open above it. The probability of a gap changes a lot with close location, but the expected overnight return does not. The model is predicting distance, not direction.

## Trading test

Trade: hold overnight (16:00 → 09:30) in the direction of P(gap up) − P(gap down).

| | Trades | Hit | Mean per night | Total | Always long overnight |
|---|---|---|---|---|---|
| NQ | 817 | 51.4% (p 0.44) | −0.015% | −12.6% | 56.1% up, +0.047%/night, +38.1% |
| ES | 636 | 49.1% (p 0.66) | +0.012% | +7.5% | 58.3% up, +0.041%/night, +26.2% |
| NQ, top-20% conviction | 164 | 53.7% | +0.018% | — | long same nights +0.138% |
| ES, top-20% conviction | 128 | 58.6% | +0.104% | — | long same nights +0.062%; small sample |

## Conclusion

The paper's AUCs are real but mechanical: closing near an extreme makes a gap through that extreme likely, without saying which way price moves overnight. On NQ and ES the model does not beat the base rate on accuracy and is beaten by a 4-variable logit. Traded overnight, it underperforms simply holding long. It fails the same benchmark as everything else.

Script: `gap_fda.py`. It needs `hydra.py` and the 1-minute files.
