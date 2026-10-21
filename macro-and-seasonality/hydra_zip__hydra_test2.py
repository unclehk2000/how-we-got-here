"""HYDRA × Genjutsu Kai, step 3: (1) the fishing machine as one model (gradient boosting on every head) vs shifted-label
nulls, out of sample; (2) the roll-week head up close; (3) does an SMT that HELD (or synced) lead anywhere after the
window; (4) sync odds: can the chance that the sister still confirms be forecast from distance and time left?"""
import pandas as pd, numpy as np, math, warnings
warnings.filterwarnings('ignore')
from scipy import stats
from scipy.special import ndtr
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
exec(open('hydra_fish.py').read().split('# ───────────────────────────── A.')[0])        # loaders + ctest + wil
out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); out.append(s)
H = pd.read_pickle('hydra_heads.pkl'); RS = pd.read_pickle('hydra_fish_res.pkl'); HEADS = RS['HEADS']
E = E.loc[H.index]
trE = (E.year <= 2024).values; teE = (E.year >= 2025).values

# ───────────────────────────── 1. one model on every head
P('=' * 100); P('1. THE WHOLE FISHING NET AS ONE MODEL (gradient boosting on all heads, fit 2018–24, scored 2025–26)')
def gbm_auc(y, X, tr, te, seed=0):
    m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=200,
                                       l2_regularization=1.0, random_state=seed)
    m.fit(X[tr], y[tr]); return roc_auc_score(y[te], m.predict_proba(X[te])[:, 1]), m
