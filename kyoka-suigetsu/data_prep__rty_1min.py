"""RTY 1-minute, 2018–2026 (Barchart QR files, Central Time, one file per front-month window) -> ET bars with trade dates.
Same steps as ES 2018–22: CT -> ET (+1 h); on roll trading days the old-contract part is shifted by the previous day's
settlement spread (task-2 per-contract daily files); checked against Barchart daily; holiday sessions folded into the
next CME trade date. Writes bars_RTY_raw.pkl, bars_RTY_all.pkl."""
import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np, glob
from pathlib import Path
SRC = Path(os.environ.get('KYOKA_RTY', RAW / 'RTY_1min_2018-2026'))
PC = f'{DAILY_DIR}/per_contract/RTY'
fs = []
for f in sorted(glob.glob(f'{SRC}/QR*.csv')):
    d = pd.read_csv(f); d = d[d.Time.astype(str).str.match(r'^\d{4}-')]
    d['ts'] = pd.to_datetime(d.Time); d['Close'] = d.Latest.astype(float); d['Contract'] = os.path.basename(f)[:5].upper()
    for c in ['Open', 'High', 'Low']: d[c] = d[c].astype(float)
    d['Volume'] = pd.to_numeric(d.Volume, errors='coerce').fillna(0).astype(int)
    fs.append(d[['ts', 'Open', 'High', 'Low', 'Close', 'Volume', 'Contract']])
d = pd.concat(fs)
print('files', len(fs), '| bars', len(d), '| dup ts across files:', d.ts.duplicated().sum(), '|', d.ts.min(), '→', d.ts.max())
d = d.sort_values(['ts', 'Volume']).drop_duplicates('ts', keep='last')
d['ts'] = d.ts + pd.Timedelta(hours=1)                     # CT -> ET
d['tday'] = (d.ts + pd.Timedelta(hours=6)).dt.normalize()
d['hm'] = d.ts.dt.hour * 100 + d.ts.dt.minute
d = d.sort_values('ts').reset_index(drop=True)
d.to_pickle('bars_RTY_raw.pkl')
# roll trading days: two contracts in one trade date → shift the old contract's bars by the prior day's settlement spread
cache = {}
def daily(c):
    if c not in cache: cache[c] = pd.read_csv(f'{PC}/{c.lower()}.csv', parse_dates=['Date']).set_index('Date')
    return cache[c]
nc = d.groupby('tday').Contract.nunique(); roll = nc[nc > 1].index
adj = []
for td in roll:
    x = d[d.tday == td]; old, new = x.Contract.iloc[0], x.Contract.iloc[-1]
    prev = d[d.tday < td].tday.max()
    sp = daily(new).Close.get(prev, np.nan) - daily(old).Close.get(prev, np.nan)
    m = (d.tday == td) & (d.Contract == old)
    if np.isfinite(sp):
        for c in ['Open', 'High', 'Low', 'Close']: d.loc[m, c] += sp
    d.loc[m, 'Contract'] = new
    adj.append((td.date(), old, new, sp, m.sum()))
A = pd.DataFrame(adj, columns=['tday', 'old', 'new', 'spread', 'bars_adj'])
print(f'roll trade dates: {len(A)} · spread range {A.spread.min():+.1f} to {A.spread.max():+.1f} pts · missing spreads {A.spread.isna().sum()}')
# holiday sessions → next CME trade date (task-2 daily calendar)
cal = pd.DatetimeIndex(pd.read_pickle('D_RTY.pkl').index)
td = pd.DatetimeIndex(d.tday.unique()).sort_values(); pos = cal.searchsorted(td); ok = pos < len(cal)
mp = pd.Series(pd.NaT, index=td, dtype='datetime64[us]'); mp[ok] = cal[pos[ok]]
d['tday0'] = d.tday; d['tday'] = d.tday.map(mp); d = d.dropna(subset=['tday'])
d.to_pickle('bars_RTY_all.pkl')
# check against Barchart daily of the same contract
g = d.groupby('tday').agg(H=('High', 'max'), L=('Low', 'min'), con=('Contract', 'last'), n=('ts', 'size'))
rows = []
for t, r in g.iterrows():
    dd = daily(r.con)
    if t in dd.index: rows.append((t, r.H - dd.High[t], r.L - dd.Low[t], (r.H - r.L) / (dd.High[t] - dd.Low[t]) - 1, r.n))
c = pd.DataFrame(rows, columns=['tday', 'dH', 'dL', 'rr', 'n']).set_index('tday')
print(f'trade dates {len(g)} ({g.index.min().date()} → {g.index.max().date()}) · matched to Barchart daily {len(c)} · merged holiday sessions {(d.tday != d.tday0).groupby(d.tday).any().sum()}')
for p, cc in [('2018–22', c[c.index.year <= 2022]), ('2023–26', c[c.index.year >= 2023])]:
    print(f'  {p}: days {len(cc)} · high exact {(cc.dH.abs() < 1e-9).mean() * 100:.1f}% · low exact {(cc.dL.abs() < 1e-9).mean() * 100:.1f}% · range off >2%: {(cc.rr.abs() > 0.02).sum()}')
print(c[c.rr.abs() > 0.02].round(3).to_string())
print('trade dates per year:', g.groupby(g.index.year).size().to_dict())
