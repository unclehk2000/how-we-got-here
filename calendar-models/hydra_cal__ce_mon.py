"""ATH CE (ATH + 08:29 close) ÷ 2 on NFP day: touched by 17:00 vs by the next session's 11:00 (Monday after an NFP Friday),
pooled NQ + ES + RTY, by the CE's distance at 08:29 (ADR)."""
import numpy as np, pandas as pd, json
from scipy import stats
from common import *
rows = []
for sym in ('NQ', 'ES', 'RTY'):
    G = days(sym); X = pd.read_pickle(f'nfp_{sym}.pkl'); idx = sorted(G)
    for d, r in X.iterrows():
        if not (r.ath > r.price): continue
        k = idx.index(d) if d in G else None
        if k is None or k + 1 >= len(idx): continue
        n = Day(G[idx[k + 1]]); hN, _ = n.rng(0, M(11, 0))
        rows.append(dict(sym=sym, tday=d, dist=r.ceDist, day=r.ceDay, mon=float(r.ceDay == 1 or hN >= r.ce), gapd=(idx[k + 1] - d).days))
Y = pd.DataFrame(rows); Y['band'] = pd.cut(Y.dist, [0, 0.5, 1, 2, 99], labels=['≤0.5', '0.5–1', '1–2', '>2'])
h = Y.tday.dt.year <= 2024
out = {}
for b, g in Y.groupby('band', observed=True):
    out[str(b)] = dict(n=len(g), day=g.day.mean(), mon=g.mon.mean(), h1=g.mon[h[g.index]].mean(), h2=g.mon[~h[g.index]].mean(), bysym={s: g.mon[g.sym == s].mean() for s in ('NQ', 'ES', 'RTY')})
    print(f"{b:6s} n {len(g):3d}  by 17:00 {100 * g.day.mean():3.0f}%  by next 11:00 {100 * g.mon.mean():3.0f}%  (2018–24 {100 * g.mon[h[g.index]].mean():.0f}%, 2025–26 {100 * g.mon[~h[g.index]].mean():.0f}%; "
          + ' '.join(f"{s} {100 * g.mon[g.sym == s].mean():.0f}" for s in ('NQ', 'ES', 'RTY')) + ')')
print('all', Y.day.mean(), Y.mon.mean(), 'next session is Monday on', (Y.gapd == 3).mean())
json.dump(out, open('ce_mon.json', 'w'))
