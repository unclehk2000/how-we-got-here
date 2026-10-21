"""NWOG (last close of the prior week → Sunday 18:00 open) midpoint: touched by the Monday close and by the NFP release,
NFP weeks vs other weeks, NQ + ES + RTY pooled."""
import numpy as np, pandas as pd, json
from common import *
import common as CM
rows = []
NPs = set(CM.NP)
for sym in ('NQ', 'ES', 'RTY'):
    G = CM.days(sym); idx = sorted(G)
    weeks = {}
    for d in idx: weeks.setdefault((d - pd.Timedelta(days=d.dayofweek)), []).append(d)
    wk = sorted(weeks)
    for i in range(1, len(wk)):
        ds = weeks[wk[i]]; prev = weeks[wk[i - 1]]
        g0 = G[prev[-1]]; fc = g0['C'][-1]; g1 = G[ds[0]]; wo = g1['O'][0]
        if abs(wo - fc) <= 0: continue
        ce = (wo + fc) / 2
        nfp = [d for d in ds if d in NPs]
        hiM, loM = g1['H'].max(), g1['L'].min()
        monHit = float(loM <= ce <= hiM)
        if nfp:
            pre = [G[d] for d in ds if d < nfp[0]]
            gN = Day(G[nfp[0]]); h0, l0 = gN.rng(0, M(8, 30))
            hiN = max([x['H'].max() for x in pre] + [h0]); loN = min([x['L'].min() for x in pre] + [l0])
            relHit = float(loN <= ce <= hiN)
        else: relHit = np.nan
        rows.append(dict(sym=sym, wk=wk[i], nfp=bool(nfp), mon=monHit, rel=relHit))
X = pd.DataFrame(rows); X = X[X.wk >= '2018-01-08']
h = X.wk.dt.year <= 2024
for lab, m in (('NFP weeks', X.nfp), ('other weeks', ~X.nfp)):
    print(f"{lab}: n {m.sum()} · CE touched by Monday's close {100 * X.mon[m].mean():.0f}% (2018–24 {100 * X.mon[m & h].mean():.0f}%, 2025–26 {100 * X.mon[m & ~h].mean():.0f}%)" +
          (f" · by the NFP release {100 * X.rel[m].mean():.0f}%" if lab == 'NFP weeks' else '') + ' · ' + ' '.join(f"{s} {100 * X.mon[m & (X.sym == s)].mean():.0f}" for s in ('NQ', 'ES', 'RTY')))
json.dump(dict(mon_nfp=float(X.mon[X.nfp].mean()), mon_oth=float(X.mon[~X.nfp].mean()), rel=float(X.rel[X.nfp].mean()), n=int(X.nfp.sum())), open('nwog_pool.json', 'w'))
