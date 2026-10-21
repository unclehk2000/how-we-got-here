"""HYDRA on NFP days with NQ, ES and RTY pooled (one row per symbol and day, every feature and target in each market's
own ADR20). The same day appears up to three times, so every test uses standard errors clustered by date, yes/no heads need
8 dates on each side, and the shifted-target nulls shift all three symbols together. Fishing on 2018–24; survivors (up to
40 per target) must hold on the locked 2025–26 days (pooled, clustered) and point the same way on NQ, ES and RTY separately."""
import numpy as np, pandas as pd, math, json, sys, warnings
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
warnings.filterwarnings('ignore')
rng = np.random.default_rng(11)
out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); out.append(s)
F = pd.concat([pd.read_pickle(f'nfp_{s}.pkl').assign(sym=s) for s in ('NQ', 'ES', 'RTY')]).reset_index().sort_values(['sym', 'tday']).reset_index(drop=True)
F['athNear'] = (F.athDist <= 1).astype(float)
BASE = ['moPos', 'dMO', 'wkPos', 'dWO', 'pdPos', 'pdRng', 'pdDir', 't5', 't20', 'adrPct', 'athDist', 'vix', 'vixRel', 'dom', 'moPrem', 'moDisc', 'abovePDH', 'belowPDL',
        'asiaRng', 'lonMove', 'preRng', 'preMove', 'drRng', 'drPos', 'wkMove', 'thuDir', 'athNear']
TGT = {'y_s1': 'stage 1 up', 'y_s2': 'stage 2 up', 'y_am': 'NY AM up', 'y_rth': 'RTH up', 'y_post': '08:30→16:14 up', 'y_cont': 'stage 2 continues stage 1',
       'y_againstWk': 'day goes against the week', 'y_upSide': 'reaches further up than down', 'firstWon': 'first DR side taken wins', 'newHi': 'new day high after 08:30',
       'newLo': 'new day low after 08:30', 'ceDay': 'ATH–08:29 CE touched by 17:00', 'y_nAM': 'Monday NY AM up', 'm_s1': '|stage 1| (ADR)', 'm_s2': '|stage 2| (ADR)',
       'm_am': '|NY AM| (ADR)', 'postRng': 'range after 08:30 (ADR)', 'nRng': "Monday's range (ADR)"}
dates = F.tday.values; dcode = pd.factorize(F.tday)[0]
tr = np.asarray(F.tday.dt.year <= 2024); te = ~tr
def slope(y, x, g, mn=8):
    """OLS of y on standardised x, errors clustered by date → (b, t, p)"""
    ok = ~(np.isnan(y) | np.isnan(x)); y, x, g = y[ok], x[ok], g[ok]
    G = len(np.unique(g))
    if G < 10 or x.std() == 0: return np.nan, 0.0, 1.0
    u = np.unique(x)
    if len(u) <= 2:
        if min(len(np.unique(g[x == u[0]])), len(np.unique(g[x == u[-1]]))) < mn: return np.nan, 0.0, 1.0
    xc = (x - x.mean()) / x.std(); yc = y - y.mean()
    b = (xc * yc).sum() / (xc ** 2).sum(); e = yc - b * xc
    sc = pd.Series(xc * e).groupby(g).sum().values
    se = math.sqrt((sc ** 2).sum() * G / (G - 1)) / (xc ** 2).sum()
    t = b / se if se > 0 else 0.0
    return b, t, 2 * stats.t.sf(abs(t), G - 1)
def bh(p, q=0.10):
    p = np.asarray(p); n = len(p); o = np.argsort(p); th = q * np.arange(1, n + 1) / n
    ok = p[o] <= th; k = np.max(np.where(ok)[0]) + 1 if ok.any() else 0
    s = np.zeros(n, bool); s[o[:k]] = True; return s
H = pd.DataFrame({b: F[b].astype(float) for b in BASE})
mu, sd = H[tr].mean(), H[tr].std().replace(0, 1); Z = (H - mu) / sd
heads = {b: H[b].values for b in BASE}
for i in range(400):
    a, b = rng.choice(len(BASE), 2, replace=False); a, b = BASE[a], BASE[b]; op = rng.integers(0, 5)
    if op == 0: heads[f'{a}*{b}'] = (Z[a] * Z[b]).values
    elif op == 1: heads[f'{a}-{b}'] = (Z[a] - Z[b]).values
    elif op == 2: heads[f'max({a},{b})'] = np.maximum(Z[a], Z[b]).values
    elif op == 3:
        q = rng.uniform(0.15, 0.85); th = H.loc[tr, a].quantile(q); heads[f'{a}>{th:.3g}'] = (H[a] > th).astype(float).values
    else:
        q1, q2 = sorted(rng.uniform(0.15, 0.85, 2)); t1, t2 = H.loc[tr, a].quantile(q1), H.loc[tr, b].quantile(q2)
        heads[f'{a}>{t1:.3g}&{b}>{t2:.3g}'] = ((H[a] > t1) & (H[b] > t2)).astype(float).values
