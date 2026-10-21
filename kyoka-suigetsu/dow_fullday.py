"""Full trading day (18:00-16:59 ET) day-of-week checks, NQ 1-min 2018 + 2022-Aug 2026.
Range %/net % of the 18:00 open by weekday, hour of the day's high/low, and which weekday sets the week's high/low
against a shuffled-within-week null (random-walk extremes cluster at the ends of the week, so uniform 20% is the wrong null)."""
import pandas as pd, numpy as np
from scipy import stats
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
rows = []
for d, x in b.groupby('tday'):
    if len(x) < 1200: continue
    o, c = x.Open.iloc[0], x.Close.iloc[-1]; H, L = x.High.max(), x.Low.min()
    hi_hm = x.hm.values[x.High.values.argmax()]; lo_hm = x.hm.values[x.Low.values.argmin()]
    rows.append(dict(tday=d, year=d.year, dow=d.dayofweek, o=o, c=c, H=H, L=L, rng=100*(H-L)/o, net=100*(c-o)/o,
                     hi_hr=hi_hm//100, lo_hr=lo_hm//100))
F = pd.DataFrame(rows); F = F[F.dow <= 4]; F['sp'] = np.where(F.year >= 2025, '2025-26', '2018-24')
F.to_pickle('/home/claude/byk/dow_F.pkl')
nm = ['Mon','Tue','Wed','Thu','Fri']
print('days', len(F), F.groupby('sp').size().to_dict())
for sp in ['2018-24','2025-26']:
    Z = F[F.sp == sp]; med_all = Z.rng.median()
    print(f'\n{sp}: weekday  n  up%  net%mean  rng%median  rng/all')
    for k in range(5):
        z = Z[Z.dow == k]
        print(f'  {nm[k]} {len(z):4d} {100*(z.net>0).mean():5.1f} {z.net.mean():+.3f} {z.rng.median():.3f} {z.rng.median()/med_all:.2f}')
    print('  range Kruskal p', round(stats.kruskal(*[Z.rng[Z.dow==k] for k in range(5)]).pvalue,4),
          '| up% chi2 p', round(stats.chi2_contingency(pd.crosstab(Z.dow, Z.net>0))[1],3))
    for k,n_ in [(3,'Thu'),(0,'Mon')]:
        print(f'  {n_} vs rest range MWU p', round(stats.mannwhitneyu(Z.rng[Z.dow==k], Z.rng[Z.dow!=k]).pvalue,4))
print('\nrange multiple by year (weekday median / all-days median)')
for y, Z in F.groupby('year'):
    m = Z.rng.median(); print(' ', y, ' '.join(f'{nm[k]} {Z.rng[Z.dow==k].median()/m:.2f}' for k in range(5)))
# hour-of-high / low, full day, ET clock hour, % of days
def hh(h): return h
F['hi_h'] = F.hi_hr; F['lo_h'] = F.lo_hr
order = [18,19,20,21,22,23,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
for sp in ['2018-24','2025-26']:
    Z = F[F.sp == sp]
    print(f'\n{sp} hour of day high / low (% of days, all weekdays)')
    print('  hr  ' + ' '.join(f'{h:>4d}' for h in order))
    print('  hi  ' + ' '.join(f'{100*(Z.hi_h==h).mean():4.0f}' for h in order))
    print('  lo  ' + ' '.join(f'{100*(Z.lo_h==h).mean():4.0f}' for h in order))
# weekly high/low by weekday vs shuffle null
F['wk'] = F.tday.dt.to_period('W-SUN')
rng_ = np.random.default_rng(7)
def wk_ext(G):
    out = []
    for w, g in G.groupby('wk'):
        if len(g) != 5: continue
        out.append((g.dow.values[g.H.values.argmax()], g.dow.values[g.L.values.argmin()]))
    return np.array(out)
def null(G, n=300):
    acc_h = np.zeros(5); acc_l = np.zeros(5); tot = 0
    for _ in range(n):
        for w, g in G.groupby('wk'):
            if len(g) != 5: continue
            # rebuild a path from shuffled day bars (open-relative highs/lows, net) keeping each day's shape
            p = rng_.permutation(5); o = 0.0; hs = []; ls = []
            for i in p:
                r = g.iloc[i]; hs.append(o + (r.H - r.o)/r.o); ls.append(o + (r.L - r.o)/r.o); o += (r.c - r.o)/r.o
            acc_h[np.argmax(hs)] += 1; acc_l[np.argmin(ls)] += 1; tot += 1
    return 100*acc_h/tot, 100*acc_l/tot
for sp in ['2018-24','2025-26']:
    G = F[F.sp == sp]; E = wk_ext(G); nh, nl = null(G, 100 if sp=='2018-24' else 200)
    print(f'\n{sp} weeks {len(E)}  weekday that set the week high / low (% of weeks) vs shuffled-week null')
    for k in range(5):
        print(f'  {nm[k]}  high {100*(E[:,0]==k).mean():5.1f} (null {nh[k]:4.1f})   low {100*(E[:,1]==k).mean():5.1f} (null {nl[k]:4.1f})')
    print('  high chi2 vs null p', round(stats.chisquare(np.bincount(E[:,0],minlength=5), nh/100*len(E)).pvalue,3),
          '| low p', round(stats.chisquare(np.bincount(E[:,1],minlength=5), nl/100*len(E)).pvalue,3))
