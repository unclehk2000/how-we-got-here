"""1-minute bars in ET with one contract per trading day (the highest-volume one). Trading day starts 18:00 ET.
Reads from INTRADAY:
  {MKT}_*1min_continuous*.csv   Barchart 'Date,Time,…,Close,…,Contract' files, or 'Time,…,Latest' files (Contract = CONT)
  {mkt}[hmuz]2?_intraday-1min*  Barchart single-contract downloads ('Time,…,Latest'), contract taken from the file name
Barchart timestamps are Central Time; ET = CT + 1 h all year.
Writes bars_NQ_full.pkl (NQ) and bars_ES.pkl (ES 2023–2026; ES 2018–2022 comes from es_1min_2018_2022.py)."""
import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np, glob
OUT = {'NQ': 'bars_NQ_full.pkl', 'ES': 'bars_ES.pkl'}
def minutes(mkt='NQ'):
    fs = []
    for f in sorted(glob.glob(f'{INTRADAY}/*{mkt}_*1min_continuous*.csv')):
        d = pd.read_csv(f)
        if 'Date' in d.columns:
            d = d[d.Time.astype(str).str.match(r'^\d\d:\d\d$')]
            d['ts'] = pd.to_datetime(d.Date + ' ' + d.Time)
        else:
            d = d[d.Time.astype(str).str.match(r'^\d{4}-')]
            d['ts'] = pd.to_datetime(d.Time); d['Close'] = d.Latest; d['Contract'] = 'CONT'
        fs.append(d[['ts', 'Open', 'High', 'Low', 'Close', 'Volume', 'Contract']])
    for f in sorted(glob.glob(f'{INTRADAY}/{mkt.lower()}[hmuz]2[0-9]_intraday-1min*.csv')):
        d = pd.read_csv(f); d = d[d.Time.astype(str).str.match(r'^\d{4}-')]
        d['ts'] = pd.to_datetime(d.Time); d['Close'] = d.Latest; d['Contract'] = os.path.basename(f)[:5].upper()
        fs.append(d[['ts', 'Open', 'High', 'Low', 'Close', 'Volume', 'Contract']])
    d = pd.concat(fs).drop_duplicates(['Contract', 'ts'])
    d['ts'] = d.ts + pd.Timedelta(hours=1)                         # CT -> ET
    d['tday'] = (d.ts + pd.Timedelta(hours=6)).dt.normalize()
    v = d.groupby(['tday', 'Contract']).Volume.sum().reset_index().sort_values('Volume').drop_duplicates('tday', keep='last')
    d = d.merge(v[['tday', 'Contract']], on=['tday', 'Contract']).sort_values('ts').reset_index(drop=True)
    d['hm'] = d.ts.dt.hour * 100 + d.ts.dt.minute
    return d
if __name__ == '__main__':
    for m in sys.argv[1:] or ['NQ', 'ES']:
        d = minutes(m); d.to_pickle(OUT[m]); print(m, len(d), d.tday.nunique(), d.ts.min(), d.ts.max())
