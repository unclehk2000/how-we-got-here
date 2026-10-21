import pandas as pd, numpy as np, json
from scipy import stats
X = pd.concat([pd.read_pickle(f'nfp_{s}.pkl') for s in ('NQ','ES','RTY')]).reset_index(); X = X[X.first != 0]
h = X.tday.dt.year <= 2024
out = {}
for nm, q in (('drRng', X.drRng), ('preRng', X.preRng)):
    t = q.quantile([1/3, 2/3]).values
    print(nm, 'cuts', t.round(3))
    for lab, m in (('narrow', q <= t[0]), ('mid', (q > t[0]) & (q <= t[1])), ('wide', q > t[1])):
        a = X.firstWon[m]; b = X.firstWon[~m]
        # date-clustered: average per date
        da = a.groupby(X.tday[m]).mean(); db = b.groupby(X.tday[~m]).mean()
        p = stats.ttest_ind(da, db, equal_var=False).pvalue
        print(f'  {lab:7s} n {m.sum():3d} won {100*a.mean():.0f}% vs {100*b.mean():.0f}% · 2018–24 {100*X.firstWon[m&h].mean():.0f}% / 2025–26 {100*X.firstWon[m&~h].mean():.0f}% · p {p:.4f} · ' +
              ' '.join(f"{s} {100*X.firstWon[m&(X.sym==s)].mean():.0f}" for s in ('NQ','ES','RTY')))
        out[f'{nm}_{lab}'] = dict(n=int(m.sum()), won=float(a.mean()), rest=float(b.mean()), h1=float(X.firstWon[m&h].mean()), h2=float(X.firstWon[m&~h].mean()), p=float(p), cut=t.tolist())
# DR width in ADR thresholds simple
for thr in (0.25, 0.3, 0.35):
    m = X.drRng <= thr
    print(f'drRng ≤ {thr}: n {m.sum()} won {100*X.firstWon[m].mean():.0f}% vs {100*X.firstWon[~m].mean():.0f}%  halves {100*X.firstWon[m&h].mean():.0f}/{100*X.firstWon[m&~h].mean():.0f}')
print('overall', X.firstWon.mean(), len(X), 'median drRng', X.drRng.median())
json.dump(out, open('dr_first.json','w'))
