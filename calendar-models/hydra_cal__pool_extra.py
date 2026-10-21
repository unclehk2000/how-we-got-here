"""Pooled NQ + ES + RTY on NFP days: (1) the index against DXY futures in stage 1 / stage 2 (Feb 2023 – Aug 2026), big DXY
move = at least its median; (2) the 08:30–09:00 expansion of the day's range against ordinary days."""
import numpy as np, pandas as pd, json
from scipy import stats
from common import *
import common as CM
exec(open('/home/claude/hm/hydra_fomc/dxy.py').read().split('out = {}')[0].replace("pd.read_pickle(f'fomc_{sym}.pkl')", "None"))
out = {}
rows = []
for sym in ('NQ', 'ES', 'RTY'):
    G = CM.days(sym); D = CM.ctx(sym); T = CM.day_type(D.index)
    for d in D.index:
        if T[d] not in (1, 6) or d not in G: continue
        g = CM.Day(G[d]); A = D.adr.loc[d]
        if not g.full() or not A > 0: continue
        h0, l0 = g.rng(0, CM.M(8, 30)); h1, l1 = g.rng(0, CM.M(9, 0))
        r = dict(tday=d, sym=sym, nfp=T[d] == 1, add=((h1 - l1) - (h0 - l0)) / A)
        if T[d] == 1 and d in DXD and d in dxday.index:
            x = DXD[d]; a20 = dxday.rng20.loc[d]
            for nm, w0, w1 in (('s1', (8, 30), (8, 50)), ('s2', (8, 50), (9, 30))):
                ix = g.c(w1[0], w1[1] - 1) - g.o(*w0); dx = at_close(x, *w1) - at_open(x, *w0)
                r['ix_' + nm], r['dx_' + nm] = ix / A, dx / a20
        rows.append(r)
X = pd.DataFrame(rows)
N = X[X.nfp]; h = N.tday.dt.year <= 2024
for nm, thr_q in (('s1', None), ('s2', None)):
    Y = N.dropna(subset=['ix_' + nm, 'dx_' + nm]); Y = Y[(Y['ix_' + nm] != 0) & (Y['dx_' + nm] != 0)]
    oth = np.sign(Y['ix_' + nm]) != np.sign(Y['dx_' + nm]); thr = Y['dx_' + nm].abs().median(); big = Y['dx_' + nm].abs() >= thr
    hh = Y.tday.dt.year <= 2024
    per = {s: float(oth[big & (Y.sym == s)].mean()) for s in ('NQ', 'ES', 'RTY')}
    # date-clustered test of the big-move other-way rate against 50%: one value per date (mean over symbols)
    byd = oth[big].groupby(Y.tday[big]).mean(); tt = stats.ttest_1samp(byd, 0.5)
    out[nm] = dict(n=int(big.sum()), dates=int(Y.tday[big].nunique()), thr=float(thr), big=float(oth[big].mean()), small=float(oth[~big].mean()), all=float(oth.mean()),
                   h1=float(oth[big & hh].mean()), h2=float(oth[big & ~hh].mean()), p=float(tt.pvalue), per=per)
    print(f"{nm}: big (≥{thr:.2f}) other way {100 * oth[big].mean():.0f}% (n {big.sum()}, {Y.tday[big].nunique()} dates; 2023–24 {100 * oth[big & hh].mean():.0f}%, 2025–26 {100 * oth[big & ~hh].mean():.0f}%; p {tt.pvalue:.4f}) · small {100 * oth[~big].mean():.0f}% · by symbol {per}")
a, b = X[X.nfp]['add'], X[~X.nfp]['add']
hh = X.tday.dt.year <= 2024
out['add'] = dict(nfp=float(a.median()), norm=float(b.median()), nfp_mean=float(a.mean()), norm_mean=float(b.mean()),
                  h=[float(X[X.nfp & hh]['add'].median()), float(X[X.nfp & ~hh]['add'].median())], per={s: float(X[X.nfp & (X.sym == s)]['add'].median()) for s in ('NQ', 'ES', 'RTY')},
                  pern={s: float(X[~X.nfp & (X.sym == s)]['add'].median()) for s in ('NQ', 'ES', 'RTY')}, p=float(stats.mannwhitneyu(a, b).pvalue), n=int(len(a)))
print('08:30–09:00 adds: NFP median', round(a.median(), 3), 'mean', round(a.mean(), 3), '| ordinary median', round(b.median(), 3), 'mean', round(b.mean(), 3), '| halves', [round(x, 3) for x in out['add']['h']], '| by symbol', {k: round(v, 3) for k, v in out['add']['per'].items()})
json.dump(out, open('pool_extra.json', 'w'))
