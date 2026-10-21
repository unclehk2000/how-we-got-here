"""Desgarrón's card and pane numbers from NQ + ES + RTY pooled NFP days (each in its own ADR20). Held (✓): the group differs
from the rest with date-clustered p < 0.05, on the same side in 2018–24 and 2025–26, and on the same side on NQ, ES and RTY."""
import numpy as np, pandas as pd, json, math, sys
from scipy import stats
sys.argv = ['x', 'nfp']; exec(open('direct_gen.py').read().split('BIN =')[0])       # groups()
F = pd.concat([groups(pd.read_pickle(f'nfp_{s}.pkl')).assign(sym=s) for s in ('NQ', 'ES', 'RTY')]).reset_index()
F['oct'] = np.minimum(8, np.floor(F.moPos * 8) + 1)
F['ce4'] = pd.cut(F.ceDist, [0, 0.5, 1, 2, 99], labels=['≤0.5', '0.5–1', '1–2', '>2'])
F['ath3'] = np.where(F.athDist <= 1, 'within 1 ADR of ATH', np.where(F.athDist <= 3, '1–3 ADR below ATH', 'over 3 ADR below ATH'))
dc = pd.factorize(F.tday)[0]
BINS = ('newHi', 'newLo', 'firstWon', 'y_againstWk', 'y_cont', 'y_nAM', 'y_am', 'y_post', 'ceDay', 'athRTH')
def ctest(mask, t):
    """group vs rest: difference in mean (rates) via clustered OLS on a dummy; for sizes, the same on ranks (robust)"""
    y = F[t].values.astype(float); x = mask.astype(float); ok = ~np.isnan(y)
    if t not in BINS: y = pd.Series(y).rank().values
    y, x, g = y[ok], x[ok], dc[ok]; G = len(np.unique(g))
    if x.sum() < 6 or (1 - x).sum() < 6: return 1.0
    xc = x - x.mean(); yc = y - y.mean(); b = (xc * yc).sum() / (xc ** 2).sum(); e = yc - b * xc
    sc = pd.Series(xc * e).groupby(g).sum().values; se = math.sqrt((sc ** 2).sum() * G / (G - 1)) / (xc ** 2).sum()
    return 2 * stats.t.sf(abs(b / se), G - 1) if se > 0 else 1.0
def stat(sub, t): s = sub[t].dropna(); return float(s.mean()) if t in BINS else float(s.median())
def row(col, val, t):
    m = (F[col] == val).values; A, B = F[m], F[~m]
    if A[t].notna().sum() < 6: return dict(v=np.nan, o=np.nan, n=int(A[t].notna().sum()), held=False, p=1.0)
    v, o = stat(A, t), stat(B, t); d = np.sign(v - o); p = ctest(m, t)
    tr = A.tday.dt.year <= 2024; trB = B.tday.dt.year <= 2024
    halves = [(stat(A[tr], t), stat(B[trB], t)), (stat(A[~tr], t), stat(B[~trB], t))]
    bysym = [(stat(A[A.sym == s], t), stat(B[B.sym == s], t)) for s in ('NQ', 'ES', 'RTY')]
    same = all(np.isfinite(a) and np.isfinite(b) and np.sign(a - b) == d for a, b in halves + bysym)
    return dict(v=v, o=o, n=int(A[t].notna().sum()), nd=int(A.tday.nunique()), p=float(p), held=bool(same and p < 0.05), halves=halves, bysym=bysym)
OUT = {'n': len(F), 'dates': int(F.tday.nunique())}
Z = ['discount', 'middle', 'premium']
for t in ('m_s1', 'm_s2', 'm_am', 'postRng', 'nRng'):
    OUT[t] = [[float(F[F.mo3 == z][t].median()), float(F[F.mo3 == z][t].quantile(.8)), row('mo3', z, t)] for z in Z]
SETS = {'mo3': Z, 'pd3': ['above PDH', 'inside PD', 'below PDL'], 'strong': ['up >0.4 ADR since 18:00', 'flat', 'down >0.4 ADR'],
        'dmo3': ['over MO >1 ADR', 'within 1 ADR', 'under MO >1 ADR'], 'vix3': ['VIX >10% over its 20d avg', 'VIX near avg', 'VIX >10% under'],
        'wk3': ['week up >0.5 ADR into NFP', 'week flat', 'week down >0.5 ADR'], 'ath3': ['within 1 ADR of ATH', '1–3 ADR below ATH', 'over 3 ADR below ATH']}
for col, vals in SETS.items():
    OUT[col] = {v: {t: row(col, v, t) for t in ('newHi', 'newLo', 'postRng', 'm_am', 'y_post', 'y_am', 'firstWon', 'ceDay', 'nRng', 'y_againstWk')} for v in vals}
OUT['oct'] = {int(o): dict(n=int((F.oct == o).sum()), postRng=float(F[F.oct == o].postRng.median()), newHi=float(F[F.oct == o].newHi.mean()), newLo=float(F[F.oct == o].newLo.mean()),
                           y_post=float(F[F.oct == o].y_post.mean()), m_am=float(F[F.oct == o].m_am.median())) for o in range(1, 9)}
OUT['ce4'] = {str(k): dict(n=int((F.ce4 == k).sum()), ceDay=float(F[F.ce4 == k].ceDay.mean()), ceRTH=float(F[F.ce4 == k].ceRTH.mean()),
                           bysym=[float(F[(F.ce4 == k) & (F.sym == s)].ceDay.mean()) for s in ('NQ', 'ES', 'RTY')]) for k in ['≤0.5', '0.5–1', '1–2', '>2']}
OUT['all'] = {t: stat(F, t) for t in ('newHi', 'newLo', 'postRng', 'm_am', 'y_post', 'ceDay', 'athRTH', 'firstWon', 'nRng')}
json.dump(OUT, open('card_pool.json', 'w'), default=float)
fm = lambda t, v: '—' if not np.isfinite(v) else (f'{100 * v:.0f}%' if t in BINS else f'{v:.2f}')
print(f"pooled NFP: {OUT['n']} symbol-days over {OUT['dates']} dates")
for t in ('m_s1', 'm_s2', 'm_am', 'postRng', 'nRng'):
    print(f'  {t:8s} ' + ' | '.join(f'{a:.2f}/{b:.2f}{"✓" if h["held"] else ""} (p {h["p"]:.3f})' for a, b, h in OUT[t]))
for col in SETS:
    for v, d in OUT[col].items():
        print(f'  {col:5s} {v[:26]:26s} ' + ' '.join(f'{t}={fm(t, x["v"])}{"✓" if x["held"] else ""}' for t, x in d.items() if t in ('newHi', 'newLo', 'postRng', 'y_post', 'firstWon', 'ceDay')) + f'  (n {d["newHi"]["n"]})')
print('  octant:', {k: (v['n'], round(v['postRng'], 2), round(v['newHi'] * 100), round(v['newLo'] * 100), round(v['y_post'] * 100)) for k, v in OUT['oct'].items()})
print('  CE touch by 17:00 by distance:', {k: (v['n'], round(100 * v['ceDay']), [round(100 * x) for x in v['bysym']]) for k, v in OUT['ce4'].items()})
print('  all:', {k: round(v, 3) for k, v in OUT['all'].items()})
