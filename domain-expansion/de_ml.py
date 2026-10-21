"""Which factors, beyond the overnight ATR, predict a Domain Expansion day? Fit on 2018-24, judged once on 2025-26.
1) ATR-only logistic baseline. 2) ATR + each ICT feature group: test AUC gain, paired-bootstrap 95% CI, and the same gain
inside 2018-24 by expanding time-series CV (so a group has to help in both). 3) Full models (logistic, gradient boosting)
with permutation importance on 2025-26. 4) Direction on expansion days."""
import pandas as pd, numpy as np, warnings
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
from sklearn.inspection import permutation_importance
warnings.filterwarnings('ignore')
F = pd.read_pickle('/home/claude/byk/de_F.pkl')
Tr, Te = F[F.sp == 'train'].reset_index(drop=True), F[F.sp == 'test'].reset_index(drop=True)
GROUPS = {
 'Settlement window 16:14-16:59 ET (21:14-21:59 UK)': ['sw_abs', 'sw_rng', 'sw_net', 'sw_rng_rel'],
 'NWOG': ['nwog_size', 'nwog_ce_dist', 'nwog_inside', 'week_first'],
 'NDOG': ['ndog', 'ndog_abs'],
 'True day open (00:00 ET)': ['mo_dist', 'mo_abs', 'mo_in_lor'],
 '23:00-00:00 ET range': ['r2300', 'r2300_rel'],
 '18:00-19:00 ET (23:00-00:00 UK) range': ['r1800', 'r1800_rel'],
 'CBDR / flout': ['cbdr', 'flout', 'cbdr_rel'],
 'Asia range': ['asia', 'asia_rel', 'asia_sw_lor'],
 'Domain range geometry': ['lor_pct', 'lor_pct_rel', 'lor_oct', 'lor_vs_asia'],
 'Overnight path': ['on_move', 'on_pos'],
 'PDH / PDL liquidity': ['pdh_dist', 'pdl_dist', 'pdh_swept', 'pdl_swept'],
 'Prior day': ['pd_rng', 'pd_ret', 'pd_clv', 'pd_rth_rng', 'pd_exp', 'vol5'],
 'Daily market structure / trend': ['st_bull', 'st_bear', 'st_inside', 'st_outside', 'ret5', 'ret20', 'pos20'],
 'Calendar / events': ['mon', 'fri', 'fomc', 'fomc_eve', 'nfp', 'dst_mis'],
}
BASE = ['atr5']
def logit(): return make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), LogisticRegression(C=0.3, max_iter=2000))
def fit_auc(cols, A, B):
    m = logit().fit(A[cols], A.exp); return m, roc_auc_score(B.exp, m.predict_proba(B[cols])[:, 1]), m.predict_proba(B[cols])[:, 1]
def cv_gain(cols):
    """expanding-window CV inside 2018-24: folds by year 2023, 2024 (train on everything earlier)"""
    g = []
    for yr in [2023, 2024]:
        A, B = Tr[Tr.year < yr], Tr[Tr.year == yr]
        g.append(fit_auc(BASE + cols, A, B)[1] - fit_auc(BASE, A, B)[1])
    return np.mean(g)
rng = np.random.default_rng(7)
def boot_gain(p0, p1, y, n=2000):
    y = np.asarray(y); out = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if y[i].min() == y[i].max(): continue
        out.append(roc_auc_score(y[i], p1[i]) - roc_auc_score(y[i], p0[i]))
    return np.percentile(out, [2.5, 97.5])
_, auc0, p0 = fit_auc(BASE, Tr, Te)
_, auc0_tr, _ = fit_auc(BASE, Tr, Tr)
print(f"Expansion-day rate: train {100*Tr.exp.mean():.1f}% (n{len(Tr)}), test {100*Te.exp.mean():.1f}% (n{len(Te)})")
print(f"ATR-only baseline AUC: in-sample {auc0_tr:.3f} | 2025-26 {auc0:.3f}\n")
res = []
for gname, cols in GROUPS.items():
    _, a1, p1 = fit_auc(BASE + cols, Tr, Te)
    lo, hi = boot_gain(p0, p1, Te.exp)
    # the group on its own (without ATR)
    _, alone, _ = fit_auc(cols, Tr, Te)
    res.append(dict(group=gname, alone_AUC=alone, with_ATR=a1, gain_test=a1 - auc0, ci_lo=lo, ci_hi=hi, gain_cv_2023_24=cv_gain(cols)))
