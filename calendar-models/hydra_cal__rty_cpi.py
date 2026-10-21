"""Does the Russell react more to CPI? CPI days vs ordinary days (Vizard type 6), NQ / ES / RTY, 2018–26: the 08:30–09:00 range
expansion and the day's range in each market's own ADR20, and RTY's return against NQ and ES from 08:29 to the 16:14 close."""
import numpy as np, pandas as pd
from scipy import stats
from common import *
R = {}
for sym in ('NQ', 'ES', 'RTY'):
    G = days(sym); D = ctx(sym); T = day_type(D.index); rows = []
    for i, d in enumerate(D.index):
        if i < 25 or d not in G or T[d] not in (2, 6): continue
        g = Day(G[d]); A = D.adr.iloc[i]
        if not g.full() or not A > 0: continue
        c829, c1614 = g.c(8, 29), g.c(16, 14)
        h0, l0 = g.rng(0, M(8, 30)); h1, l1 = g.rng(0, M(9, 0))
        rows.append(dict(tday=d, cpi=T[d] == 2, exp=((h1 - l1) - (h0 - l0)) / A, rng=(D.H.iloc[i] - D.L.iloc[i]) / A, ret=(c1614 / c829 - 1) * 100))
    R[sym] = pd.DataFrame(rows).set_index('tday')
X = pd.concat({s: R[s] for s in R}, axis=1).dropna()
print(f'days with all three: {len(X)} (CPI {int(X[("NQ", "cpi")].sum())})')
cpi = X[('NQ', 'cpi')].astype(bool); h = X.index.year <= 2024
print('\n08:30–09:00 range expansion (ADR, mean) · CPI vs ordinary · ratio')
for s in ('NQ', 'ES', 'RTY'):
    a, b = X[(s, 'exp')][cpi], X[(s, 'exp')][~cpi]
    print(f'  {s:3s} CPI {a.mean():.3f} vs {b.mean():.3f} → ×{a.mean() / b.mean():.1f} · day range CPI {X[(s, "rng")][cpi].median():.2f} vs {X[(s, "rng")][~cpi].median():.2f} ADR (×{X[(s, "rng")][cpi].median() / X[(s, "rng")][~cpi].median():.2f})')
for o in ('NQ', 'ES'):
    d = X[('RTY', 'ret')] - X[(o, 'ret')]
    a, b = d[cpi], d[~cpi]
    p = stats.mannwhitneyu(a, b).pvalue
    print(f'\nRTY − {o}, 08:29 → 16:14 return (%): CPI mean {a.mean():+.3f} (median {a.median():+.3f}, RTY ahead {100 * (a > 0).mean():.0f}%) vs ordinary {b.mean():+.3f} ({100 * (b > 0).mean():.0f}%) · p {p:.3f}'
          f' · 2018–24 {d[cpi & h].mean():+.3f} vs {d[~cpi & h].mean():+.3f} · 2025–26 {d[cpi & ~h].mean():+.3f} vs {d[~cpi & ~h].mean():+.3f}')
    # when CPI day is up / down for NQ: does RTY move more (beta)?
    for lab, m in (('NQ up 08:29→16:14', X[('NQ', 'ret')] > 0), ('NQ down', X[('NQ', 'ret')] < 0)):
        print(f'   {lab:18s} CPI {d[cpi & m].mean():+.3f} (n {int((cpi & m).sum())}) vs ordinary {d[~cpi & m].mean():+.3f}')
# RTY's own sensitivity: |return| per ADR% on CPI vs ordinary, relative to NQ
for s in ('NQ', 'ES', 'RTY'):
    a, b = X[(s, 'ret')][cpi].abs(), X[(s, 'ret')][~cpi].abs()
    print(f'  |ret| {s}: CPI {a.median():.2f}% vs {b.median():.2f}% → ×{a.median() / b.median():.2f}')
