"""Checks: (a) shuffled-label null for the all-feature model (should sit near 0.5 -> no leakage),
(b) the three groups that helped on 2025-26 (NWOG, CBDR/flout, structure): gain over ATR in 2025 and 2026 separately,
and in each 2018-24 year when trained on the others (leave-one-year-out)."""
import pandas as pd, numpy as np, warnings
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
warnings.filterwarnings('ignore')
F = pd.read_pickle('/home/claude/byk/de_F.pkl')
Tr, Te = F[F.sp == 'train'], F[F.sp == 'test']
def logit(): return make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), LogisticRegression(C=0.3, max_iter=2000))
G = {'NWOG': ['nwog_size', 'nwog_ce_dist', 'nwog_inside', 'week_first'], 'CBDR / flout': ['cbdr', 'flout', 'cbdr_rel'],
     'Structure / trend': ['st_bull', 'st_bear', 'st_inside', 'st_outside', 'ret5', 'ret20', 'pos20']}
ALL = ['atr5'] + sorted({c for v in G.values() for c in v})
rng = np.random.default_rng(11); nulls = []
for _ in range(50):
    y = rng.permutation(Tr.exp.values); m = logit().fit(Tr[ALL], y); nulls.append(roc_auc_score(Te.exp, m.predict_proba(Te[ALL])[:, 1]))
print(f"(a) shuffled-label null AUC on 2025-26: mean {np.mean(nulls):.3f}, 95% range {np.percentile(nulls, 2.5):.3f}-{np.percentile(nulls, 97.5):.3f}")
print('(b) AUC gain over ATR-only, by year')
yrs = sorted(F.year.unique())
for g, cols in G.items():
    out = []
    for yr in yrs:
        A = F[(F.year != yr) & (F.year <= 2024)] if yr <= 2024 else Tr
        B = F[F.year == yr]
        m0 = logit().fit(A[['atr5']], A.exp); m1 = logit().fit(A[['atr5'] + cols], A.exp)
        out.append(f"{yr}: {roc_auc_score(B.exp, m1.predict_proba(B[['atr5'] + cols])[:, 1]) - roc_auc_score(B.exp, m0.predict_proba(B[['atr5']])[:, 1]):+.3f}")
    print(f"  {g:18s} " + ' | '.join(out))
