"""Location-scale version: X = median_j + s(context) × U. The stored rows are quantiles of the context-free part
median_j + (X − median_j) / s, so multiplying back by s at run time keeps the bands calibrated overall."""
import numpy as np, pandas as pd, json
from model import long, fit, BLOCKS, FEAT, QA
from stats import NJ
def svec(M, j, Z):
    for name, a, c in BLOCKS:
        if a <= j <= c: return np.exp(Z @ np.asarray(M[name]['b']))
def held_model(MF, MA, MB):
    return {name: {'b': [MF[name]['b'][i] if (MF[name]['p'][i] < 0.05 and np.sign(MA[name]['b'][i]) == np.sign(MF[name]['b'][i]) == np.sign(MB[name]['b'][i])) else 0.0 for i in range(len(FEAT))]} for name, _, _ in BLOCKS}
def base_rows(L, M, col):
    R = np.full((NJ, len(QA)), np.nan)
    for j, g in L.groupby('j'):
        x = g[col].values; ok = np.isfinite(x)
        if ok.sum() < 50: continue
        x = x[ok]; med = np.median(x); s = svec(M, j, g[FEAT].values[ok])
        R[j] = np.quantile(med + (x - med) / s, QA)
    return R
def evaluate(R, M, T, col):
    cov = {k: [0, 0] for k in ('all', 'belowPDL', 'abovePDH', 'belowMO>1.5', 'nearATH')}
    pin = 0.0; n = 0
    for j, g in T.groupby('j'):
        x = g[col].values; ok = np.isfinite(x)
        if np.isnan(R[j]).any() or not ok.any(): continue
        g = g[ok]; x = x[ok]
        q = R[j]; med = np.interp(0.5, QA, q); s = svec(M, j, g[FEAT].values)
        qq = med + (q[None, :] - med) * s[:, None]
        lo, hi = qq[:, 3], qq[:, 19]                                   # 10% and 90% levels
        e = x[:, None] - qq; pin += np.sum(np.maximum(QA * e, (QA - 1) * e)); n += len(x)
        for k, mk in (('all', np.ones(len(g), bool)), ('belowPDL', g.belowPDL.values == 1), ('abovePDH', g.abovePDH.values == 1), ('belowMO>1.5', g.belowMO.values > 1.5), ('nearATH', g.nearATH.values == 1)):
            cov[k][0] += ((x >= lo) & (x <= hi))[mk].sum(); cov[k][1] += mk.sum()
    return {k: round(v[0] / v[1], 3) for k, v in cov.items()}, pin / n
OUT = {}
for sym in ('NQ', 'ES', 'RTY'):
    L = long(sym); A, B = L[L.year <= 2024], L[L.year >= 2025]
    MF, MA, MB = fit(L), fit(A), fit(B)
    H = held_model(MF, MA, MB)
    HA = {name: {'b': [MA[name]['b'][i] if H[name]['b'][i] != 0 else 0.0 for i in range(len(FEAT))]} for name, _, _ in BLOCKS}
    Z = {name: {'b': [0.0] * len(FEAT)} for name, _, _ in BLOCKS}
    print(f'\n{sym}  test 2025–26, rows built on 2018–24 — 80% band coverage and mean pinball loss')
    for col, lab in (('X', 'trading-day close'), ('XR', 'RTH close')):
        c0, p0 = evaluate(base_rows(A, Z, col), Z, B, col)
        c1, p1 = evaluate(base_rows(A, HA, col), HA, B, col)
        print(f'  {lab:17s} no context {c0}  pinball {p0:.4f}')
        print(f'  {"":17s} context    {c1}  pinball {p1:.4f} ({(p1 / p0 - 1) * 100:+.1f}%)')
    OUT[sym] = dict(beta={name: [round(float(x), 4) for x in H[name]['b']] for name, _, _ in BLOCKS},
                    q_TD=np.round(base_rows(L, H, 'X') * 1000).tolist(), q_RTH=np.round(base_rows(L, H, 'XR') * 1000).tolist())
json.dump(dict(blocks=[b[0] for b in BLOCKS], bj=[[b[1], b[2]] for b in BLOCKS], feat=FEAT, sym=OUT), open('ctx_model2.json', 'w'))
