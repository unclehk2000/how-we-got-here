"""Lead inside the stage: DXY's first 5 / 10 minutes after 14:00 (and after 14:30) against what NQ / ES do for the rest of
the stage. Control: the index's own first minutes (momentum) on the same days."""
import numpy as np, pandas as pd
from scipy import stats
exec(open('dxy.py').read().split('out = {}')[0])          # loads DXD (DXY bars per trading day), M, at_close, at_open
for sym in ('NQ', 'ES'):
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl'); b = b[b.tday >= '2023-01-01']
    hm = b.hm.values; b = b.assign(m=((hm // 100) * 60 + hm % 100 - 1080) % 1440)
    F = pd.read_pickle(f'dxy_{sym}.pkl')
    rows = []
    for d in F.index:
        g = b[b.tday == d]; mm = g.m.values; dx = DXD[d]
        px = lambda h, mi: g.Close.values[np.searchsorted(mm, M(h, mi), side='right') - 1]
        po = lambda h, mi: g.Open.values[np.searchsorted(mm, M(h, mi), side='left')]
        for (h0, m0), lead, (h1, m1) in (((14, 0), 5, (14, 29)), ((14, 0), 10, (14, 29)), ((14, 30), 10, (16, 14)), ((14, 30), 30, (16, 14))):
            t0 = h0 * 60 + m0; tl = t0 + lead
            dxl = at_close(dx, tl // 60, tl % 60) - at_open(dx, h0, m0)
            ixl = px(tl // 60, tl % 60 - 1) - po(h0, m0)                  # index over the same lead minutes
            rest = px(h1, m1) - px(tl // 60, tl % 60 - 1)
            rows.append(dict(tday=d, win=f'{h0:02d}:{m0:02d}+{lead}m', dxl=dxl, ixl=ixl, rest=rest))
    R = pd.DataFrame(rows)
    print(f'\n{sym}: {R.tday.nunique()} FOMC days')
    for w, g in R.groupby('win', sort=False):
        g = g[(g.dxl != 0) & (g.rest != 0)]
        opp = (np.sign(g.dxl) != np.sign(g.rest)); mom = (np.sign(g.ixl) == np.sign(g.rest))
        k, n = int(opp.sum()), len(g)
        h = g.tday < '2025-01-01'
        print(f'  {w:10s} rest of stage OTHER way to DXY lead {opp.mean() * 100:3.0f}% (n {n}, p {stats.binomtest(k, n, 0.5).pvalue:.3f}; 2023–24 {opp[h].mean() * 100:3.0f}%, 2025–26 {opp[~h].mean() * 100:3.0f}%) · control: same way as {sym} lead {mom.mean() * 100:3.0f}%')
