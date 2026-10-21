"""Sync odds: fit on 2018–24 snapshots of open SMTs, score 2025–26."""
import pandas as pd, numpy as np, math, warnings, json
warnings.filterwarnings('ignore')
from scipy.special import ndtr, logit, expit
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, log_loss
S = pd.read_pickle('hydra_snaps.pkl').dropna(subset=['sync', 'gapNow', 'corr60', 'sgRel'])
S['gapNow'] = S.gapNow.clip(0)                                      # sister already at/through: distance 0
S['z'] = S.gapNow / np.sqrt(S.left)
tr = S.year <= 2024; te = S.year >= 2025
def pth(z, k): return np.clip(2 * ndtr(-z / k), 1e-4, 1 - 1e-4)
def nll(y, p): return -(y * np.log(p) + (1 - y) * np.log(1 - p)).mean()
K = {}
for k in ('30m', '60m', 'OR'):
    x = S[tr & (S.kind == k)]; g = np.arange(0.3, 2.5, 0.005)
    K[k] = float(g[np.argmin([nll(x.sync.values, pth(x.z.values, v)) for v in g])])
S['p1'] = [pth(z, K[k]) for z, k in zip(S.z, S.kind)]
S['lp1'] = logit(S.p1)
S['k60'] = (S.kind == '60m').astype(float); S['kOR'] = (S.kind == 'OR').astype(float)
S['lead_z'] = S.leadNow.clip(-5, 10) / np.sqrt(S.left)               # leader's extension, same scaling as z
S['pull'] = (S.gapNow - S.gapExt.clip(0)).clip(0, 20) / np.sqrt(S.left)   # sister's pullback from its best
S['lleft'] = np.log(S.left); S['lsg'] = np.log(S.sgRel.clip(0.2, 5))
base = S[tr].groupby('kind').sync.mean(); S['p0'] = S.kind.map(base)
F2 = ['lp1', 'k60', 'kOR']
F3 = ['lp1', 'k60', 'kOR', 'lead_z', 'pull', 'lleft', 'lsg', 'corr60', 'hi', 'leadNQ']
fits = {}
for nm, F in (('platt', F2), ('compact', F3)):
    m = LogisticRegression(C=1.0, max_iter=2000).fit(S.loc[tr, F], S.loc[tr, 'sync']); S['p_' + nm] = m.predict_proba(S[F])[:, 1]
    fits[nm] = dict(zip(['const'] + F, [float(m.intercept_[0])] + [float(c) for c in m.coef_[0]]))
gb = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=300).fit(S.loc[tr, F3 + ['z', 'gapNow', 'left', 'tod']], S.loc[tr, 'sync'])
S['p_gb'] = gb.predict_proba(S[F3 + ['z', 'gapNow', 'left', 'tod']])[:, 1]
print('κ per kind (2018–24):', {k: round(v, 3) for k, v in K.items()})
for lab, M in (('2018–24 (fit)', tr), ('2025–26 (locked)', te)):
    x = S[M]; y = x.sync.values
    print(f'\n{lab}: snapshots {len(x)} on {x.sid.nunique()} SMTs · synced {y.mean()*100:.0f}%')
    for nm, col in (('base rate by kind', 'p0'), ('random-walk formula', 'p1'), ('formula, recalibrated', 'p_platt'), ('compact logistic', 'p_compact'), ('boosting (ceiling)', 'p_gb')):
        p = x[col].values; print(f'   {nm:24s} AUC {roc_auc_score(y, p):.3f} · Brier {((p - y) ** 2).mean():.4f} · log loss {log_loss(y, p):.4f}')
    for col in ('p1', 'p_compact'):
        b = pd.cut(x[col], np.linspace(0, 1, 11)); cal = x.groupby(b).agg(pred=(col, 'mean'), real=('sync', 'mean'), n=('sync', 'size'))
        print(f'   calibration {col}: ' + ' · '.join(f'{r.pred*100:.0f}→{r.real*100:.0f}' for _, r in cal.iterrows() if r.n >= 50))
    f = x[x['first'] == 1]; print(f'   at the bar the SMT is drawn only: compact AUC {roc_auc_score(f.sync, f.p_compact):.3f} (n {len(f)})')
print('\ncoefficients:', json.dumps(fits, indent=1))
json.dump(dict(kappa=K, fits=fits), open('hydra_sync_fit.json', 'w'), indent=1)
S.to_pickle('hydra_snaps_scored.pkl')
