"""Monthly seasonality in % terms, NQ/ES/RTY Jan 2010 - Sep 2026 (Oct 2026 is partial and excluded).
Per-month stats, cross-month tests, split-half stability, and walk-forward seasonal rules vs always-long."""
import numpy as np, pandas as pd
from scipy import stats
M = pd.read_pickle('/home/claude/byk/season_M.pkl')
MN = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
rng = np.random.default_rng(11)
for nm, X in M.items():
    X = X[~((X.year == 2026) & (X.month >= 10))].copy()
    print(f'\n================ {nm}  ({len(X)} months)')
    g = X.groupby('month')
    pts_avg = g.pts.mean(); pct_avg = g.pct.mean()
    print('month  ptsAvg  pct mean  pct median  up%   n   t(vs 0)')
    for m in range(1, 13):
        v = X.pct[X.month == m]
        print(f' {MN[m-1]}  {pts_avg[m]:8.1f}  {v.mean():+6.2f}   {v.median():+6.2f}   {100*(v>0).mean():5.1f}  {len(v):2d}  {stats.ttest_1samp(v,0).statistic:+5.2f}')
    print(' all months: mean %+.2f, up %.1f%%' % (X.pct.mean(), 100 * (X.pct > 0).mean()))
    # how much of the points average comes from 2020+
    share = X[X.year >= 2020].pts.abs().sum() / X.pts.abs().sum()
    print(f' share of total |points| from 2020-26: {100*share:.0f}%  (those years are {100*(X.year>=2020).mean():.0f}% of months)')
    print(' rank of months by points avg vs % mean: Spearman', round(stats.spearmanr(pts_avg, pct_avg)[0], 2))
    print(' Kruskal across months p', round(stats.kruskal(*[X.pct[X.month == m] for m in range(1, 13)]).pvalue, 3),
          '| ANOVA p', round(stats.f_oneway(*[X.pct[X.month == m] for m in range(1, 13)]).pvalue, 3))
    a = X[X.year <= 2017].groupby('month').pct.mean(); b = X[X.year >= 2018].groupby('month').pct.mean()
    print(' split-half: month means 2010-17 vs 2018-26 Spearman', round(stats.spearmanr(a, b)[0], 2), 'p', round(stats.spearmanr(a, b)[1], 2))
    # walk-forward: decide each month using only earlier years (expanding, min 5 years)
    X = X.sort_values(['year', 'month']).reset_index(drop=True)
    res = {k: [] for k in ['long', 'pos_mean', 'skip_worst', 'skip_worst2', 'halloween', 'skip_sep']}
    for i, r in X.iterrows():
        if r.year < 2015: continue
        H = X[X.year < r.year]; mm = H.groupby('month').pct.mean()
        res['long'].append(r.pct)
        res['pos_mean'].append(r.pct if mm[r.month] > 0 else 0.0)
        res['skip_worst'].append(0.0 if r.month == mm.idxmin() else r.pct)
        res['skip_worst2'].append(0.0 if r.month in mm.nsmallest(2).index else r.pct)
        res['halloween'].append(r.pct if r.month in (11, 12, 1, 2, 3, 4) else 0.0)
        res['skip_sep'].append(0.0 if r.month == 9 else r.pct)
    L = np.array(res['long'])
    print(f' walk-forward 2015-01..2026-09 ({len(L)} months): rule  total%  mean%/mo  Sharpe(ann)  minus-long t')
    for k, v in res.items():
        v = np.array(v); d = v - L
        sh = v.mean() / v.std() * np.sqrt(12)
        t = d.mean() / (d.std(ddof=1) / np.sqrt(len(d))) if d.std() > 0 else 0
        print(f'   {k:12s} {v.sum():+7.1f}  {v.mean():+.3f}   {sh:5.2f}   {t:+5.2f}')
    # null for 'skip_worst': skip one random calendar month (chosen fresh each year), same exposure
    sk = []
    for s in range(2000):
        tot = 0.0
        for y, G in X[X.year >= 2015].groupby('year'):
            m0 = rng.integers(1, 13); tot += G.pct[G.month != m0].sum()
        sk.append(tot)
    v = np.array(res['skip_worst']).sum()
    print(f'   skip_worst {v:+.1f} vs skipping a random month each year: null median {np.median(sk):+.1f}, pct rank {100*(np.array(sk) < v).mean():.0f}%')
