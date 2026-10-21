"""Pre-specified FOMC hypotheses at 13:59 (the user's: the month's premium / discount and distance from the month's open;
plus the size heads HYDRA surfaced). Held = p < 0.05 over 2018–26 and the same side in 2018–24 and 2025–26."""
import numpy as np, pandas as pd, json
from scipy import stats
def load(sym):
    F = pd.read_pickle(f'fomc_{sym}.pkl')
    F['mo3'] = np.where(F.moPos >= 0.75, 'premium', np.where(F.moPos <= 0.25, 'discount', 'middle'))
    F['dmo3'] = np.where(F.dMO > 1, 'over MO >1 ADR', np.where(F.dMO < -1, 'under MO >1 ADR', 'within 1 ADR'))
    F['pd3'] = np.where(F.pdPos > 1, 'above PDH', np.where(F.pdPos < 0, 'below PDL', 'inside PD'))
    F['strong'] = np.where(F.preMove > 0.4, 'up >0.4 ADR since 18:00', np.where(F.preMove < -0.4, 'down >0.4 ADR', 'flat'))
    F['sepm'] = np.where(F.sep == 1, 'SEP meeting', 'no SEP')
    return F
BIN = {'y_s1': 'stage 1 up', 'y_s2': 'stage 2 up', 'y_post': '14:00→16:14 up', 'y_cont': 'stage 2 continues stage 1', 'newHi': 'new day high after 14:00', 'newLo': 'new day low after 14:00', 'y_nAM': 'next NY AM up'}
CON = {'m_s1': '|stage 1|', 'm_s2': '|stage 2|', 'postRng': 'post-14:00 range'}
def test(F, col, val):
    A, B = F[F[col] == val], F[F[col] != val]
    half = lambda X: (X.index.year <= 2024, X.index.year >= 2025)
    rows = []
    for t, lab in {**BIN, **CON}.items():
        a, b = A[t].dropna(), B[t].dropna()
        if len(a) < 6: continue
        if t in BIN:
            d = a.mean() - b.mean(); n1, n0 = len(a), len(b); pp = (a.sum() + b.sum()) / (n1 + n0)
            se = np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n0)); p = 2 * stats.norm.sf(abs(d / se)) if se > 0 else 1
            sides = []
            for m in range(2):
                ah, bh = A[half(A)[m]][t].dropna(), B[half(B)[m]][t].dropna()
                sides.append(np.sign(ah.mean() - bh.mean()) if len(ah) and len(bh) else 0)
            rows.append((lab, len(a), f'{a.mean() * 100:.0f}%', f'{b.mean() * 100:.0f}%', p, all(s == np.sign(d) for s in sides) and p < 0.05, [f'{A[half(A)[m]][t].mean() * 100:.0f}%' if half(A)[m].any() else '—' for m in range(2)]))
        else:
            r = a.median() / b.median(); p = stats.mannwhitneyu(a, b).pvalue
            sides = []
            for m in range(2):
                ah, bh = A[half(A)[m]][t].dropna(), B[half(B)[m]][t].dropna()
                sides.append(np.sign(ah.median() - bh.median()) if len(ah) and len(bh) else 0)
            rows.append((lab, len(a), f'{a.median():.2f}', f'{b.median():.2f}', p, all(s == np.sign(a.median() - b.median()) for s in sides) and p < 0.05, [f'{A[half(A)[m]][t].median():.2f}' if half(A)[m].any() else '—' for m in range(2)]))
    return rows
R = {}
for sym in ('NQ', 'ES'):
    F = load(sym); R[sym] = {}
    print(f'\n================ {sym}: {len(F)} FOMC days 2018–26 (at 13:59)')
    for col, vals in (('mo3', ['premium', 'discount', 'middle']), ('dmo3', ['over MO >1 ADR', 'under MO >1 ADR', 'within 1 ADR']), ('pd3', ['above PDH', 'below PDL']),
                      ('strong', ['up >0.4 ADR since 18:00', 'down >0.4 ADR']), ('sepm', ['SEP meeting'])):
        for v in vals:
            n = (F[col] == v).sum()
            print(f'  {v} (n {n}, {n / len(F) * 100:.0f}% of meetings)')
            for lab, na, va, vb, p, held, halves in test(F, col, v):
                if p < 0.10 or held:
                    print(f'     {"✓" if held else " "} {lab:28s} {va:>6s} vs {vb:>6s} others · p {p:.3f} · 2018–24 {halves[0]} · 2025–26 {halves[1]}')
                R[sym].setdefault(v, []).append(dict(t=lab, n=int(na), v=va, o=vb, p=float(p), held=bool(held), halves=halves))
json.dump(R, open('direct.json', 'w'))
# headline stats per month position: what the stage card will show
for sym in ('NQ', 'ES'):
    F = load(sym)
    print(f'\n{sym} by month position at 13:59 (n · stage1 up · |s1| · stage2 up · |s2| · post range · new low after 14:00)')
    for v in ('discount', 'middle', 'premium'):
        X = F[F.mo3 == v]
        print(f'   {v:9s} n{len(X):3d} · s1 up {X.y_s1.mean() * 100:3.0f}% · |s1| {X.m_s1.median():.2f} · s2 up {X.y_s2.mean() * 100:3.0f}% · |s2| {X.m_s2.median():.2f} · range {X.postRng.median():.2f} · new low {X.newLo.mean() * 100:3.0f}%')
