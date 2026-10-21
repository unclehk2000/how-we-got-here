"""Pre-specified groups at the snapshot (the month's premium / discount and distance from the month's open, the prior day,
a strong run into the snapshot, and each event's own groups). Held = p < 0.05 over 2018–26 and the same side in 2018–24 and
2025–26 (group vs the rest of the event's days).   python3 direct_gen.py nfp|wk|fa"""
import numpy as np, pandas as pd, json, sys
from scipy import stats
EV = sys.argv[1]
def groups(F):
    F = F.copy()
    F['mo3'] = np.where(F.moPos >= 0.75, 'premium', np.where(F.moPos <= 0.25, 'discount', 'middle'))
    F['dmo3'] = np.where(F.dMO > 1, 'over MO >1 ADR', np.where(F.dMO < -1, 'under MO >1 ADR', 'within 1 ADR'))
    F['pd3'] = np.where(F.pdPos > 1, 'above PDH', np.where(F.pdPos < 0, 'below PDL', 'inside PD'))
    mv = F.preMove if 'preMove' in F else F.onMove
    F['strong'] = np.where(mv > 0.4, 'up >0.4 ADR since 18:00', np.where(mv < -0.4, 'down >0.4 ADR', 'flat'))
    F['vix3'] = np.where(F.vixRel > 0.1, 'VIX >10% over its 20d avg', np.where(F.vixRel < -0.1, 'VIX >10% under', 'VIX near avg'))
    if EV == 'nfp':
        F['wk3'] = np.where(F.wkMove > 0.5, 'week up >0.5 ADR into NFP', np.where(F.wkMove < -0.5, 'week down >0.5 ADR', 'week flat'))
        F['dr3'] = np.where(F.drPos >= 0.75, 'top of 07:00 range', np.where(F.drPos <= 0.25, 'bottom of 07:00 range', 'mid 07:00 range'))
    if EV in ('wk', 'fa'):
        F['gap3'] = np.where(F.gap > 0.25, 'gap up >0.25 ADR', np.where(F.gap < -0.25, 'gap down >0.25 ADR', 'small gap'))
    if EV == 'wk':
        F['dow3'] = F.dow.map({0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday'})
    if EV == 'fa':
        F['fp3'] = np.where(F.fPost > 0, 'FOMC 14:00→16:14 up', 'FOMC 14:00→16:14 down')
        F['fr3'] = np.where(F.fRng > F.fRng.median(), 'FOMC day range above median', 'FOMC range below median')
        F['fc3'] = np.where(F.fClosePos >= 0.75, 'FOMC closed top quarter', np.where(F.fClosePos <= 0.25, 'FOMC closed bottom quarter', 'FOMC closed middle'))
    return F
BIN = {'nfp': ['y_s1', 'y_s2', 'y_am', 'y_rth', 'y_post', 'y_cont', 'y_againstWk', 'y_upSide', 'firstWon', 'newHi', 'newLo', 'drHi', 'drLo', 'y_nAM'],
       'wk': ['y_am', 'y_rth', 'y_amCont', 'y_upSide', 'newHi', 'newLo', 'gapFill', 'ce10', 'ce50', 'q4held', 'y_settle'],
       'fa': ['y_am', 'y_rth', 'y_contF', 'y_contS2', 'y_upSide', 'newHi', 'newLo', 'takeFH', 'takeFL', 'gapFill', 'ce50', 'q4held']}[EV]
CON = {'nfp': ['m_s1', 'm_s2', 'm_am', 'postRng', 'nRng'], 'wk': ['m_am', 'rthRng', 'settleRng', 'nRng'], 'fa': ['m_am', 'rthRng', 'nRng']}[EV]
GRP = ['mo3', 'dmo3', 'pd3', 'strong', 'vix3'] + {'nfp': ['wk3', 'dr3'], 'wk': ['gap3', 'dow3'], 'fa': ['gap3', 'fp3', 'fr3', 'fc3']}[EV]
def test(F, col, val, t):
    A, B = F[F[col] == val], F[F[col] != val]
    a, b = A[t].dropna(), B[t].dropna()
    if len(a) < 6 or len(b) < 6: return None
    hA, hB = A.index.year <= 2024, B.index.year <= 2024
    if t in BIN:
        d = a.mean() - b.mean(); n1, n0 = len(a), len(b); pp = (a.sum() + b.sum()) / (n1 + n0)
        se = np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n0)); p = 2 * stats.norm.sf(abs(d / se)) if se > 0 else 1.0
        f = lambda s: s.mean()
    else:
        d = a.median() - b.median(); p = stats.mannwhitneyu(a, b).pvalue; f = lambda s: s.median()
    halves = [(f(A[t][hA].dropna()) if hA.any() else np.nan, f(B[t][hB].dropna()) if hB.any() else np.nan),
              (f(A[t][~hA].dropna()) if (~hA).any() else np.nan, f(B[t][~hB].dropna()) if (~hB).any() else np.nan)]
    same = all(np.sign(x - y) == np.sign(d) for x, y in halves if np.isfinite(x) and np.isfinite(y)) and all(np.isfinite(x) and np.isfinite(y) for x, y in halves)
    return dict(n=len(a), nt=int((~hA).sum()), v=float(f(a)), o=float(f(b)), p=float(p), held=bool(same and p < 0.05), halves=[[float(x), float(y)] for x, y in halves])
R = {}
for sym in ('NQ', 'ES'):
    F = groups(pd.read_pickle(f'{EV}_{sym}.pkl')); R[sym] = {}
    print(f'\n================ {EV} · {sym}: {len(F)} days 2018–26')
    for col in GRP:
        for val in sorted(F[col].dropna().unique()):
            n = (F[col] == val).sum(); R[sym][val] = {}
            lines = []
            for t in BIN + CON:
                r = test(F, col, val, t)
                if r is None: continue
                R[sym][val][t] = r
                if r['p'] < 0.10:
                    fm = (lambda v: f'{100 * v:.0f}%') if t in BIN else (lambda v: f'{v:.2f}')
                    lines.append(f'     {"✓" if r["held"] else " "} {t:12s} {fm(r["v"]):>6s} vs {fm(r["o"]):>6s} · p {r["p"]:.3f} · 2018–24 {fm(r["halves"][0][0])} vs {fm(r["halves"][0][1])} · 2025–26 {fm(r["halves"][1][0])} vs {fm(r["halves"][1][1])} (n {r["nt"]})')
            print(f'  {val} (n {n})'); print('\n'.join(lines)) if lines else None
json.dump(R, open(f'direct_{EV}.json', 'w'))
