"""Paths for the whole pipeline. Set KYOKA_RAW (raw data) and KYOKA_WORK (intermediate files) to override.

Every script imports this first. It adds task2/ to the import path and moves the working directory to WORK, so all
intermediate files (.pkl / .json / .npy) are read and written there by plain file name."""
import os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
RAW = Path(os.environ.get('KYOKA_RAW', ROOT / 'data')).resolve()
DAILY_DIR = RAW / 'nq_es_rty_daily_task2_1'      # Barchart daily, per contract + continuous (task 2 delivery)
ES_1822_DIR = RAW / 'ES_1min_2018-2022'          # Barchart ES 1-minute, one file per front-month window (CT)
INTRADAY = RAW / 'intraday'                      # other 1-minute files: NQ_*_1min_continuous*.csv, ES_2023_2026_*, nq[hmuz]26_*
WORK = Path(os.environ.get('KYOKA_WORK', ROOT / 'work')).resolve()
WORK.mkdir(parents=True, exist_ok=True)
for p in (ROOT / 'task2', ROOT / 'data_prep'):
    if str(p) not in sys.path:
        sys.path.append(str(p))
os.chdir(WORK)
__all__ = ['ROOT', 'RAW', 'DAILY_DIR', 'ES_1822_DIR', 'INTRADAY', 'WORK']
