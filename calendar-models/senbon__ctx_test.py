import numpy as np, pandas as pd, json
from scipy import stats as st
MARKS = {'18:00': 0, '09:30': 31, '12:00': 36, '14:00': 40}
def frame(sym):
    D = pd.read_pickle(f'ctx_{sym}.pkl'); D = D[D.full & D.adr.notna() & D.C_TD.notna() & D.PDH.notna()]
    rows = []
    for lab, j in MARKS.items():
        P = np.array([p[j] for p in D.P]); Hj = np.array([h[j] for h in D.Hj]); Lj = np.array([l[j] for l in D.Lj])
        if j == 0: Hj = P.copy(); Lj = P.copy()
        a = D.adr.values
        f = pd.DataFrame(dict(mark=lab, X=(D.C_TD.values - P) / a, pos=np.where(P > D.PDH.values, 'above PDH', np.where(P < D.PDL.values, 'below PDL', 'inside')),
                              dMO=(P - D.MO.values) / a, dATH=(np.maximum(D.ATHp.values, Hj) - P) / a, half=np.where(D.index.year <= 2024, 'A', 'B')), index=D.index)
        rows.append(f)
    F = pd.concat(rows); F = F[np.isfinite(F.X)]
    F['mo'] = pd.cut(F.dMO, [-99, -1.5, -0.5, 0.5, 1.5, 99], labels=['MO < −1.5 ADR', 'MO −1.5…−0.5', 'MO ±0.5', 'MO +0.5…+1.5', 'MO > +1.5 ADR']).astype(str)
    F['ath'] = pd.cut(F.dATH, [-1, 0.5, 2, 5, 999], labels=['ATH ≤ 0.5 ADR', 'ATH 0.5–2', 'ATH 2–5', 'ATH > 5 ADR']).astype(str)
    return F
def test(F, col, val):
    out = {}
    for mark in MARKS:
        G = F[F.mark == mark]; s, r = G[G[col] == val], G[G[col] != val]
        if len(s) < 40: continue
        def stat(a, b):
            med = a.X.median() - b.X.median()
            up = (a.X > 0).mean() - (b.X > 0).mean()
            wid = (a.X.abs().mean() / b.X.abs().mean()) if b.X.abs().mean() > 0 else np.nan
            return med, up, wid
        med, up, wid = stat(s, r)
        p_med = st.mannwhitneyu(s.X, r.X).pvalue
        n1, n0 = len(s), len(r); k1, k0 = (s.X > 0).sum(), (r.X > 0).sum(); pp = (k1 + k0) / (n1 + n0)
        z = ((k1 / n1) - (k0 / n0)) / np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n0)); p_up = 2 * (1 - st.norm.cdf(abs(z)))
        p_wid = st.mannwhitneyu(s.X.abs(), r.X.abs()).pvalue
        halves = {h: stat(s[s.half == h], r[r.half == h]) for h in 'AB'}
        held = lambda i, p, ref: p < 0.05 and all(np.sign(halves[h][i] - ref) == np.sign((med, up, wid)[i] - ref) for h in 'AB')
        out[mark] = dict(n=n1, share=round(n1 / (n1 + n0), 2), med=round(med, 3), up=round(up, 3), wid=round(wid, 2),
                         p_med=p_med, p_up=p_up, p_wid=p_wid,
                         held_med=held(0, p_med, 0), held_up=held(1, p_up, 0), held_wid=held(2, p_wid, 1),
                         halves={h: [round(x, 3) for x in halves[h]] for h in 'AB'})
    return out
R = {}
for sym in ('NQ', 'ES', 'RTY'):
    F = frame(sym); R[sym] = {}
    print(f'\n===== {sym}  (median shift and P(up) shift are vs all other days at that half hour; width = mean |move| ratio)')
    for col, vals in (('pos', ['above PDH', 'below PDL', 'inside']), ('mo', ['MO < −1.5 ADR', 'MO −1.5…−0.5', 'MO ±0.5', 'MO +0.5…+1.5', 'MO > +1.5 ADR']), ('ath', ['ATH ≤ 0.5 ADR', 'ATH 0.5–2', 'ATH 2–5', 'ATH > 5 ADR'])):
        for v in vals:
            o = test(F, col, v); R[sym][v] = o
            cells = []
            for mark, d in o.items():
                flags = ('M' if d['held_med'] else '·') + ('U' if d['held_up'] else '·') + ('W' if d['held_wid'] else '·')
                cells.append(f"{mark} n{d['n']:4d} med{d['med']:+.3f} up{d['up']*100:+5.1f} w×{d['wid']:.2f} {flags}")
            print(f'{v:15s} | ' + ' | '.join(cells))
json.dump(R, open('ctx_tests.json', 'w'), default=float)
