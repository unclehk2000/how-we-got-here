"""RTY 1-minute: do the pooled NQ + ES constants transfer? (train 2018–24, test 2025–26, full trading day)
1. Live projection weights: NQ+ES (v12) vs RTY's own vs pooled NQ+ES+RTY, on RTY and on NQ / ES.
2. Variance still to come (VREM) and kappa for the 'high / low already in' chance: NQ+ES vs RTY's own.
3. Brier skill of the high / low-in chance on RTY at every half-hour."""
import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
from common import *
from scipy.stats import norm
from statsmodels.regression.quantile_regression import QuantReg
Q = (0.10, 0.25, 0.5, 0.75, 0.90)
A = {s: prep(s) for s in ['NQ', 'ES', 'RTY']}
tr = lambda S: S[S.index.year <= 2024]; te = lambda S: S[S.index.year >= 2025]
def xy(S, i):
    lrun = np.log(S[f'r{i}'].clip(lower=1e-4)); proj = lrun - S[f'sh{i}']
    return pd.DataFrame({'c': 1.0, 'gap': S.har - proj}), S.lf - proj, proj, lrun
def fitq(S, i):
    X, y, _, _ = xy(S, i); out = {}
    for q in Q:
        try: par = QuantReg(y, X).fit(q=q, max_iter=5000).params.values
        except Exception: par = None
        if par is None or abs((y <= X.values @ par).mean() - q) > 0.03 or par[1] < -0.05: par = np.array([np.quantile(y, q), 0.0])
        out[q] = par
    return out
def pred(S, i, par):
    X, _, proj, lrun = xy(S, i); return {q: np.maximum(proj + X.values @ par[q], lrun) for q in Q}
# ── 1. projection weights
fits = {'NQ+ES': pd.concat([tr(A['NQ']), tr(A['ES'])]), 'RTY own': tr(A['RTY']), 'NQ+ES+RTY': pd.concat([tr(A[s]) for s in A])}
rows = []
for i in range(23):
    pars = {k: fitq(v, i) for k, v in fits.items()}
    for tgt in A:
        T = te(A[tgt])
        for k, par in pars.items():
            p = pred(T, i, par)
            rows.append(dict(slot=i, tgt=tgt, fit=k, mae=(T.lf - p[0.5]).abs().mean(),
                             c50=((T.lf >= p[0.25]) & (T.lf <= p[0.75])).mean(), c80=((T.lf >= p[0.10]) & (T.lf <= p[0.90])).mean()))
R = pd.DataFrame(rows)
def base_err(S):
    b = np.log(S.final.rolling(30).median().shift(1)); c = (S.lf - b)[S.index.year <= 2024].median()
    hc = (S.lf - S.har)[S.index.year <= 2024].median(); t = S.index.year >= 2025
    return (S.lf - b - c)[t].abs().mean(), (S.lf - S.har - hc)[t].abs().mean()
print('1. LIVE PROJECTION · test 2025–26 · MAE of log final range, mean over the 23 hourly checkpoints (P25–75 / P10–90 coverage)')
for tgt in A:
    bt, bh = base_err(A[tgt]); x = R[R.tgt == tgt].groupby('fit')[['mae', 'c50', 'c80']].mean()
    print(f'  {tgt} ({len(te(A[tgt]))} test days · typical day {bt:.3f} · expected range alone {bh:.3f}): ' +
          ' · '.join(f'{k} {x.loc[k, "mae"]:.4f} ({x.loc[k, "c50"] * 100:.0f}/{x.loc[k, "c80"] * 100:.0f}%)' for k in fits))
x = R[R.tgt == 'RTY'].pivot(index='slot', columns='fit', values='mae')
print('  RTY by checkpoint (NQ+ES / RTY own / NQ+ES+RTY):', ' '.join(f'{(18 + i) % 24:02d}:59 {x.loc[i, "NQ+ES"]:.3f}/{x.loc[i, "RTY own"]:.3f}/{x.loc[i, "NQ+ES+RTY"]:.3f}' for i in [2, 8, 14, 15, 16, 18, 20]))
# ── 2. variance profile and kappa
H30 = {s: pd.read_pickle(f'slots30_{s}.pkl') for s in A}
def vprof(S):
    lc = np.log(S[[f'c{k}' for k in range(46)]].values); r = np.diff(np.c_[np.zeros(len(S)), lc], axis=1); return np.nanmean(r ** 2, axis=0)