R = pd.DataFrame(res).sort_values('gain_test', ascending=False)
pd.set_option('display.width', 220)
print(R.round(3).to_string(index=False))
ALL = BASE + sorted({c for v in GROUPS.values() for c in v})
mL, aL, pL = fit_auc(ALL, Tr, Te)
gb = make_pipeline(SimpleImputer(strategy='median'), HistGradientBoostingClassifier(max_depth=3, learning_rate=0.04, max_iter=250, min_samples_leaf=40, l2_regularization=1.0, random_state=1))
gb.fit(Tr[ALL], Tr.exp); pG = gb.predict_proba(Te[ALL])[:, 1]; aG = roc_auc_score(Te.exp, pG)
gbn = make_pipeline(SimpleImputer(strategy='median'), HistGradientBoostingClassifier(max_depth=3, learning_rate=0.04, max_iter=250, min_samples_leaf=40, l2_regularization=1.0, random_state=1))
NOATR = [c for c in ALL if c not in ('atr5', 'on_tr', 'vol5', 'pd_rng', 'pd_rth_rng', 'asia', 'asia_rel', 'r2300', 'r1800', 'cbdr', 'flout', 'sw_rng', 'lor_pct')]
gbn.fit(Tr[NOATR], Tr.exp); aN = roc_auc_score(Te.exp, gbn.predict_proba(Te[NOATR])[:, 1])
print(f"\nAll features, logistic: 2025-26 AUC {aL:.3f} (gain over ATR {aL-auc0:+.3f}, 95% CI {boot_gain(p0, pL, Te.exp)[0]:+.3f} to {boot_gain(p0, pL, Te.exp)[1]:+.3f})")
print(f"All features, gradient boosting: 2025-26 AUC {aG:.3f} (gain over ATR {aG-auc0:+.3f}, 95% CI {boot_gain(p0, pG, Te.exp)[0]:+.3f} to {boot_gain(p0, pG, Te.exp)[1]:+.3f})")
print(f"Gradient boosting with every volatility/size measure removed: 2025-26 AUC {aN:.3f}")
pi = permutation_importance(gb, Te[ALL], Te.exp, scoring='roc_auc', n_repeats=30, random_state=3)
imp = pd.Series(pi.importances_mean, index=ALL).sort_values(ascending=False)
print('\nPermutation importance on 2025-26 (AUC drop when shuffled), top 12:'); print(imp.head(12).round(4).to_string())
# univariate check of the top non-volatility candidates: rate by tercile, within ATR-qualified (>=1%) and not
print('\nExpansion rate by tercile (cuts from 2018-24), split by the ATR qualifier (>= 1.00%):')
for c in ['sw_abs', 'mo_abs', 'ndog_abs', 'nwog_size', 'pdh_dist', 'pdl_dist', 'on_move', 'lor_oct', 'pos20', 'ret5', 'lor_pct_rel', 'asia_rel']:
    q = Tr[c].quantile([1/3, 2/3]).values
    line = f"  {c:11s}"
    for nm, Z in [('train', Tr), ('test', Te)]:
        for qual in [True, False]:
            S = Z[(Z.atr5 >= 1.0) == qual]; k = np.digitize(S[c], q)
            line += f" | {nm[:2]} {'Q' if qual else 'n'}: " + ' '.join(f"{100*S.exp[k==i].mean():4.0f}" for i in range(3))
    print(line)
# direction on expansion days
print('\nDirection on expansion days (up vs down), 2025-26 AUC; base rate up:')
E1, E2 = Tr[Tr.exp], Te[Te.exp]
DIRF = ['on_move', 'on_pos', 'mo_dist', 'nwog_ce_dist', 'ndog', 'sw_net', 'pd_ret', 'pd_clv', 'ret5', 'ret20', 'pos20', 'lor_oct', 'pdh_dist', 'pdl_dist', 'st_bull', 'st_bear']
md = logit().fit(E1[DIRF], E1.expDir > 0); pdir = md.predict_proba(E2[DIRF])[:, 1]
print(f"  train up {100*(E1.expDir>0).mean():.1f}% (n{len(E1)}), test up {100*(E2.expDir>0).mean():.1f}% (n{len(E2)}) | direction AUC 2025-26 {roc_auc_score(E2.expDir > 0, pdir):.3f}")
for c in DIRF:
    a = roc_auc_score(E1.expDir > 0, E1[c].fillna(E1[c].median())); b_ = roc_auc_score(E2.expDir > 0, E2[c].fillna(E2[c].median()))
    if abs(a - 0.5) > 0.07: print(f"    {c:12s} single-feature AUC train {a:.3f} | test {b_:.3f}")
R.to_csv('/home/claude/byk/de_ml_groups.csv', index=False)