names = list(heads)
syms = F.sym.values
def shift(y, k):                                   # circular shift within each symbol, by the same k
    z = y.copy()
    for s in ('NQ', 'ES', 'RTY'):
        m = (syms == s) & tr; z[m] = np.roll(y[m], k)
    return z
P(f'HYDRA · NFP days, NQ + ES + RTY pooled · train 2018–24 {tr.sum()} rows / {len(np.unique(dates[tr]))} dates · locked 2025–26 {te.sum()} rows / {len(np.unique(dates[te]))} dates · {len(names)} heads × {len(TGT)} targets')
P('\nB. FISHING (2018–24, errors clustered by date): BH 10% survivors vs 20 shifted-target nulls')
res = {}
for t, lab in TGT.items():
    y = F[t].values.astype(float)
    ps = np.array([slope(y[tr], heads[h][tr], dcode[tr])[2] for h in names]); surv = bh(ps)
    nulls = []
    for k in range(1, 21):
        ys = shift(y, k)
        nulls.append(bh(np.array([slope(ys[tr], heads[h][tr], dcode[tr])[2] for h in names])).sum())
    order = np.argsort(ps); sv = [names[i] for i in order if surv[i]]
    res[t] = dict(n_surv=int(surv.sum()), null_mean=float(np.mean(nulls)), null_max=int(np.max(nulls)), surv=sv)
    P(f'  {lab:34s} survivors {surv.sum():3d} | null mean {np.mean(nulls):.1f} max {np.max(nulls)} | best raw p {ps.min():.4f} ({names[int(np.argmin(ps))]})')
P('\nC. LOCKED TEST 2025–26 (pooled, same sign, one-sided p < 0.05) and the same sign on NQ, ES and RTY separately (2018–24)')
held = []; ntest = 0
for t, r in res.items():
    y = F[t].values.astype(float)
    for h in r['surv'][:40]:
        ntest += 1
        b0, t0, _ = slope(y[tr], heads[h][tr], dcode[tr]); b1, t1, p1 = slope(y[te], heads[h][te], dcode[te], 4)
        bs = [slope(y[tr & (syms == s)], heads[h][tr & (syms == s)], dcode[tr & (syms == s)])[0] for s in ('NQ', 'ES', 'RTY')]
        ok1 = np.sign(b1) == np.sign(b0) and p1 / 2 < 0.05; oks = all(np.sign(x) == np.sign(b0) for x in bs)
        if ok1 and oks:
            held.append(dict(t=t, h=h, t0=t0, t1=t1)); P(f'  HELD {lab if False else TGT[t]:30s} {h:36s} train t {t0:+.2f} · test t {t1:+.2f} (p1s {p1 / 2:.3f})')
P(f'\n  survivors taken to the test: {ntest} · held (test and all three symbols): {len(held)}')
from collections import Counter
P('  held by target: ' + ', '.join(f'{TGT[k]} {v}' for k, v in Counter(h["t"] for h in held).items()))
P('\nD. WHOLE NET (ridge logistic on the base features, fit 2018–24): AUC on 2025–26 vs 200 shuffled nulls')
X = Z[BASE].fillna(0).values
for t in TGT:
    y = F[t].values
    if t.startswith('m_') or t.endswith('Rng'): continue
    ok = ~np.isnan(y); a, b_ = tr & ok, te & ok
    if len(set(y[b_])) < 2: continue
    m = LogisticRegression(C=0.3, max_iter=2000).fit(X[a], y[a]); pr = m.predict_proba(X[b_])[:, 1]; yt = y[b_]
    auc = roc_auc_score(yt, pr); nul = [roc_auc_score(rng.permutation(yt), pr) for _ in range(200)]
    P(f'  {TGT[t]:34s} AUC {auc:.3f} · null 95th {np.percentile(nul, 95):.3f}{"  ← beats the null" if auc > np.percentile(nul, 95) else ""}')
json.dump(dict(res=res, held=held), open('fish_pool.json', 'w'), default=float)
open('fish_pool.txt', 'w').write('\n'.join(out))
