"""Monday check against data the v2 sheet never saw. The v2 'Monday 60% up' claim was built on Jan 2023 - Aug 2026,
so the fair out-of-sample test is 2018-2022 plus Sep-Oct 2026. Also splits each weekday's full-day return into the
overnight part (18:00 -> 09:29 ET) and the day part (09:30 -> 16:59 ET)."""
import pandas as pd, numpy as np
from scipy import stats
b = pd.read_pickle('/home/claude/twin/bars_NQ_full.pkl').sort_values('ts')
F = pd.read_pickle('/home/claude/byk/dow_full.pkl')
rows = []
for d, x in b.groupby('tday'):
    if d.dayofweek > 4 or len(x) < 1000: continue
    o = x.Open.iloc[0]; pre = x[(x.hm >= 1800) | (x.hm < 930)]; day = x[(x.hm >= 930) & (x.hm < 1700)]
    if len(pre) < 300 or len(day) < 300: continue
    rows.append(dict(tday=d, dow=d.dayofweek, year=d.year, on=100 * (pre.Close.iloc[-1] - o) / o,
                     dy=100 * (day.Close.iloc[-1] - day.Open.iloc[0]) / o, full=100 * (x.Close.iloc[-1] - o) / o))
X = pd.DataFrame(rows)
nm = ['Mon','Tue','Wed','Thu','Fri']
def cmp(Z, lab):
    m = Z.full[Z.dow == 0]; o = Z.full[Z.dow != 0]; t = stats.ttest_ind(m, o, equal_var=False)
    print(f'  {lab}: n Mon {len(m)} | Mon {m.mean():+.3f}% up {100*(m>0).mean():.0f}% vs others {o.mean():+.3f}% up {100*(o>0).mean():.0f}% | Welch t {t.statistic:+.2f} p {t.pvalue:.3f}')
print('Monday vs other weekdays, full trading day:')
cmp(X[X.year <= 2022], '2018-2022 (before the sheet)')
cmp(X[(X.tday >= '2023-01-01') & (X.tday < '2026-09-01')], 'Jan 2023-Aug 2026 (the sheet\'s own sample)')
cmp(X[X.tday >= '2026-09-01'], 'Sep-Oct 2026 (after the sheet)')
print('\nOvernight (18:00-09:29) vs day (09:30-16:59) mean % by weekday, 2018-2026:')
for k in range(5):
    Z = X[X.dow == k]
    print(f'  {nm[k]}  overnight {Z.on.mean():+.3f}% (t {stats.ttest_1samp(Z.on, 0).statistic:+.2f})   day {Z.dy.mean():+.3f}% (t {stats.ttest_1samp(Z.dy, 0).statistic:+.2f})   n {len(Z)}')
o_m = X.on[X.dow == 0]; o_o = X.on[X.dow != 0]
print(f'  Monday overnight vs other overnights: Welch p {stats.ttest_ind(o_m, o_o, equal_var=False).pvalue:.3f}')
d_m = X.dy[X.dow == 0]; d_o = X.dy[X.dow != 0]
print(f'  Monday day session vs other day sessions: Welch p {stats.ttest_ind(d_m, d_o, equal_var=False).pvalue:.3f}')
