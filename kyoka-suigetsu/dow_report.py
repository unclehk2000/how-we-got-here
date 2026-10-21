import pandas as pd, numpy as np
from scipy import stats
D = pd.read_pickle('/home/claude/byk/dow_D.pkl'); NM = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
def t(v): v = pd.Series(v).dropna(); return v.mean() / (v.std(ddof=1) / np.sqrt(len(v)))
pd.set_option('display.width', 220)
for sp in ['2018-24', '2025-26']:
    Z = D[D.sp == sp]
    g = Z.groupby('dow').agg(n=('up', 'size'), up=('up', lambda s: 100 * s.mean()), net=('net', 'mean'), rng=('rng', 'mean'), rng_med=('rng', 'median'),
                             or_hold=('or_hold', lambda s: 100 * s.mean()), rev=('rev', lambda s: 100 * s.mean()))
    g.index = NM; g.loc['All'] = [len(Z), 100 * Z.up.mean(), Z.net.mean(), Z.rng.mean(), Z.rng.median(), 100 * Z.or_hold.mean(), 100 * Z.rev.mean()]
    print(f"\n==== {sp} (RTH 09:30-16:14; net and range in % of the open)"); print(g.round(3).to_string())
    ct = pd.crosstab(Z.dow, Z.up); chi = stats.chi2_contingency(ct)
    kw = stats.kruskal(*[Z.rng[Z.dow == k] for k in range(5)])
    an = stats.kruskal(*[Z.net[Z.dow == k] for k in range(5)])
    print(f"  up% differs by weekday? chi-square p = {chi[1]:.3f} | net move differs? Kruskal p = {an.pvalue:.3f} | range differs? Kruskal p = {kw.pvalue:.4f}")
print('\n==== Year by year: % up days by weekday (all-days in brackets)')
for y, Z in D.groupby('year'):
    print(f"  {y}: " + ' '.join(f"{NM[k]} {100*Z.up[Z.dow==k].mean():3.0f}" for k in range(5)) + f"  (all {100*Z.up.mean():.0f}, n{len(Z)})")
print('\n==== Year by year: mean RTH range by weekday as a multiple of that year\'s average')
for y, Z in D.groupby('year'):
    m = Z.rng.mean(); print(f"  {y}: " + ' '.join(f"{NM[k]} {Z.rng[Z.dow==k].mean()/m:4.2f}" for k in range(5)))
print('\n==== Hour the RTH high / low forms (% of days), all years')
for k in range(5):
    Z = D[D.dow == k]
    hh = (Z.hi_hr.value_counts(normalize=True) * 100).round(0).sort_index().to_dict(); ll = (Z.lo_hr.value_counts(normalize=True) * 100).round(0).sort_index().to_dict()
    print(f"  {NM[k]} high {hh}\n      low  {ll}")
print('\n==== Weekday rules vs always-long (RTH open -> 16:14 close, 1 pt cost per trade, % per day averaged over ALL days)')
for sp in ['2018-24', '2025-26']:
    Z = D[D.sp == sp].copy(); cost = 100 * 1 / Z.o
    long_all = Z.net - cost
    rules = {'Always long': long_all,
             'Long, but flat on Thursday': np.where(Z.dow == 3, 0, Z.net - cost),
             'Long, but short Thursday': np.where(Z.dow == 3, -Z.net - cost, Z.net - cost),
             'Long Monday only': np.where(Z.dow == 0, Z.net - cost, 0)}
    for nm, v in rules.items():
        v = pd.Series(v)
        print(f"  {sp} {nm:28s} avg {v.mean():+.4f}%/day | total {v.sum():+7.1f}% | vs always-long {(v - long_all.values).mean():+.4f}%/day (t {t(v.values - long_all.values):.2f})")
