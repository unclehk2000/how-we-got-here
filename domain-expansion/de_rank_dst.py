"""Rank of each form->expand pair, and a check that the 03:00 ET expansion is the European cash open:
in the DST-mismatch weeks (US on summer time, UK not) 08:00 UK falls at 04:00 ET instead of 03:00 ET."""
import pandas as pd, numpy as np
X = pd.read_pickle('/home/claude/byk/de_X.pkl')
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl')
for spl in ['train', 'test']:
    g = X[X.sp == spl].groupby('start').agg(ext=('ext', 'median'), ratio=('ratio', 'median'), brk=('brk', 'mean'))
    g['rank_ext'] = g.ext.rank(ascending=False).astype(int); g['rank_ratio'] = g.ratio.rank(ascending=False).astype(int)
    print(spl, 'of', len(g), 'half-hours'); print(g.loc[['01:30', '02:00', '02:30', '03:00', '03:30', '09:00']].round(3).to_string())
# DST mismatch days
import datetime as dt
def nth_sunday(y, m, n):
    d = dt.date(y, m, 1); d += dt.timedelta(days=(6 - d.weekday()) % 7); return d + dt.timedelta(weeks=n - 1)
def last_sunday(y, m):
    d = dt.date(y, m + 1, 1) - dt.timedelta(days=1); return d - dt.timedelta(days=(d.weekday() + 1) % 7)
def mismatch(day):
    y = day.year; d = day.date()
    return (nth_sunday(y, 3, 2) <= d < last_sunday(y, 3)) or (last_sunday(y, 10) <= d < nth_sunday(y, 11, 1))
days = pd.Series(sorted(b.tday.unique())); mis = set(days[days.map(mismatch)])
# rebuild expansion ratio for two pairs per day, flagging mismatch days
mm = (b.hm // 100) * 60 + b.hm % 100; b['sm'] = (mm - 18 * 60) % 1440
res = []
for d, x in b.groupby('tday'):
    for lab, s in [('02:30->03:00', (2*60+30-18*60) % 1440), ('03:30->04:00', (3*60+30-18*60) % 1440)]:
        f = x[(x.sm >= s) & (x.sm < s + 30)]; e = x[(x.sm >= s + 30) & (x.sm < s + 60)]
        if len(f) < 28 or len(e) < 28: continue
        R = f.High.max() - f.Low.min()
        if R <= 0: continue
        res.append(dict(pair=lab, mis=d in mis, ratio=(e.High.max() - e.Low.min()) / R))
Q = pd.DataFrame(res)
print('\nExpansion ratio (2nd half-hour range / 1st), median:')
print(Q.groupby(['pair', 'mis']).ratio.agg(['median', 'size']).round(3).to_string())
