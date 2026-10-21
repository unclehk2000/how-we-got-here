"""HYDRA on one event table: fish many heads (base features known at the snapshot + 400 random combinations) on 2018–24,
Benjamini–Hochberg 10% per target, the same fishing on circularly shifted targets as the null (20 shifts), survivors
(up to 40 per target) taken to the locked 2025–26 days and to ES 2018–24, and a whole-net ridge logistic scored on
2025–26 against 200 shuffled-label nulls.   python3 fish_gen.py nfp|wk|fa"""
import numpy as np, pandas as pd, math, json, sys, warnings
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
warnings.filterwarnings('ignore')
EV = sys.argv[1]
COMMON = ['moPos', 'dMO', 'wkPos', 'dWO', 'pdPos', 'pdRng', 'pdDir', 't5', 't20', 'adrPct', 'athDist', 'vix', 'vixRel', 'dom', 'moPrem', 'moDisc', 'abovePDH', 'belowPDL']
CFG = {
 'nfp': dict(name='NFP days (snapshot 08:29)', base=COMMON + ['asiaRng', 'lonMove', 'preRng', 'preMove', 'drRng', 'drPos', 'wkMove', 'thuDir'],
             tgt={'y_s1': 'stage 1 up (08:30–08:50)', 'y_s2': 'stage 2 up (08:50–09:30)', 'y_am': 'NY AM up (09:30–11:00)', 'y_rth': 'RTH up', 'y_post': '08:30→16:14 up',
                  'y_cont': 'stage 2 continues stage 1', 'y_againstWk': 'day goes against the week', 'y_upSide': 'reaches further up than down', 'firstWon': 'first DR side taken wins',
                  'newHi': 'new day high after 08:30', 'newLo': 'new day low after 08:30', 'y_nAM': 'Monday NY AM up', 'm_s1': '|stage 1| (ADR)', 'm_s2': '|stage 2| (ADR)',
                  'm_am': '|NY AM| (ADR)', 'postRng': 'range after 08:30 (ADR)', 'nRng': "Monday's range (ADR)"}),
 'wk': dict(name='NFP week Mon–Thu (snapshot 09:29)', base=COMMON + ['onRng', 'onMove', 'gap', 'gapAbs', 'wkMove', 'nwog', 'dToNFP', 'dow'],
            tgt={'y_am': 'NY AM up', 'y_rth': 'RTH up', 'y_amCont': 'rest of RTH continues NY AM', 'y_upSide': 'reaches further up than down', 'newHi': 'new day high after 09:30',
                 'newLo': 'new day low after 09:30', 'gapFill': 'RTH gap filled by 16:14', 'ce10': 'gap 50% by 10:00', 'ce50': 'gap 50% in NY AM', 'q4held': 'open-side ¼ held NY AM',
                 'y_settle': 'settlement window up', 'm_am': '|NY AM| (ADR)', 'rthRng': 'RTH range (ADR)', 'settleRng': 'settlement range (ADR)', 'nRng': "next day's range (ADR)"}),
 'fa': dict(name='day after FOMC (snapshot 09:29)', base=COMMON + ['onRng', 'onMove', 'gap', 'gapAbs', 'fS1', 'fS2', 'fPost', 'fRng', 'fClosePos', 'fSep'],
            tgt={'y_am': 'NY AM up', 'y_rth': 'RTH up', 'y_contF': 'RTH goes the FOMC 14:00→16:14 way', 'y_contS2': 'NY AM goes the stage-2 way', 'y_upSide': 'reaches further up than down',
                 'newHi': 'new day high after 09:30', 'newLo': 'new day low after 09:30', 'takeFH': 'RTH takes FOMC day high', 'takeFL': 'RTH takes FOMC day low', 'gapFill': 'RTH gap filled by 16:14',
                 'ce50': 'gap 50% in NY AM', 'q4held': 'open-side ¼ held NY AM', 'm_am': '|NY AM| (ADR)', 'rthRng': 'RTH range (ADR)', 'nRng': "next day's range (ADR)"})}[EV]
rng = np.random.default_rng(11)
out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); out.append(s)
def slope(y, x, mn=8):
    ok = ~(np.isnan(y) | np.isnan(x)); y, x = y[ok], x[ok]; n = len(y)
    if n < 10 or x.std() == 0: return np.nan, 0.0, 1.0
    u = np.unique(x)
    if len(u) <= 2 and min((x == u[0]).sum(), (x == u[-1]).sum()) < mn: return np.nan, 0.0, 1.0
    xc = (x - x.mean()) / x.std(); yc = y - y.mean()
    b = (xc * yc).sum() / (xc ** 2).sum(); e = yc - b * xc
    h = 1 / n + xc ** 2 / (xc ** 2).sum()
    se = math.sqrt(((xc * e / (1 - h)) ** 2).sum()) / (xc ** 2).sum()
    t = b / se if se > 0 else 0.0
    return b, t, 2 * stats.t.sf(abs(t), n - 2)
def bh(p, q=0.10):
    p = np.asarray(p); n = len(p); o = np.argsort(p); th = q * np.arange(1, n + 1) / n
    ok = p[o] <= th; k = np.max(np.where(ok)[0]) + 1 if ok.any() else 0
    s = np.zeros(n, bool); s[o[:k]] = True; return s
