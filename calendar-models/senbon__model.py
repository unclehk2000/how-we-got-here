"""Context scale model: how wide today's close distribution is, given where price sits against the prior day's range,
the month's open and the all-time high. |close − price| ÷ ADR20, divided by its average at that half hour, modelled as
exp(β · context) (Poisson GLM, log link, day-clustered errors), one model per symbol and time block."""
import numpy as np, pandas as pd, json, warnings
import statsmodels.api as sm
from stats import NJ, Q
warnings.filterwarnings('ignore')
QA = np.array(Q)
BLOCKS = [('18:00–03:00', 0, 17), ('03:00–09:30', 18, 30), ('09:30–12:00', 31, 35), ('12:00–17:00', 36, 45)]
FEAT = ['abovePDH', 'belowPDL', 'belowMO', 'aboveMO', 'nearATH']
def long(sym):
    D = pd.read_pickle(f'ctx_{sym}.pkl'); D = D[D.full & D.adr.notna() & D.C_TD.notna() & D.PDH.notna()]
    P = np.vstack(D.P.values); Hj = np.vstack(D.Hj.values); Hj[:, 0] = P[:, 0]; Hj = np.where(np.isnan(Hj), P, Hj)
    a = D.adr.values[:, None]
    X = (D.C_TD.values[:, None] - P) / a
    XR = (D.C_RTH.values[:, None] - P) / a; XR[:, 45:] = np.nan
    dMO = (P - D.MO.values[:, None]) / a
    dATH = (np.maximum(D.ATHp.values[:, None], Hj) - P) / a
    n = len(D)
    L = pd.DataFrame(dict(day=np.repeat(np.arange(n), NJ), date=np.repeat(D.index.values, NJ), j=np.tile(np.arange(NJ), n),
                          X=X.ravel(), XR=XR.ravel(),
                          abovePDH=(P > D.PDH.values[:, None]).ravel().astype(float), belowPDL=(P < D.PDL.values[:, None]).ravel().astype(float),
                          belowMO=np.clip(-dMO, 0, 3).ravel(), aboveMO=np.clip(dMO, 0, 3).ravel(), nearATH=(dATH <= 0.5).ravel().astype(float)))
    L['year'] = pd.DatetimeIndex(L.date).year
    return L[np.isfinite(L.X) & np.isfinite(L[FEAT]).all(axis=1)]
def fit(L, keep=None):
    out = {}
    m = L.groupby('j').X.apply(lambda s: s.abs().mean())
    for name, j0, j1 in BLOCKS:
        G = L[(L.j >= j0) & (L.j <= j1)]
        y = G.X.abs().values / m.reindex(G.j).values
        Xm = sm.add_constant(G[FEAT].values)
        r = sm.GLM(y, Xm, family=sm.families.Poisson()).fit(cov_type='cluster', cov_kwds={'groups': G.day.values})
        out[name] = dict(b=r.params[1:].tolist(), p=r.pvalues[1:].tolist(), c=float(r.params[0]))
    return out
def scale_of(M, j, z):
    for name, j0, j1 in BLOCKS:
        if j0 <= j <= j1: return np.exp(np.asarray(M[name]['b']) @ z)
def qrow(L, col):
    return {j: np.nanquantile(g[col].values, QA) for j, g in L.groupby('j')}
