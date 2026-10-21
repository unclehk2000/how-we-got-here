"""Day-of-week and hour tests on the merged NQ set 2018-2026 (train 2018-24, test 2025-26)."""
import pandas as pd, numpy as np
from scipy import stats
F = pd.read_pickle('/home/claude/byk/dow_full.pkl')
nm = ['Mon','Tue','Wed','Thu','Fri']
for col, lab in [('rng', 'full day 18:00-17:00'), ('rth_rng', '09:30-16:14')]:
    print(f'\n=== range by weekday, {lab}: weekday median / all-days median')
    for y, Z in F.groupby('year'):
        m = Z[col].median(); print(' ', y, ' '.join(f'{nm[k]} {Z[col][Z.dow==k].median()/m:.2f}' for k in range(5)))
    for sp in ['2018-24', '2025-26']:
        Z = F[F.sp == sp].dropna(subset=[col]); m = Z[col].median()
        print(f'  {sp} n={len(Z)}  ' + ' '.join(f'{nm[k]} {Z[col][Z.dow==k].median()/m:.2f}' for k in range(5)),
              '| Kruskal p', round(stats.kruskal(*[Z[col][Z.dow == k] for k in range(5)]).pvalue, 4),
              '| Thu vs rest p', round(stats.mannwhitneyu(Z[col][Z.dow==3], Z[col][Z.dow!=3]).pvalue, 4),
              '| Mon vs rest p', round(stats.mannwhitneyu(Z[col][Z.dow==0], Z[col][Z.dow!=0]).pvalue, 4))
print('\n=== direction by weekday (full day): up% and mean net%')
for sp in ['2018-24', '2025-26']:
    Z = F[F.sp == sp]
    print(f'  {sp} ' + ' '.join(f'{nm[k]} {100*(Z.net[Z.dow==k]>0).mean():.0f}%/{Z.net[Z.dow==k].mean():+.2f}' for k in range(5)),
          '| chi2 p', round(stats.chi2_contingency(pd.crosstab(Z.dow, Z.net > 0))[1], 3))
# range relative to ATR removes the volatility regime: is any weekday different once the regime is out?
F['rr'] = F.rng / (100 * F.atr14 / F.o)
print('\n=== range / prior ATR14 by weekday (regime removed)')
for sp in ['2018-24', '2025-26']:
    Z = F[F.sp == sp].dropna(subset=['rr'])
    print(f'  {sp} ' + ' '.join(f'{nm[k]} {Z.rr[Z.dow==k].median():.2f}' for k in range(5)), '| Kruskal p',
          round(stats.kruskal(*[Z.rr[Z.dow == k] for k in range(5)]).pvalue, 4))
# hour of high/low, full day, % of days, by period
order = [18,19,20,21,22,23,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
for sp in ['2018-24', '2025-26']:
    Z = F[F.sp == sp]
    print(f'\n{sp} hour of the day high / low (% of days)')
    print('  hr ' + ' '.join(f'{h:>3d}' for h in order))
    print('  hi ' + ' '.join(f'{100*(Z.hi_hr==h).mean():3.0f}' for h in order))
    print('  lo ' + ' '.join(f'{100*(Z.lo_hr==h).mean():3.0f}' for h in order))
# rolling 'wide/narrow' colour vs weekday-shuffled null, last 20 of each weekday vs last 100 days
rng = np.random.default_rng(5)
r = F.rng.values
def shares(dw):
    out = np.zeros((5, 3))
    for t in range(150, len(F)):
        allm = np.median(r[t - 100:t])
        for k in range(5):
            idx = np.where(dw[:t] == k)[0][-20:]; m = np.median(r[idx]) / allm
            out[k] += [m >= 1.05, m <= 0.95, 1]
    return out[:, 0] / out[:, 2] * 100, out[:, 1] / out[:, 2] * 100
w, n_ = shares(F.dow.values)
print('\nrolling colour, 2018-26: wide%', np.round(w), 'narrow%', np.round(n_))
F['wk'] = F.tday.dt.to_period('W-SUN'); W = []
for s in range(15):
    d = F.dow.values.copy()
    for _, g in F.groupby('wk').groups.items():
        g = np.array(list(g)); d[g] = rng.permutation(d[g])
    W.append(shares(d)[0])
print('shuffled-weekday null wide% mean', np.round(np.mean(W, 0)), '95th', np.round(np.percentile(W, 95, 0)))