X = H[HEADS].values.astype(float)
for t, lab in (('rev1', 'race won fading the SMT'), ('held', 'SMT held vs synced')):
    y = E[t].values; ok = ~np.isnan(y) & (y != 0.5)
    if t == 'held': ok &= (E.atEnd == 0).values
    tr = ok & trE; te = ok & teE; yb = (y > 0.5).astype(int)
    auc, _ = gbm_auc(yb, X, tr, te)
    nul = []
    for s_ in range(12):
        ys = yb.copy(); idx = np.where(tr)[0]; ys[idx] = np.roll(yb[idx], np.random.default_rng(s_).integers(len(idx) // 10, len(idx) * 9 // 10))
        nul.append(gbm_auc(ys, X, tr, te, s_)[0])
    P(f'   {lab}: test AUC {auc:.3f} · shifted-label nulls {np.mean(nul):.3f} (max {np.max(nul):.3f})')

# ───────────────────────────── 2. roll week
P('\n' + '=' * 100); P('2. THE ROLL-WEEK HEAD (the one directional head that survived both periods)')
for lab, M in (('2018–24', trE), ('2025–26', teE)):
    e = E[M]
    for rw in (1, 0):
        x = e[e.roll_week == rw]; y = x.rev1.dropna(); lo, hi = wil(y.sum(), len(y))
        lg = np.where(x.dd == 1, x.rev1, 1 - x.rev1); lg = lg[~np.isnan(lg)]
        P(f'   {lab} {"roll week " if rw else "other wks"}: SMTs {len(y):5d} on {x.tday.nunique():4d} days · fade won {y.mean() * 100:5.1f}% [{lo * 100:.1f}–{hi * 100:.1f}] · always long {lg.mean() * 100:5.1f}%')
yr = E[E.roll_week == 1].groupby('year').rev1.agg(['mean', 'size']); yr0 = E[E.roll_week == 0].groupby('year').rev1.mean()
P('   by year, roll week fade won % (other weeks): ' + ' · '.join(f'{y_} {r['mean'] * 100:.0f} ({yr0[y_] * 100:.0f}) n{int(r['size'])}' for y_, r in yr.iterrows()))
c = C.copy()
for lab, M in (('2018–24', c.year <= 2024), ('2025–26', c.year >= 2025)):
    x = c[M]
    P(f'   controls {lab}: roll week fade won {x[x.roll_week == 1].rev1.mean() * 100:.1f}% · other weeks {x[x.roll_week == 0].rev1.mean() * 100:.1f}%')

# ───────────────────────────── 3. after the window
P('\n' + '=' * 100); P('3. AFTER THE WINDOW: fade race from the window close (held SMTs, controls) or from the sync bar (synced SMTs)')
for lab, M in (('2018–24', E.year <= 2024), ('2025–26', E.year >= 2025)):
    e = E[M & (E.atEnd == 0)]; cc = C[(C.year <= 2024) if lab == '2018–24' else (C.year >= 2025)]
    for nm, x in (('held SMTs', e[e.st == 4]), ('synced SMTs (from sync)', e[e.st == 3]), ('controls (window close)', cc)):
        y = x.revPost.dropna(); lo, hi = wil(y.sum(), len(y))
        lg = np.where(x.dd == 1, x.revPost, 1 - x.revPost); lg = lg[~np.isnan(lg)]
        P(f'   {lab} {nm:25s} n {len(y):5d} · fade won {y.mean() * 100:5.1f}% [{lo * 100:.1f}–{hi * 100:.1f}] · always long {lg.mean() * 100:5.1f}%')
    for k in ('30m', '60m', 'OR'):
        x = e[(e.st == 4) & (e.kind == k)].revPost.dropna(); x2 = cc[cc.kind == k].revPost.dropna()
        P(f'      {k:3s}: held {x.mean() * 100:5.1f}% (n {len(x)}) vs controls {x2.mean() * 100:5.1f}% (n {len(x2)})')

# ───────────────────────────── 4. sync odds
P('\n' + '=' * 100); P('4. SYNC ODDS: P(sister takes its level before the window ends) = 2Φ(−gap / (κ · σ1 · √minutes left))')
S = E[(E.atEnd == 0) & (E.wLeft > 0) & E.held.notna()].copy()
S['gap'] = np.where(S.leadNQ == 1, -S.overB, -S.overA).clip(0)               # sister's distance to its level, in its σ30
S['z'] = S.gap * math.sqrt(30) / np.sqrt(S.wLeft)
S['sync'] = 1 - S.held
trS = S.year <= 2024; teS = S.year >= 2025
def p_th(z, k): return np.clip(2 * ndtr(-z / k), 1e-4, 1 - 1e-4)
def nll(y, p): return -(y * np.log(p) + (1 - y) * np.log(1 - p)).mean()
K = {}
for k in ('all', '30m', '60m', 'OR'):
    x = S[trS] if k == 'all' else S[trS & (S.kind == k)]
    grid = np.arange(0.3, 2.01, 0.005); L = [nll(x.sync.values, p_th(x.z.values, g)) for g in grid]; K[k] = grid[int(np.argmin(L))]
P('   κ fit on 2018–24: ' + ' · '.join(f'{k} {v:.3f}' for k, v in K.items()))
S['p1'] = p_th(S.z, K['all']); S['pk'] = [p_th(z, K[k]) for z, k in zip(S.z, S.kind)]
base = S[trS].groupby('kind').sync.mean(); S['pb'] = S.kind.map(base)
for lab, M in (('2018–24', trS), ('2025–26', teS)):
    x = S[M]; y = x.sync.values
    br = lambda p: ((p - y) ** 2).mean()
    P(f'\n   {lab}: n {len(x)} · synced {y.mean() * 100:.0f}%')
    P(f'      base rate by window kind    AUC {roc_auc_score(y, x.pb):.3f} · Brier {br(x.pb.values):.4f}')
    P(f'      one κ                       AUC {roc_auc_score(y, x.p1):.3f} · Brier {br(x.p1.values):.4f}')
    P(f'      κ per window kind           AUC {roc_auc_score(y, x.pk):.3f} · Brier {br(np.array(x.pk)):.4f}')
x = S[teS].copy(); x['bin'] = pd.cut(x.pk, [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0])
cal = x.groupby('bin').agg(pred=('pk', 'mean'), real=('sync', 'mean'), n=('sync', 'size'))
P('   2025–26 calibration (κ per kind): ' + ' · '.join(f'{r.pred * 100:.0f}→{r.real * 100:.0f}% n{int(r.n)}' for _, r in cal.iterrows() if r.n > 0))
# does the fishing add anything beyond the physics?
Xs = np.column_stack([H.loc[S.index, HEADS].values, S.z.values, np.array(S.pk)])
ys = S.sync.values.astype(int); a1, _ = gbm_auc(ys, Xs, trS.values, teS.values)
P(f'   all fished heads + physics (boosting): test AUC {a1:.3f}  vs physics alone {roc_auc_score(S[teS].sync, S[teS].pk):.3f}')
pd.to_pickle(K, 'hydra_kappa.pkl')
open('hydra_test2_out.txt', 'w').write('\n'.join(out))
