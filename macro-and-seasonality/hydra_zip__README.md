# Genjutsu Kai × HYDRA: fished heads, locked test

NQ (chart) vs ES (sister), 1-minute ET, Jan 2018 to Aug 2026. Genjutsu Kai v2 is replayed exactly: 30m, 60m and OR references, a 2-minute grace and a 0.02% minimum lag.
- **Train:** 2018–24 (1,685 RTH days).
- **Locked test:** 2025–26 (359 days).
- **Controls:** windows where the sister confirmed before an SMT qualified ("both took").

**Race:** from the close of the bar where the SMT is drawn, does NQ move 1σ30 in the fade direction before it moves 1σ30 against, by 16:14?
- σ30 is the standard deviation of the last 60 one-minute log returns × √30.
- Median σ30 is 0.20%.

## A. What an SMT is worth before any fishing

| | 2018–24 | 2025–26 |
|---|---|---|
| SMTs (all three references) | 19,262 (11.4/day) | 3,754 (10.5/day) |
| Fade the SMT, race won | 49.5% [48.7–50.2] | 49.9% [48.2–51.5] |
| Control (fade the sweep) | 50.1% | 51.6% |
| Always long, same bars | 51.2% | 50.2% |

SMT minus control: t −1.06 (train), −1.29 (test). On its own, an SMT is a coin flip.

## B. Fishing (2018–24 only)

There were 635 heads: 71 base features plus 564 random combinations. The random combinations were products, differences, maxima, random thresholds and threshold pairs.

Each head was tested against three targets with day-clustered t-tests and a 10% Benjamini–Hochberg false discovery rate (FDR). For comparison, the same fishing was run on 20 time-shifted copies of each target.

| Target | BH survivors | Shifted-target null |
|---|---|---|
| Race won (direction) | 17 | mean 0.5, max 2 |
| 30-min move (direction) | 0 | mean 1.4, max 12 |
| Held vs synced | 373 | mean 2.5, max 20 |

## C. Locked test 2025–26

- **Direction:** 6 of the 17 survivors held out of sample (same sign, one-sided p<0.05).
  - Four of the six are the roll-week head in different forms.
  - The other two are distON−beta60 and relStr>0.132, both marginal.
- **Whole net as one model:** gradient boosting on all 635 heads gave a direction AUC of 0.509 against shifted-label nulls of 0.501 (max 0.521). For held vs synced it gave 0.761 against nulls of 0.503.
- **Held vs synced:** this is predictable, but mechanically. What matters is how far away the sister is, how long the window has left, and the window type.

## D. The roll-week head

Roll week is Mon–Fri of the week before quarterly expiry week.

| SMT fade race won | 2018–24 | 2025–26 |
|---|---|---|
| Roll week | 54.0% [51.5–56.5], 1,517 SMTs / 136 days, clustered t 2.61 | 57.9% [52.1–63.5], 285 / 30 days, t 2.78 |
| Other weeks | 49.1% | 49.2% |
| Always long, roll-week bars | 49.2% | 49.8% |

**Placebo weeks** (week −2, −1, roll week, +1, +2):
- Train: 47.1 / 50.2 / **54.0** / 49.9 / 46.8.
- Test: 51.1 / 53.2 / **57.9** / 51.3 / 50.6.

**Robustness:**
- **By year:** 54, 57, 54, 56, 58, 48, 51, 60, 53 (2018 to 2026).
- **Sides:** the effect shows on both the high and the low side.
- **Duplicates:** it survives removing duplicate 30m/60m SMTs.
- **Controls in roll week:** 49.4% in train, 55.2% in test.

**Size:** the edge is (2p−1)·σ30, about +0.08 to +0.16σ30 per SMT before costs. SMTs cluster within days, so the real sample is 136 and 30 days.

**Status:** a candidate. Re-check it each quarter.

## E. After the window

Fade race measured from the window close (for held SMTs and controls) or from the sync bar (for synced SMTs):

| | 2018–24 | 2025–26 |
|---|---|---|
| Held | 50.0% | 50.3% |
| Synced | 50.4% | 51.2% |
| Controls | 49.2% | 48.7% |

Whether an SMT held or synced says nothing about the direction afterwards.

## F. Sync odds (built into the indicator)

The question: will the sister take its level before the window ends?

**Model:**
- p = logistic(A + B·logit(2Φ(−gap / (κ·σ1·√left))) + kind term).
- gap = the sister's log distance from its close to its level.
- σ1 = its 1-minute σ over the last 60 bars.
- left = minutes to the end of the window.
- κ = 1.080 (30m), 1.115 (60m), 1.155 (OR). A = −0.186, B = 0.769, kind terms +0.033 (60m) and +0.015 (OR).

**Data:** snapshots every 5 minutes while an SMT is open.
- Train: 103,768 snapshots on 18,366 SMTs.
- Test: 18,541 snapshots on 3,568 SMTs.

| 2025–26 (locked) | AUC | Brier |
|---|---|---|
| Base rate by window type | 0.508 | 0.2299 |
| Random-walk formula | 0.841 | 0.1574 |
| Recalibrated formula (shipped) | 0.841 | 0.1553 |
| Formula + fished heads (logistic) | 0.841 | 0.1554 |
| Boosting on everything (ceiling) | 0.856 | 0.1477 |

**Calibration on 2025–26** (predicted→actual): 3→3, 15→14, 25→21, 35→28, 45→40, 55→54, 65→67, 75→77, 84→89, 93→93.

The fished heads add nothing beyond distance, volatility and time.

## Scripts

| Script | What it does |
|---|---|
| `hydra_events.py` | Replay, events, controls, causal features and targets |
| `hydra_fish.py` | Baselines, 635 heads, BH/Bonferroni, shifted-target null, locked test |
| `hydra_test2.py` | Whole-net model vs nulls, roll week, after-window races |
| `hydra_snaps.py`, `hydra_sync.py` | Open-SMT snapshots, sync-odds fit and test |

Data inputs are the roll-adjusted 1-minute files `bars_NQ_all.pkl` / `bars_ES_all.pkl` (ET, CME trading dates) and the daily calendar file `F_NQ.pkl`.
