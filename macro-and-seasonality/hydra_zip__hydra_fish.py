"""HYDRA × Genjutsu Kai, step 2–3: fish many heads (base features + random combinations) for anything that predicts what
happens after an SMT, on 2018–24 only; correct for multiple testing; measure how much the same fishing finds in
shifted-target nulls; then take survivors and a multivariate model to the locked 2025–26 period."""
import pandas as pd, numpy as np, math, warnings, json, sys
warnings.filterwarnings('ignore')
from scipy import stats
rng = np.random.default_rng(7)
R = pd.read_pickle('hydra_events.pkl')
R['dd'] = np.where(R.hi == 1, -1, 1)                         # SMT trade direction: fade the take
TR = (R.year <= 2024); TE = (R.year >= 2025)
E = R[R.typ == 'smt'].copy(); C = R[R.typ == 'ctl'].copy(); Q = R[R.typ == 'rand'].copy()
out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); out.append(s)

def ctest(y, x=None, g=None):
    """mean (x None) or slope of y on standardised x, with day-clustered SE. Returns (est, t, p, n)."""
    y = np.asarray(y, float); g = np.asarray(g)
    if x is None:
        ok = ~np.isnan(y); y, g = y[ok], g[ok]; mu = y.mean(); e = y - mu
        codes = pd.factorize(g)[0]; s = np.bincount(codes, e); se = math.sqrt((s ** 2).sum()) / len(y)
        t = mu / se if se > 0 else 0; return mu, t, 2 * stats.norm.sf(abs(t)), len(y)
    x = np.asarray(x, float); ok = ~(np.isnan(y) | np.isnan(x)); y, x, g = y[ok], x[ok], g[ok]
    if len(y) < 200 or x.std() == 0: return np.nan, 0, 1, len(y)
    xc = (x - x.mean()) / x.std(); b = (xc * (y - y.mean())).sum() / (xc ** 2).sum()
    e = (y - y.mean()) - b * xc; codes = pd.factorize(g)[0]; s = np.bincount(codes, xc * e)
    se = math.sqrt((s ** 2).sum()) / (xc ** 2).sum(); t = b / se if se > 0 else 0
    return b, t, 2 * stats.norm.sf(abs(t)), len(y)

