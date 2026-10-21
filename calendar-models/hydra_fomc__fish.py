"""HYDRA on FOMC days. Fish many heads (base features known at 13:59 + random combinations) for anything that predicts
what follows the 14:00 statement, on 2018–24 only; Benjamini–Hochberg 10% FDR per target; the same fishing on circularly
shifted targets as the null; survivors and a whole-net model taken to the locked 2025–26 meetings; ES as a replication."""
import numpy as np, pandas as pd, math, json, warnings
from scipy import stats
warnings.filterwarnings('ignore')
rng = np.random.default_rng(11)
out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); out.append(s)
BASE = ['moPos', 'dMO', 'wkPos', 'dWO', 'pdPos', 'pdRng', 'pdDir', 'dayPos', 'preRng', 'preMove', 'onRng', 'onMove', 'amRng', 'amMove',
        'lunMove', 'gap', 'gapFilled', 't5', 't20', 'adrPct', 'athDist', 'vix', 'vixRel', 'sep', 'dom', 'moPrem', 'moDisc', 'abovePDH', 'belowPDL']
TGT = {'y_s1': 'stage 1 up', 'y_s2': 'stage 2 up', 'y_post': '14:00→16:14 up', 'y_cont': 'stage 2 continues stage 1', 'y_nAM': 'next NY AM up',
       'y_nAMwithS2': 'next NY AM with stage 2', 'y_nAMwithPost': 'next NY AM with 14:00→16:14', 'y_upSide': 'post-14:00 extends further up',
       'newHi': 'post-14:00 new day high', 'newLo': 'post-14:00 new day low', 'm_s1': '|stage 1| (ADR)', 'm_s2': '|stage 2| (ADR)', 'postRng': 'post-14:00 range (ADR)'}
def load(sym):
    F = pd.read_pickle(f'fomc_{sym}.pkl')
    F['moPrem'] = (F.moPos >= 0.75).astype(float); F['moDisc'] = (F.moPos <= 0.25).astype(float)
    F['abovePDH'] = (F.pdPos > 1).astype(float); F['belowPDL'] = (F.pdPos < 0).astype(float)
    return F
def slope(y, x, mn=8):
    """OLS slope of y on standardised x with HC1 robust SE → (b, t, p)"""
    ok = ~(np.isnan(y) | np.isnan(x)); y, x = y[ok], x[ok]; n = len(y)
    if n < 10 or x.std() == 0: return np.nan, 0.0, 1.0
    xc = (x - x.mean()) / x.std(); yc = y - y.mean()
    u = np.unique(x)
    if len(u) <= 2 and min((x == u[0]).sum(), (x == u[-1]).sum()) < mn: return np.nan, 0.0, 1.0   # yes/no head: 8+ days each side
    b = (xc * yc).sum() / (xc ** 2).sum(); e = yc - b * xc
    h = 1 / n + xc ** 2 / (xc ** 2).sum()                                                       # HC3: leverage-corrected
    se = math.sqrt(((xc * e / (1 - h)) ** 2).sum()) / (xc ** 2).sum()
    t = b / se if se > 0 else 0.0
    return b, t, 2 * stats.t.sf(abs(t), n - 2)
def bh(p, q=0.10):
    p = np.asarray(p); n = len(p); o = np.argsort(p); th = q * np.arange(1, n + 1) / n
    ok = p[o] <= th; k = np.max(np.where(ok)[0]) + 1 if ok.any() else 0
    s = np.zeros(n, bool); s[o[:k]] = True; return s
N = load('NQ'); E = load('ES')
trN = N.index.year <= 2024; teN = ~trN
# ── heads
H = pd.DataFrame({b: N[b].astype(float) for b in BASE}); HE = pd.DataFrame({b: E[b].astype(float) for b in BASE})
mu, sd = H[trN].mean(), H[trN].std().replace(0, 1)
Z, ZE = (H - mu) / sd, (HE - mu) / sd
heads = {b: (H[b], HE[b]) for b in BASE}
for i in range(400):
    a, b = rng.choice(len(BASE), 2, replace=False); a, b = BASE[a], BASE[b]; op = rng.integers(0, 5)
    if op == 0: heads[f'{a}*{b}'] = (Z[a] * Z[b], ZE[a] * ZE[b])
    elif op == 1: heads[f'{a}-{b}'] = (Z[a] - Z[b], ZE[a] - ZE[b])
    elif op == 2: heads[f'max({a},{b})'] = (np.maximum(Z[a], Z[b]), np.maximum(ZE[a], ZE[b]))
    elif op == 3:
        q = rng.uniform(0.15, 0.85); th = H.loc[trN, a].quantile(q); heads[f'{a}>{th:.3g}'] = ((H[a] > th).astype(float), (HE[a] > th).astype(float))
    else:
        q1, q2 = sorted(rng.uniform(0.15, 0.85, 2)); t1, t2 = H.loc[trN, a].quantile(q1), H.loc[trN, b].quantile(q2)
        heads[f'{a}>{t1:.3g}&{b}>{t2:.3g}'] = (((H[a] > t1) & (H[b] > t2)).astype(float), ((HE[a] > t1) & (HE[b] > t2)).astype(float))
