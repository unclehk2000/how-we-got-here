"""Hollow's card and Shirosaki numbers from NQ + ES + RTY pooled days (each in its own ADR20).  python3 card_pool_ev.py wk|fa
Held (✓): the group differs from the rest with date-clustered p < 0.05, on the same side in 2018–24 and 2025–26, and on the
same side on NQ, ES and RTY. Also the pooled DXY rule (DXY futures, Feb 2023 – Jul 2026)."""
import numpy as np, pandas as pd, json, math, sys
from scipy import stats
EV = sys.argv[1]
sys.argv = ['x', EV]; exec(open('direct_gen.py').read().split('BIN =')[0])       # groups()
F = pd.concat([groups(pd.read_pickle(f'{EV}_{s}.pkl')).assign(sym=s) for s in ('NQ', 'ES', 'RTY')]).reset_index()
dc = pd.factorize(F.tday)[0]
BINS = ('newHi', 'newLo', 'gapFill', 'ce10', 'ce50', 'q4held', 'takeFH', 'takeFL', 'y_am', 'y_rth', 'y_upSide')
def ctest(mask, t):
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
OUT = {'n': len(F), 'dates': int(F.tday.nunique()), 'nsym': {s: int((F.sym == s).sum()) for s in ('NQ', 'ES', 'RTY')}}
Z = ['discount', 'middle', 'premium']
SIZES = {'wk': ['m_am', 'rthRng', 'settleRng', 'nRng'], 'fa': ['m_am', 'rthRng', 'nRng']}[EV]
for t in SIZES:
    OUT[t] = [[float(F[F.mo3 == z][t].median()), float(F[F.mo3 == z][t].quantile(.8)), row('mo3', z, t)] for z in Z]
SETS = {'mo3': Z, 'pd3': ['above PDH', 'inside PD', 'below PDL'], 'strong': ['up >0.4 ADR since 18:00', 'flat', 'down >0.4 ADR'],
        'dmo3': ['over MO >1 ADR', 'within 1 ADR', 'under MO >1 ADR'], 'vix3': ['VIX >10% over its 20d avg', 'VIX near avg', 'VIX >10% under'],
        'gap3': ['gap up >0.25 ADR', 'small gap', 'gap down >0.25 ADR']}
if EV == 'wk': SETS['dow3'] = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
if EV == 'fa': SETS.update(fp3=['FOMC 14:00→16:14 up', 'FOMC 14:00→16:14 down'], fc3=['FOMC closed top quarter', 'FOMC closed middle', 'FOMC closed bottom quarter'])
TS = ['newHi', 'newLo', 'rthRng', 'm_am', 'gapFill', 'ce50', 'q4held', 'y_am', 'y_rth', 'nRng'] + (['ce10', 'settleRng'] if EV == 'wk' else ['takeFH', 'takeFL'])
for col, vals in SETS.items():
    OUT[col] = {v: {t: row(col, v, t) for t in TS} for v in vals}
OUT['all'] = {t: stat(F, t) for t in TS}
# ── pooled DXY: index against DXY futures in the same window (NY AM, RTH)
import common as CM
exec(open('/home/claude/hm/hydra_fomc/dxy.py').read().split('out = {}')[0].replace("pd.read_pickle(f'fomc_{sym}.pkl')", "None"))
R = []
for sym in ('NQ', 'ES', 'RTY'):
    G = CM.days(sym); D = CM.ctx(sym); X = F[F.sym == sym]
    for d in X.tday:
        if d not in DXD or d not in G or d not in dxday.index: continue
        g = CM.Day(G[d]); x = DXD[d]; a20 = dxday.rng20.loc[d]; A = D.adr.loc[d]
        for nm, w0, w1 in (('am', (9, 30), (11, 0)), ('rth', (9, 30), (16, 15))):
            ix = (g.c(w1[0], w1[1] - 1) if w1[1] else g.c(w1[0] - 1, 59)) - g.o(*w0); dx = at_close(x, *w1) - at_open(x, *w0)
            if a20 > 0 and A > 0 and np.isfinite(ix) and np.isfinite(dx) and ix != 0 and dx != 0:
                R.append(dict(sym=sym, tday=d, w=nm, ix=ix / A, dx=dx / a20))
Rd = pd.DataFrame(R); OUT['dxy'] = {}
for nm in ('am', 'rth'):
    Y = Rd[Rd.w == nm].copy(); oth = (np.sign(Y.ix) != np.sign(Y.dx)); thr = float(Y.dx.abs().median()); big = Y.dx.abs() >= thr
    h = Y.tday.dt.year <= 2024
    byd = oth[big].groupby(Y.tday[big]).mean(); tt = stats.ttest_1samp(byd, 0.5)
    OUT['dxy'][nm] = dict(n=int(big.sum()), dates=int(Y.tday[big].nunique()), thr=thr, big=float(oth[big].mean()), small=float(oth[~big].mean()), all=float(oth.mean()),
                          h1=float(oth[big & h].mean()), h2=float(oth[big & ~h].mean()), p=float(tt.pvalue),
                          per={s: float(oth[big & (Y.sym == s)].mean()) for s in ('NQ', 'ES', 'RTY')})
json.dump(OUT, open(f'card_pool_{EV}.json', 'w'), default=float)
fm = lambda t, v: '—' if not np.isfinite(v) else (f'{100 * v:.0f}%' if t in BINS else f'{v:.2f}')
print(f"pooled {EV}: {OUT['n']} symbol-days over {OUT['dates']} dates {OUT['nsym']}")
for t in SIZES:
    print(f'  {t:9s} ' + ' | '.join(f'{a:.2f}/{b:.2f}{"✓" if h["held"] else ""} (p {h["p"]:.3f})' for a, b, h in OUT[t]))
for col in SETS:
    for v, d in OUT[col].items():
        print(f'  {col:6s} {v[:26]:26s} ' + ' '.join(f'{t}={fm(t, x["v"])}{"✓" if x["held"] else ""}' for t, x in d.items()) + f'  (n {d["newHi"]["n"]})')
print('  all:', {k: round(v, 3) for k, v in OUT['all'].items()})
for nm, r in OUT['dxy'].items():
    print(f"  DXY {nm}: big ≥{r['thr']:.2f} other way {100 * r['big']:.0f}% (n {r['n']}, {r['dates']} dates; 23–24 {100 * r['h1']:.0f}%, 25–26 {100 * r['h2']:.0f}%; p {r['p']:.4f}) · small {100 * r['small']:.0f}% · {r['per']}")
