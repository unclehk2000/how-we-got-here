"""Market-structure context at each half-hour mark: high / low so far today, prior day's high / low, the month's open
(the first trading day of the calendar month, 18:00 open) and the all-time high (daily highs since 2008 plus today so far)."""
import numpy as np, pandas as pd
from stats import NJ
def build(sym):
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl')
    hm = b.hm.values
    b = b.assign(m=((hm // 100) * 60 + hm % 100 - 1080) % 1440)
    D = pd.read_pickle(f'/home/claude/hm/senbon/days_{sym}.pkl')
    HJ = {}; LJ = {}
    marks = np.arange(NJ) * 30
    for td, g in b.groupby('tday', sort=True):
        mm = g.m.values; hh = np.maximum.accumulate(g.High.values); ll = np.minimum.accumulate(g.Low.values)
        idx = np.searchsorted(mm, marks, side='left') - 1               # last bar before the mark
        h = np.where(idx >= 0, hh[np.maximum(idx, 0)], np.nan); l = np.where(idx >= 0, ll[np.maximum(idx, 0)], np.nan)
        HJ[td] = h; LJ[td] = l
    D['Hj'] = pd.Series(HJ); D['Lj'] = pd.Series(LJ)
    D['PDH'] = D.H.shift(1); D['PDL'] = D.L.shift(1)
    ym = D.index.to_period('M')
    D['MO'] = D.groupby(ym).O.transform('first')
    L = pd.read_pickle(f'/home/claude/kyw/D_{sym}.pkl')
    athp = L.h.cummax().shift(1)                                       # highest daily high before each date
    D['ATHp'] = athp.reindex(D.index, method='ffill')
    return D
if __name__ == '__main__':
    for s in ('NQ', 'ES', 'RTY'):
        D = build(s); D.to_pickle(f'/home/claude/hm/senbon/ctx_{s}.pkl')
        print(s, len(D), 'MO first', D.MO.iloc[0], 'ATHp first', D.ATHp.iloc[0], 'last', D.ATHp.iloc[-1])