names = list(heads); P(f'HYDRA · FOMC days · NQ train 2018–24 n={trN.sum()} · locked 2025–26 n={teN.sum()} · {len(names)} heads ({len(BASE)} base) × {len(TGT)} targets')
res = {}
P('\nB. FISHING (2018–24): BH 10% survivors vs circularly shifted targets (20 shifts)')
for t, lab in TGT.items():
    y = N[t].values.astype(float)
    ps = np.array([slope(y[trN], heads[h][0].values[trN])[2] for h in names])
    surv = bh(ps)
    nulls = []
    ytr = y[trN]
    for k in range(1, 21):
        ys = np.roll(ytr, k)
        pn = np.array([slope(ys, heads[h][0].values[trN])[2] for h in names]); nulls.append(bh(pn).sum())
    sv = [names[i] for i in np.where(surv)[0]]
    res[t] = dict(n_surv=int(surv.sum()), null_mean=float(np.mean(nulls)), null_max=int(np.max(nulls)), surv=sv, minp=float(ps.min()))
    P(f'  {lab:32s} survivors {surv.sum():3d} | shifted null mean {np.mean(nulls):.1f} max {np.max(nulls)} | best raw p {ps.min():.4f} ({names[int(np.argmin(ps))]})')
P('\nC. LOCKED TEST 2025–26 (same sign, one-sided p < 0.05) and ES replication (same sign on ES 2018–24)')
held = []
for t, r in res.items():
    y = N[t].values.astype(float); ye = E[t].values.astype(float); trE = np.asarray(E.index.year <= 2024)
    for h in r['surv'][:40]:
        b0, t0, p0 = slope(y[trN], heads[h][0].values[trN])
        b1, t1, p1 = slope(y[teN], heads[h][0].values[teN], 4)
        be, te_, pe = slope(ye[trE], heads[h][1].values[trE])
        ok1 = np.sign(b1) == np.sign(b0) and (p1 / 2) < 0.05
        oke = np.sign(be) == np.sign(b0)
        P(f'  {TGT[t]:30s} {h:40s} train t {t0:+.2f} · test t {t1:+.2f} (p1s {p1 / 2:.3f}) {"HELD" if ok1 else "—"} · ES t {te_:+.2f} {"same" if oke else "opp"}')
        if ok1 and oke: held.append((t, h, t0, t1, te_))
P(f'\n  held in the locked test and same side on ES: {len(held)}')
# ── whole net: ridge logistic on base features → 2025–26 AUC vs shifted-label nulls
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
P('\nD. WHOLE NET (ridge logistic on the 29 base features, fit 2018–24): AUC on 2025–26 vs 200 shuffled-label nulls')
X = Z[BASE].fillna(0).values
for t in ('y_s1', 'y_s2', 'y_post', 'y_cont', 'y_nAM', 'y_upSide', 'newHi', 'newLo'):
    y = N[t].values
    m = LogisticRegression(C=0.3, max_iter=2000).fit(X[trN], y[trN])
    pr = m.predict_proba(X[teN])[:, 1]; yt = y[teN]
    if len(set(yt)) < 2: continue
    auc = roc_auc_score(yt, pr)
    nul = [roc_auc_score(rng.permutation(yt), pr) for _ in range(200)]
    P(f'  {TGT[t]:32s} AUC {auc:.3f} · null 95th pct {np.percentile(nul, 95):.3f}')
json.dump(dict(res=res, held=held), open('fish_NQ_v3.json', 'w'), default=float)
open('fish_NQ_v3.txt', 'w').write('\n'.join(out))
