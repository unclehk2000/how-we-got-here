import numpy as np, pandas as pd, json
from stats import Q, NJ
from scipy import stats as st
QA = np.array(Q)
def X(D, tgt):
    P = np.vstack(D.P.values)                                      # days × NJ
    C = D[tgt].values[:, None]
    x = (C - P) / D.adr.values[:, None]
    if tgt == 'C_RTH': x[:, 45:] = np.nan                          # 16:30 is after the RTH close
    return x
def qtab(x):
    return np.array([np.nanquantile(x[:, j], QA) if np.isfinite(x[:, j]).sum() > 50 else np.full(len(QA), np.nan) for j in range(NJ)])
def cdf(qrow, v):
    """empirical CDF from the quantile row by linear interpolation, flat 1% / 99% tails extended linearly"""
    return np.interp(v, qrow, QA, left=0.0, right=1.0)
def coverage(qt, x, lv):
    lo, hi = (1 - lv) / 2, 1 - (1 - lv) / 2
    hits, n = 0, 0
    for j in range(NJ):
        if np.isnan(qt[j]).any(): continue
        a, b = np.interp([lo, hi], QA, qt[j])
        v = x[:, j]; v = v[np.isfinite(v)]
        hits += ((v >= a) & (v <= b)).sum(); n += len(v)
    return hits / n
res = {}
vix = pd.read_csv('/home/claude/mac/vix_daily.csv', parse_dates=['DATE']).set_index('DATE').CLOSE
for s in ('NQ', 'ES', 'RTY'):
    D = pd.read_pickle(f'days_{s}.pkl'); D = D[D.full & D.adr.notna() & D.C_TD.notna()]
    tr, te = D[D.index.year <= 2024], D[D.index.year >= 2025]
    r = {'n': len(D), 'n_train': len(tr), 'n_test': len(te)}
    for tgt in ('C_TD', 'C_RTH'):
        xa, xtr, xte = X(D, tgt), X(tr, tgt), X(te, tgt)
        qa, qtr = qtab(xa), qtab(xtr)
        r[tgt] = dict(q=np.round(qa * 1000).astype('float').tolist(),
                      cov_in={lv: round(coverage(qtr, xtr, lv), 3) for lv in (0.5, 0.8, 0.9, 0.98)},
                      cov_out={lv: round(coverage(qtr, xte, lv), 3) for lv in (0.5, 0.8, 0.9, 0.98)})
        # share of the full trading day's variance still ahead (returns, squared, mean), for the implied curve
        P = np.vstack(D.P.values); C = D[tgt].values[:, None]
        ret = (C - P) / P
        if tgt == 'C_RTH': ret[:, 45:] = np.nan
        base = np.nanmean(((D.C_TD.values - P[:, 0]) / P[:, 0]) ** 2)
        r[tgt]['f'] = np.round(np.nanmean(ret ** 2, axis=0) / base * 1000).tolist()
        # shape: excess kurtosis at 18:00, 09:30, 14:00
        r[tgt]['kurt'] = {lab: round(float(st.kurtosis(xa[:, j][np.isfinite(xa[:, j])])), 2) for lab, j in (('18:00', 0), ('09:30', 31), ('14:00', 40))}
        r[tgt]['skew'] = {lab: round(float(st.skew(xa[:, j][np.isfinite(xa[:, j])])), 2) for lab, j in (('18:00', 0), ('09:30', 31), ('14:00', 40))}
    # VIX-implied (lognormal, 1-day σ = VIX/√252, spread through the day by the variance share) on ES only
    if s == 'ES':
        V = vix.shift(1).reindex(D.index, method='ffill')            # prior VIX close, known at the 18:00 open
        P = np.vstack(D.P.values); C = D.C_TD.values[:, None]
        f = np.array(r['C_TD']['f']) / 1000
        sig = (V.values[:, None] / 100 / np.sqrt(252)) * np.sqrt(f[None, :])
        z = np.log(C / P) / sig
        ok = np.isfinite(z)
        r['vix'] = {}
        for lv in (0.5, 0.8, 0.9, 0.98):
            zc = st.norm.ppf(1 - (1 - lv) / 2)
            r['vix'][lv] = dict(all=round(float((np.abs(z[ok]) <= zc).mean()), 3),
                                y2025=round(float((np.abs(z[ok & np.asarray(D.index.year >= 2025)[:, None]]) <= zc).mean()), 3))
        # width: implied 80% band ÷ historical 80% band, at 18:00 / 09:30 / 14:00
        qa = np.array(r['C_TD']['q']) / 1000
        adrp = (D.adr / D.O).median()
        w = {}
        for lab, j in (('18:00', 0), ('09:30', 31), ('14:00', 40)):
            hist = (np.interp(0.9, QA, qa[j]) - np.interp(0.1, QA, qa[j])) * adrp
            impl = 2 * 1.2816 * (V.median() / 100 / np.sqrt(252)) * np.sqrt(f[j])
            w[lab] = round(float(impl / hist), 2)
        r['vix']['width_ratio_80'] = w
    res[s] = r
    print(s, 'days', r['n'], '| trading-day close: in', r['C_TD']['cov_in'], 'out', r['C_TD']['cov_out'])
    print('   ', ' RTH close:        in', r['C_RTH']['cov_in'], 'out', r['C_RTH']['cov_out'])
    print('    kurt', r['C_TD']['kurt'], 'skew', r['C_TD']['skew'])
    print('    f (TD) at 18:00/03:00/09:30/12:00/14:00/16:00:', [r['C_TD']['f'][j] for j in (0, 18, 31, 36, 40, 44)])
    print('    median / 10% / 90% at 18:00 (ADR ×1000):', r['C_TD']['q'][0][11], r['C_TD']['q'][0][3], r['C_TD']['q'][0][19], '| at 14:00:', r['C_TD']['q'][40][11], r['C_TD']['q'][40][3], r['C_TD']['q'][40][19])
    if 'vix' in r: print('    VIX-implied coverage', r['vix'])
json.dump(res, open('dist.json', 'w'))