def wil(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d

# ───────────────────────────── A. what an SMT is worth before any fishing
P('=' * 100); P('A. BASELINES  (race: does NQ move 1σ30 in the SMT direction before 1σ30 against, by 16:14; σ30 = last-60-min 1-min σ × √30)')
for lab, M in (('2018–24', TR), ('2025–26', TE)):
    e = E[M[E.index]]; c = C[M[C.index]]; q = Q[M[Q.index]]
    ndays = R[M].tday.nunique()
    P(f'\n{lab}: {ndays} days · SMTs {len(e)} ({len(e) / ndays:.1f}/day) · controls (sister confirmed) {len(c)} · random bars {len(q)}')
    for nm, x in (('SMT, fade the leader', e), ('control, fade the sweep', c)):
        y = x.rev1.dropna(); lo, hi = wil(y.sum(), len(y))
        m_, t_, p_, n_ = ctest(x.r30.values, g=x.tday.values)
        P(f'   {nm:26s} race won {y.mean() * 100:5.1f}% [{lo * 100:.1f}–{hi * 100:.1f}]  · mean 30-min move {m_:+.3f}σ (t {t_:+.2f})')
    long_e = np.where(e.dd == 1, e.rev1, 1 - e.rev1); long_e = long_e[~np.isnan(long_e)]
    P(f'   {"always long, same bars":26s} race won {long_e.mean() * 100:5.1f}%  · random bars always long {q.rev1.mean() * 100:.1f}%  (30-min {q.up30.mean():+.3f}σ)')
    d_ = pd.concat([e.assign(isS=1), c.assign(isS=0)])
    b_, t_, p_, _ = ctest(d_.rev1.values, d_.isS.values.astype(float), d_.tday.values)
    P(f'   SMT minus control on race: t {t_:+.2f} (p {p_:.3f})')
    for k in ('30m', '60m', 'OR'):
        for hi in (1, 0):
            x = e[(e.kind == k) & (e.hi == hi)]; y = x.rev1.dropna(); cc = c[(c.kind == k) & (c.hi == hi)].rev1.dropna()
            hd = x[x.atEnd == 0].held.dropna()
            P(f'     {k:3s} {"high ▼" if hi else "low ▲ "}  n {len(y):5d}  SMT race {y.mean() * 100:5.1f}%  control {cc.mean() * 100:5.1f}%  · held {hd.mean() * 100:4.0f}% of SMTs')

# ───────────────────────────── B. the heads
BASE = ['hi', 'leadNQ', 'tod', 'lag', 'lagMx', 'grace', 'winMin', 'refA_pct', 'refB_pct', 'refA_sig', 'overA', 'overB', 'overDiff',
        'lrw', 'srw', 'dayExt', 'onExt', 'pdExt', 'posDay', 'mom30', 'mom5', 'momOpen', 'relStr', 'bothUp', 'gap', 'gapS', 'gap_atr',
        'on_atr', 'pm_atr', 'on_pos', 'rng_atr', 'pd_atr', 'd5_atr', 'atr_pct', 'sig30_pct', 'rv_rel', 'corr60', 'corrD', 'beta60',
        'disp60', 'v30A', 'v30B', 'distON', 'distPD', 'nSmt', 'nSameSide', 'nSyncd', 'sinceSmt', 'rvol', 'carry', 'dte', 'dow', 'mon',
        'opex_day', 'opex_week', 'qopex_week', 'tom', 'pre_hol', 'post_hol', 'roll_week', 'atEnd']
E['k30'] = (E.kind == '30m').astype(float); E['k60'] = (E.kind == '60m').astype(float); E['kOR'] = (E.kind == 'OR').astype(float)
E['refRatio'] = E.refA_pct / E.refB_pct; E['lagGrow'] = E.lagMx - E.lag
BASE += ['k30', 'k60', 'kOR', 'refRatio', 'lagGrow']
for d_ in range(5): E[f'dow{d_}'] = (E.dow == d_).astype(float)
BASE += [f'dow{d_}' for d_ in range(5)]
H = pd.DataFrame(index=E.index)
for b in BASE: H[b] = E[b].astype(float)
trE = E.year <= 2024
mu = H[trE].mean(); sd = H[trE].std().replace(0, 1)
Z = (H - mu) / sd
# random heads: products, differences, max/min of pairs, and random-threshold indicators ("fished data points")
nb = len(BASE); RND = []
for i in range(600):
    a, b = rng.choice(nb, 2, replace=False); a, b = BASE[a], BASE[b]; op = rng.integers(0, 5)
    if op == 0: v = Z[a] * Z[b]; nm = f'{a}*{b}'
    elif op == 1: v = Z[a] - Z[b]; nm = f'{a}-{b}'
    elif op == 2: v = np.maximum(Z[a], Z[b]); nm = f'max({a},{b})'
    elif op == 3:
        q = rng.uniform(0.1, 0.9); th = H.loc[trE, a].quantile(q); v = (H[a] > th).astype(float).where(H[a].notna()); nm = f'{a}>{th:.3g}'
    else:
        qa, qb = rng.uniform(0.2, 0.8, 2); ta, tb = H.loc[trE, a].quantile(qa), H.loc[trE, b].quantile(qb)
        v = ((H[a] > ta) & (H[b] > tb)).astype(float).where(H[a].notna() & H[b].notna()); nm = f'{a}>{ta:.3g}&{b}>{tb:.3g}'
    if nm not in H.columns and v[trE].std() > 0: H[nm] = v; RND.append(nm)
HEADS = BASE + RND
P('\n' + '=' * 100); P(f'B. FISHING on 2018–24: {len(HEADS)} heads ({len(BASE)} base + {len(RND)} random combinations) × 3 targets')
TARGETS = {'rev1': 'race won (fade)', 'r30': '30-min move (fade, σ)', 'held': 'SMT held (vs synced)'}
def target_mask(t): return (E.atEnd == 0) if t == 'held' else pd.Series(True, index=E.index)
def bh(p, q=0.10):
    p = np.asarray(p); o = np.argsort(p); n = len(p); th = q * np.arange(1, n + 1) / n
    ok = p[o] <= th; k = np.where(ok)[0].max() + 1 if ok.any() else 0
    res = np.zeros(n, bool); res[o[:k]] = True; return res
RES = {}
order = np.argsort(E.tday.values, kind='stable')
for t in TARGETS:
    msk = (trE & target_mask(t)).values
    y = E[t].values[msk]; g = E.tday.values[msk]
    rows = []
    for h in HEADS:
        b_, t_, p_, n_ = ctest(y, H[h].values[msk], g); rows.append((h, b_, t_, p_, n_))
    D = pd.DataFrame(rows, columns=['head', 'b', 't', 'p', 'n']).set_index('head')
    D['bh'] = bh(D.p.fillna(1).values); D['bonf'] = D.p * len(D) < 0.05
    # null: same fishing with the target circularly shifted in time (keeps its structure, breaks the alignment)
    nulls = []
    for s_ in range(20):
        sh = rng.integers(len(y) // 10, len(y) - len(y) // 10); ys = np.roll(y, sh)
        ps = np.array([ctest(ys, H[h].values[msk], g)[2] for h in HEADS])
        nulls.append(((ps < 0.01).sum(), bh(ps).sum(), (ps * len(ps) < 0.05).sum()))
    nulls = np.array(nulls)
    RES[t] = D
    P(f'\n{TARGETS[t]} (n {msk.sum()}): p<0.01 {int((D.p < 0.01).sum())} heads (shifted-target null: mean {nulls[:, 0].mean():.1f}, max {nulls[:, 0].max()}) · '
      f'BH-FDR 10% survivors {int(D.bh.sum())} (null mean {nulls[:, 1].mean():.1f}, max {nulls[:, 1].max()}) · Bonferroni {int(D.bonf.sum())} (null max {nulls[:, 2].max()})')

# ───────────────────────────── C. locked test
P('\n' + '=' * 100); P('C. LOCKED TEST 2025–26: train survivors (BH) and the top-12 train heads, same sign and one-sided p<0.05 out of sample?')
teE = E.year >= 2025
for t in TARGETS:
    D = RES[t]; msk = (teE & target_mask(t)).values; y = E[t].values[msk]; g = E.tday.values[msk]
    cand = list(D[D.bh].sort_values('p').index) + [h for h in D.reindex(D.t.abs().sort_values(ascending=False).index).index[:12] if not D.loc[h, 'bh']]
    P(f'\n{TARGETS[t]}: {int(D.bh.sum())} train survivors')
    keep = 0
    for h in cand[:40]:
        b2, t2, p2, n2 = ctest(y, H[h].values[msk], g)
        same = np.sign(b2) == np.sign(D.loc[h, 'b']); p1 = p2 / 2 if same else 1 - p2 / 2
        flag = 'HOLDS' if (same and p1 < 0.05) else ''
        keep += (flag == 'HOLDS') and D.loc[h, 'bh']
        P(f'   {"[BH]" if D.loc[h, "bh"] else "    "} {h[:46]:46s} train t {D.loc[h, "t"]:+6.2f} · test t {t2:+6.2f}  {flag}')
    P(f'   → train survivors that hold out of sample: {keep} of {int(D.bh.sum())}')
pd.to_pickle(dict(RES=RES, HEADS=HEADS, BASE=BASE, mu=mu, sd=sd), 'hydra_fish_res.pkl')
H.to_pickle('hydra_heads.pkl')
open('hydra_fish_out.txt', 'w').write('\n'.join(out))
