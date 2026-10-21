"""Merge the new Barchart NQ 1-min continuous files (2019, 2020, 2021, Sep 2026 -> date; CT timestamps, no contract
column) with the existing NQ set (2018, 2022 - Aug 2026). Checks: timezone, bars per day, missing trading days,
and where the continuous series switches contract (price jumps), so a roll can't land inside a day's range."""
import pandas as pd, numpy as np, glob
UP = '/root/.claude/uploads/46420b5d-8899-592c-962a-4f205cf71b0c'
fs = []
for f in sorted(glob.glob(f'{UP}/*NQ_*1min_continuous_1.csv')):
    d = pd.read_csv(f)
    d = d[d.Time.astype(str).str.match(r'^\d{4}-')]
    d['ts'] = pd.to_datetime(d.Time) + pd.Timedelta(hours=1)          # CT -> ET
    d['Close'] = d.Latest; d['Contract'] = 'CONT'
    fs.append(d[['ts', 'Open', 'High', 'Low', 'Close', 'Volume', 'Contract']])
    print(f.split('/')[-1], len(d), d.ts.min(), d.ts.max())
N = pd.concat(fs).drop_duplicates('ts').sort_values('ts').reset_index(drop=True)
N['tday'] = (N.ts + pd.Timedelta(hours=6)).dt.normalize()
N['hm'] = N.ts.dt.hour * 100 + N.ts.dt.minute

# timezone check: biggest-volume minute of the day should be the 09:30 ET open
v = N.groupby('hm').Volume.median().sort_values(ascending=False)
print('top median-volume minutes (ET):', v.index[:4].tolist())

# continuous-contract switches: jumps between consecutive bars far beyond normal 1-min moves
N['gap'] = N.Open - N.Close.shift(1)
N['dt'] = N.ts.diff().dt.total_seconds() / 60
r = (N.gap.abs() / N.Close.shift(1))
big = N[(r > 0.004)].copy()
big['pct'] = 100 * N.gap / N.Close.shift(1)
print('\nconsecutive-bar jumps > 0.4%:')
print(big[['ts', 'hm', 'dt', 'gap', 'pct']].to_string())

O = pd.read_pickle('/home/claude/twin/bars_NQ.pkl')
A = pd.concat([O, N[O.columns]]).drop_duplicates('ts').sort_values('ts').reset_index(drop=True)
A.to_pickle('/home/claude/twin/bars_NQ_full.pkl')

# coverage: trading days per year, bars per day, missing weekdays (excluding CME holidays roughly = days with no data
# that are also missing in both neighbours' years is impossible to know; list gaps of >3 calendar days instead)
c = A.groupby('tday').size()
print('\ntrading days per year:', c.groupby(c.index.year).size().to_dict())
print('days with < 600 bars (half days / partial):', (c < 600).sum())
td = pd.Series(sorted(A.tday.unique()))
g = td.diff().dt.days
print('\ngaps in trading days > 4 calendar days:')
for i in np.where(g > 4)[0]:
    print('  ', td[i - 1].date(), '->', td[i].date(), f'({int(g[i])} days)')