def evaluate(Ltr, Lte, M, col):
    """80% band coverage and mean pinball loss on the test years: unconditional rows vs context-scaled rows"""
    QR = qrow(Ltr, col)
    T = Lte[np.isfinite(Lte[col])]
    res = {'all': [], 'belowPDL': [], 'abovePDH': [], 'belowMO>1.5': [], 'nearATH': []}
    pin0 = pin1 = 0.0; n = 0
    cov = {k: [0, 0, 0] for k in res}
    for j, g in T.groupby('j'):
        q = QR[j]; med = np.interp(0.5, QA, q)
        z = g[FEAT].values
        s = np.exp(z @ np.asarray([M[b]['b'] for b in [nm for nm, a, c in BLOCKS if a <= j <= c]][0]))
        x = g[col].values
        q0 = np.tile(q, (len(g), 1)); q1 = med + (q0 - med) * s[:, None]
        for qq, k in ((q0, 0), (q1, 1)):
            lo, hi = np.interp(0.1, QA, qq[0]) if False else None, None
        lo0, hi0 = np.interp(0.1, QA, q), np.interp(0.9, QA, q)
        lo1, hi1 = med + (lo0 - med) * s, med + (hi0 - med) * s
        masks = {'all': np.ones(len(g), bool), 'belowPDL': g.belowPDL.values == 1, 'abovePDH': g.abovePDH.values == 1,
                 'belowMO>1.5': g.belowMO.values > 1.5, 'nearATH': g.nearATH.values == 1}
        for k, mk in masks.items():
            cov[k][0] += ((x >= lo0) & (x <= hi0))[mk].sum(); cov[k][1] += ((x >= lo1) & (x <= hi1))[mk].sum(); cov[k][2] += mk.sum()
        e0 = x[:, None] - q0; e1 = x[:, None] - q1
        pin0 += np.sum(np.maximum(QA * e0, (QA - 1) * e0)); pin1 += np.sum(np.maximum(QA * e1, (QA - 1) * e1)); n += len(g)
    return {k: (round(v[0] / v[2], 3), round(v[1] / v[2], 3), int(v[2])) for k, v in cov.items()}, round(pin0 / n, 5), round(pin1 / n, 5)
OUT = {}
for sym in ('NQ', 'ES', 'RTY'):
    L = long(sym)
    A, B = L[L.year <= 2024], L[L.year >= 2025]
    MA, MB, MF = fit(A), fit(B), fit(L)
    # held: p < 0.05 on the full sample and the same sign when fitted on 2018–24 and on 2025–26 alone
    MH = {}
    print(f'\n===== {sym}: width multipliers exp(β) per unit (dummies: on vs off; MO distances: per ADR, capped at 3)')
    for name, j0, j1 in BLOCKS:
        b = []
        cells = []
        for i, f in enumerate(FEAT):
            bf, pf_ = MF[name]['b'][i], MF[name]['p'][i]
            held = pf_ < 0.05 and np.sign(MA[name]['b'][i]) == np.sign(bf) == np.sign(MB[name]['b'][i])
            b.append(bf if held else 0.0)
            cells.append(f"{f} ×{np.exp(bf):.2f}{'✓' if held else ' '} (A ×{np.exp(MA[name]['b'][i]):.2f} B ×{np.exp(MB[name]['b'][i]):.2f} p{pf_:.3f})")
        MH[name] = {'b': b}
        print(f'  {name}: ' + ' | '.join(cells))
    # out-of-sample: fit the held model on 2018–24 only, test on 2025–26
    MAh = {name: {'b': [MA[name]['b'][i] if MH[name]['b'][i] != 0 else 0.0 for i in range(len(FEAT))]} for name, _, _ in BLOCKS}
    for col in ('X', 'XR'):
        cov, p0, p1 = evaluate(A, B, MAh, col)
        print(f'  test 2025–26 ({"trading-day" if col == "X" else "RTH"} close): 80% band coverage unconditional → with context:', {k: f'{v[0]:.3f}→{v[1]:.3f} (n{v[2]})' for k, v in cov.items()}, f'| pinball {p0} → {p1} ({(p1 / p0 - 1) * 100:+.1f}%)')
    OUT[sym] = {name: [round(float(x), 4) for x in MH[name]['b']] for name, _, _ in BLOCKS}
json.dump(dict(blocks=BLOCKS, feat=FEAT, beta=OUT), open('ctx_model.json', 'w'))
print(json.dumps(OUT))