N = pd.read_pickle(f'{EV}_NQ.pkl'); E = pd.read_pickle(f'{EV}_ES.pkl')
BASE, TGT = CFG['base'], CFG['tgt']
trN = np.asarray(N.index.year <= 2024); teN = ~trN; trE = np.asarray(E.index.year <= 2024)
mn_test = 4 if teN.sum() < 30 else 8
H = pd.DataFrame({b: N[b].astype(float) for b in BASE}); HE = pd.DataFrame({b: E[b].astype(float) for b in BASE})
mu, sd = H[trN].mean(), H[trN].std().replace(0, 1)
Z, ZE = (H - mu) / sd, (HE - mu) / sd
heads = {b: (H[b].values, HE[b].values) for b in BASE}
for i in range(400):
    a, b = rng.choice(len(BASE), 2, replace=False); a, b = BASE[a], BASE[b]; op = rng.integers(0, 5)
    if op == 0: heads[f'{a}*{b}'] = ((Z[a] * Z[b]).values, (ZE[a] * ZE[b]).values)
    elif op == 1: heads[f'{a}-{b}'] = ((Z[a] - Z[b]).values, (ZE[a] - ZE[b]).values)
    elif op == 2: heads[f'max({a},{b})'] = (np.maximum(Z[a], Z[b]).values, np.maximum(ZE[a], ZE[b]).values)
    elif op == 3:
        q = rng.uniform(0.15, 0.85); th = H.loc[trN, a].quantile(q); heads[f'{a}>{th:.3g}'] = ((H[a] > th).astype(float).values, (HE[a] > th).astype(float).values)
    else:
        q1, q2 = sorted(rng.uniform(0.15, 0.85, 2)); t1, t2 = H.loc[trN, a].quantile(q1), H.loc[trN, b].quantile(q2)
        heads[f'{a}>{t1:.3g}&{b}>{t2:.3g}'] = (((H[a] > t1) & (H[b] > t2)).astype(float).values, ((HE[a] > t1) & (HE[b] > t2)).astype(float).values)
names = list(heads)
P(f'HYDRA · {CFG["name"]} · NQ train 2018–24 n={trN.sum()} · locked 2025–26 n={teN.sum()} · {len(names)} heads ({len(BASE)} base) × {len(TGT)} targets')
P('\nB. FISHING (2018–24): BH 10% survivors vs circularly shifted targets (20 shifts)')
res = {}
for t, lab in TGT.items():
    y = N[t].values.astype(float); ytr = y[trN]
    ps = np.array([slope(ytr, heads[h][0][trN])[2] for h in names]); surv = bh(ps)
    nulls = [bh(np.array([slope(np.roll(ytr, k), heads[h][0][trN])[2] for h in names])).sum() for k in range(1, 21)]
    order = np.argsort(ps); sv = [names[i] for i in order if surv[i]]
    res[t] = dict(n_surv=int(surv.sum()), null_mean=float(np.mean(nulls)), null_max=int(np.max(nulls)), surv=sv, minp=float(ps.min()))
    P(f'  {lab:34s} survivors {surv.sum():3d} | shifted null mean {np.mean(nulls):.1f} max {np.max(nulls)} | best raw p {ps.min():.4f} ({names[int(np.argmin(ps))]})')
P('\nC. LOCKED TEST 2025–26 (same sign, one-sided p < 0.05) and ES replication (same sign on ES 2018–24)')
held = []; ntest = 0
for t, r in res.items():
    y = N[t].values.astype(float); ye = E[t].values.astype(float)
    for h in r['surv'][:40]:
        ntest += 1
        b0, t0, p0 = slope(y[trN], heads[h][0][trN]); b1, t1, p1 = slope(y[teN], heads[h][0][teN], mn_test); be, te_, pe = slope(ye[trE], heads[h][1][trE])
        ok1 = np.sign(b1) == np.sign(b0) and (p1 / 2) < 0.05; oke = np.sign(be) == np.sign(b0)
        if ok1: P(f'  {TGT[t]:32s} {h:40s} train t {t0:+.2f} · test t {t1:+.2f} (p1s {p1 / 2:.3f}) HELD · ES t {te_:+.2f} {"same" if oke else "opp"}')
        if ok1 and oke: held.append(dict(t=t, h=h, t0=t0, t1=t1, te=te_))
P(f'\n  survivors taken to the test: {ntest} · held in the locked test and same side on ES: {len(held)}')
P('\nD. WHOLE NET (ridge logistic on the base features, fit 2018–24): AUC on 2025–26 vs 200 shuffled-label nulls')
X = Z[BASE].fillna(0).values; net = {}
for t in TGT:
    y = N[t].values
    if t.startswith(('m_',)) or t.endswith('Rng') or set(np.unique(y[~np.isnan(y)])) - {0.0, 1.0}: continue
    ok = ~np.isnan(y); tr, te = trN & ok, teN & ok
    if len(set(y[te])) < 2: continue
    m = LogisticRegression(C=0.3, max_iter=2000).fit(X[tr], y[tr]); pr = m.predict_proba(X[te])[:, 1]; yt = y[te]
    auc = roc_auc_score(yt, pr); nul = [roc_auc_score(rng.permutation(yt), pr) for _ in range(200)]
    net[t] = (auc, float(np.percentile(nul, 95)))
    P(f'  {TGT[t]:34s} AUC {auc:.3f} · null 95th pct {np.percentile(nul, 95):.3f}{"  ← beats the null" if auc > np.percentile(nul, 95) else ""}')
json.dump(dict(res=res, held=held, net=net, ntest=ntest), open(f'fish_{EV}.json', 'w'), default=float)
open(f'fish_{EV}.txt', 'w').write('\n'.join(out))
