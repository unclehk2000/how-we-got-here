"""Every number the Cero and Hollow stages cards show, computed the way the cards group days, with the held test
(group vs the rest of the event's days: p < 0.05 over 2018–26, same side in 2018–24 and 2025–26)."""
import numpy as np, pandas as pd, json, sys
from scipy import stats
sys.argv = ['x', 'nfp']; exec(open('direct_gen.py').read().split('BIN =')[0])       # groups()
def held_test(F, mask, t, binary):
    A, B = F[mask][t].dropna(), F[~mask][t].dropna()
    if len(A) < 6 or len(B) < 6: return dict(p=1.0, held=False, v=np.nan, o=np.nan, h=[np.nan] * 4, n=len(A), nt=0)
    hA, hB = A.index.year <= 2024, B.index.year <= 2024
    f = (lambda s: s.mean()) if binary else (lambda s: s.median())
    d = f(A) - f(B)
    if binary:
        n1, n0 = len(A), len(B); pp = (A.sum() + B.sum()) / (n1 + n0); se = np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n0))
        p = 2 * stats.norm.sf(abs(d / se)) if se > 0 else 1.0
    else: p = stats.mannwhitneyu(A, B).pvalue
    hv = [f(A[hA]) if hA.any() else np.nan, f(B[hB]) if hB.any() else np.nan, f(A[~hA]) if (~hA).any() else np.nan, f(B[~hB]) if (~hB).any() else np.nan]
    same = all(np.isfinite(x) for x in hv) and np.sign(hv[0] - hv[1]) == np.sign(d) and np.sign(hv[2] - hv[3]) == np.sign(d)
    return dict(p=float(p), held=bool(same and p < 0.05), v=float(f(A)), o=float(f(B)), h=[float(x) for x in hv], n=int(len(A)), nt=int((~hA).sum()))
OUT = {}
for ev in ('nfp', 'wk', 'fa'):
    EV = ev
    for sym in ('NQ', 'ES'):
        F = groups(pd.read_pickle(f'{ev}_{sym}.pkl')); R = {'n': len(F)}
        Z = ['discount', 'middle', 'premium']
        sizes = {'nfp': ['m_s1', 'm_s2', 'm_am', 'postRng', 'nRng'], 'wk': ['m_am', 'rthRng', 'settleRng', 'nRng'], 'fa': ['m_am', 'rthRng', 'nRng']}[ev]
        for t in sizes:
            R[t] = [[float(F[F.mo3 == z][t].median()), float(F[F.mo3 == z][t].quantile(.8)), held_test(F, F.mo3 == z, t, False)] for z in Z]
            R[t + '_all'] = [float(F[t].median()), float(F[t].quantile(.8))]
        R['zone_n'] = [int((F.mo3 == z).sum()) for z in Z]
        sets = {'pd3': ['above PDH', 'inside PD', 'below PDL'], 'strong': ['up >0.4 ADR since 18:00', 'flat', 'down >0.4 ADR'], 'mo3': Z, 'dmo3': ['over MO >1 ADR', 'within 1 ADR', 'under MO >1 ADR'],
                'vix3': ['VIX >10% over its 20d avg', 'VIX near avg', 'VIX >10% under']}
        if ev == 'nfp': sets['wk3'] = ['week up >0.5 ADR into NFP', 'week flat', 'week down >0.5 ADR']
        if ev in ('wk', 'fa'): sets['gap3'] = ['gap up >0.25 ADR', 'small gap', 'gap down >0.25 ADR']
        if ev == 'wk': sets['dow3'] = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
        tg = {'nfp': ['newHi', 'newLo', 'firstWon', 'y_againstWk', 'y_cont', 'y_nAM', 'y_am', 'postRng', 'nRng', 'm_am'],
              'wk': ['newHi', 'newLo', 'gapFill', 'ce10', 'ce50', 'q4held', 'y_amCont', 'rthRng', 'm_am', 'settleRng', 'nRng'],
              'fa': ['newHi', 'newLo', 'takeFH', 'takeFL', 'gapFill', 'ce50', 'q4held', 'y_contF', 'rthRng', 'm_am', 'nRng']}[ev]
        for col, vals in sets.items():
            R[col] = {}
            for v in vals:
                R[col][v] = {t: held_test(F, F[col] == v, t, not (t.startswith('m_') or t.endswith('Rng'))) for t in tg}
        for t in tg: R['all_' + t] = float(F[t].mean()) if not (t.startswith('m_') or t.endswith('Rng')) else float(F[t].median())
        OUT.setdefault(ev, {})[sym] = R
json.dump(OUT, open('card_stats.json', 'w'), default=float)
# a compact print of what the cards will show
def pc(v): return '—' if not np.isfinite(v) else f'{100 * v:.0f}'
for ev in OUT:
    for sym in OUT[ev]:
        R = OUT[ev][sym]; print(f'\n=== {ev} {sym} n {R["n"]} · zones n {R["zone_n"]}')
        for t in [k for k in R if not k.endswith('_all') and isinstance(R[k], list) and k != 'zone_n']:
            print(f'  {t:9s} ' + ' | '.join(f'{a:.2f}/{b:.2f}{"✓" if h["held"] else ""}' for a, b, h in R[t]) + f'   all {R[t + "_all"][0]:.2f}/{R[t + "_all"][1]:.2f}')
        for col in [k for k in R if isinstance(R[k], dict)]:
            for v, d in R[col].items():
                hs = ' '.join(f'{t}={pc(x["v"]) if not (t.startswith("m_") or t.endswith("Rng")) else f"{x[chr(118)]:.2f}"}{"✓" if x["held"] else ""}(n{x["n"]})' for t, x in d.items() if t in ('newHi', 'newLo', 'gapFill', 'ce10', 'q4held', 'takeFH', 'takeFL', 'postRng', 'rthRng', 'firstWon', 'y_againstWk'))
                print(f'  {col:6s} {v[:24]:24s} {hs}')
