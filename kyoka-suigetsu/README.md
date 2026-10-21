# Kyōka Suigetsu — research

This repository holds the research behind **Kyōka Suigetsu**, an open-source TradingView Pine v6 indicator for CME index futures (NQ, ES, RTY):
- the data preparation;
- the tests;
- the production fits that the indicator's constants come from.

The indicator itself is in `pine/Kyoka_Suigetsu.pine`. The results are written up in `docs/`.

**Conventions used throughout:**
- **Full trading day.** Every figure uses the full 18:00–17:00 ET session; nothing is split into RTH.
- **Times.** Barchart timestamps are in Central Time; Eastern Time is Central plus 1 hour all year.
- **Holidays.** A holiday session counts towards the next trading day, the CME convention that Barchart's daily bars also follow.
- **Testing.** Daily models are tested walk-forward: each year is refitted on the years before it only. Intraday models are trained on 2018–24 and tested on 2025–26. Every result is compared against a naive baseline.

## Layout

| Folder | What it holds |
|---|---|
| `config.py` | Paths. `KYOKA_RAW` points to the raw data (default `data/`) and `KYOKA_WORK` to the intermediate files (default `work/`). |
| `data_prep/` | Daily panel, daily features, 1-minute bars, the ES 2018–22 and RTY 2018–26 roll-day fixes, and the checks against Barchart daily. |
| `task2/` | Daily research: weekday / week / month profiles, the anchored HAR expected range, carry, the live projection (v1), and Python copies of the Pine logic. |
| `task3/` | ES and RTY 1-minute research: projection weights per market vs pooled, the chance the high / low is already in, days in profile, the production fit, and a minute-by-minute run of the Pine logic. |
| `tools/pine_check.py` | Checks that the Pine file parses (uses pynescript). |
| `pine/` | The indicator. |
| `docs/` | Findings for task 2 and task 3. |

## Data (not included)

The raw files are Barchart downloads and are not committed (`data/` is in `.gitignore`). Put them here:

```
data/
  nq_es_rty_daily_task2_1/     per_contract/{NQ,ES,RTY}/*.csv and continuous/*_continuous.csv
  ES_1min_2018-2022/           ESH18.csv … ESH23.csv (one front-month window each, Central Time)
  RTY_1min_2018-2026/          QRH18.csv … QRZ26.csv (one front-month window each, Central Time)
  intraday/                    NQ_YYYY_1min_continuous*.csv, NQ_Sep2026_to_date_1min_continuous*.csv,
                               ES_2023_2026_1min_continuous.csv, nq[hmuz]26_intraday-1min*.csv
```

## Run

```
pip install -r requirements.txt
./run_all.sh                 # or run the scripts one by one, in the order listed in run_all.sh
```

The whole run takes about 5 minutes.

Every script imports `config` first, then reads and writes its intermediate files in `work/` by plain file name. Scripts in later stages need the files written by earlier ones.

## Where the indicator's constants come from

| Pine | Produced by |
|---|---|
| `cfFor()` (expected-range coefficients and residual quantiles for NQ / ES / RTY / pooled) | `task2/prod_har.py` → `work/har_coef.json` |
| `PW10…PW90`, `PC10…PC90` (live projection weights, pooled NQ + ES + RTY) | `task3/prod_fit.py` (printed as Pine arrays; v12's NQ + ES fit is `task3/prod_fit_v12.py`) |
| `VREM` (NQ / ES) and `VREMR` (RTY): share of the day's variance still to come at the end of each hour; `KAPPA` | `task3/prod_fit.py` |
| CME holiday rules | checked against the calendar by `task2/pine_emul.py` |

`task2/pine_emul_har.py` and `task3/emul_ext.py` run Python copies of the Pine calculations against the research models.

## Not included

`t_intraday.py` and `t_intraday2.py` from task 2 are not included. `t_proj.py` replaces them, and they need a file from earlier, separate work.

## Reproducibility

Rebuilt from the raw files on 2026-10-11. The rebuilt daily panels, features, 1-minute bars, slot data, HAR coefficients and projection weights were identical to the originals.
