#!/usr/bin/env bash
# Rebuild everything from the raw data. KYOKA_RAW / KYOKA_WORK override the default data/ and work/ folders.
set -euo pipefail
cd "$(dirname "$0")"
run() { echo "== $*"; python3 "$@"; }
# 1. data preparation
for s in load_daily features_daily bars_1min es_1min_2018_2022 es_roll_adjust bars_all check_vs_daily rty_1min; do run data_prep/$s.py; done
# 2. task 2 — daily data
for s in t_weekday t_week t_week_null t_month t_har har2 t_wf t_carry t_extra slots t_proj prod_har pine_emul pine_emul_har; do run task2/$s.py; done
# 3. task 3 — ES and RTY 1-minute data
run task3/slots2.py RTY; run task3/slots30.py RTY
for s in slots2 slots30 proj_es ext_test ext_eval ext_rw n_test rty_transfer rty_emul prod_fit emul_ext; do run task3/$s.py; done