def rem(v): r = (1 - np.cumsum(v) / v.sum())[1::2]; r[-1] = 0.0; return r
yrs = lambda S, a, b: S[(S.index.year >= a) & (S.index.year <= b)]
vNE = rem(np.mean([vprof(yrs(H30[s], 2018, 2024)) for s in ['NQ', 'ES']], axis=0))
vR = rem(vprof(yrs(H30['RTY'], 2018, 2024)))
print('\n2. SHARE OF THE DAY\'S VARIANCE STILL TO COME at the end of each hour (2018–24)')
hrs = [0, 6, 9, 12, 14, 15, 16, 17, 18, 19, 20, 21]
print('   hour ET   ' + ' '.join(f'{(18 + j + 1) % 24:02d}:00' for j in hrs))
print('   NQ+ES     ' + ' '.join(f'{vNE[j]:5.2f}' for j in hrs))
print('   RTY       ' + ' '.join(f'{vR[j]:5.2f}' for j in hrs))
for a, b in [(2018, 2020), (2021, 2022), (2023, 2024), (2025, 2026)]:
    print(f'   RTY {a}–{str(b)[2:]} ' + ' '.join(f'{x:5.2f}' for x in rem(vprof(yrs(H30["RTY"], a, b)))[hrs]))
def long_rows(S, sl):
    out = []
    for j in range(22):
        for pp, y in [(S[f'p{j}'], S[f'hi{j}']), (1 - S[f'p{j}'], S[f'lo{j}'])]:
            out.append(pd.DataFrame({'j': j, 'y': y, 'd': S[f'r{j}'] * (1 - pp), 'har': S.har, 'yr': S.index.year}))
    return pd.concat(out)
P_ = lambda d, kap, vr: np.clip(2 * norm.cdf(d.d / (kap * np.exp(d.har) * np.sqrt(np.maximum(vr[d.j.values], 1e-6)))) - 1, 0, 1)
L = {s: long_rows(A[s], s) for s in A}
def kfit(D, vr): return min(np.arange(0.4, 1.0, 0.005), key=lambda kp: ((D.y - P_(D, kp, vr)) ** 2).mean())
kNE = kfit(pd.concat([L['NQ'][L['NQ'].yr <= 2024], L['ES'][L['ES'].yr <= 2024]]), vNE)
kR = kfit(L['RTY'][L['RTY'].yr <= 2024], vR)
print(f'\n   kappa fitted 2018–24: NQ+ES {kNE:.3f} · RTY own {kR:.3f}  (production v12: 0.655)')
# ── 3. Brier skill on the test years
print('\n3. HIGH / LOW ALREADY IN · Brier skill vs the base rate for each hour, test 2025–26')
for s in A:
    D = L[s]; trD = D[D.yr <= 2024]; teD = D[D.yr >= 2025].copy(); teD['B'] = teD.j.map(trD.groupby('j').y.mean())
    sk = lambda p, m=None: 100 * (1 - ((teD.y - p) ** 2)[m].mean() / ((teD.y - teD.B) ** 2)[m].mean()) if m is not None else 100 * (1 - ((teD.y - p) ** 2).mean() / ((teD.y - teD.B) ** 2).mean())
    pv12 = P_(teD, 0.655, vNE); pown = P_(teD, kR, vR)
    am = teD.j >= 15
    print(f'  {s}: v12 constants {sk(pv12):5.1f}% (09:59 on {sk(pv12, am):5.1f}%) · RTY constants {sk(pown):5.1f}% (09:59 on {sk(pown, am):5.1f}%)')
R.to_pickle('rty_proj_cmp.pkl'); np.save('remH_RTY.npy', vR); pd.to_pickle({'kNE': kNE, 'kR': kR, 'vNE': vNE, 'vR': vR}, 'rty_rw.pkl')
