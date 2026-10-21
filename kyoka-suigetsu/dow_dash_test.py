"""Does the dashboard's 'by now' status carry information, and does matching the weekday add anything?
At checkpoints (end of the 03, 09, 10, 12, 14 ET hour slots): today's running range vs the last 30 same-weekday days
at the same slot (80% band of the median) -> Above / Neutral / Below; same with the last 30 days of any weekday.
Outcome: range still to come, max(rest-of-day high) - min(rest-of-day low) beyond what's done, measured as the
day's final range / range at the checkpoint, and the rest-of-day net move sign. Also Monday-direction check."""
import pandas as pd, numpy as np
from scipy import stats
F = pd.read_pickle('/home/claude/byk/dow_full.pkl').reset_index(drop=True)
b = pd.read_pickle('/home/claude/twin/bars_NQ_full.pkl').sort_values('ts')
Z = 1.2816; N = 30
def band(a):
    s = np.sort(a); n = len(s)
    r1 = max(0, int(np.floor(n / 2 - Z * np.sqrt(n) / 2))); r2 = min(n - 1, int(np.ceil(n / 2 + Z * np.sqrt(n) / 2)) - 1)
    return np.median(s), s[r1], s[max(r1, r2)]
# rest-of-day extension after each checkpoint (from the bars)
ext = {}
g = {d: x for d, x in b.groupby('tday')}
for cp in [3, 9, 10, 12, 14]:
    e = []
    for d in F.tday:
        x = g[d]; hr = x.hm.values // 100
        # bars up to the end of slot cp in trading-day order: hours 18..23 come first, then 0..16
        ordh = np.where(hr >= 18, hr - 18, hr + 6); k = (cp - 18) % 24
        done = ordh <= k
        if done.sum() == 0 or (~done).sum() == 0: e.append((np.nan, np.nan)); continue
        o = x.Open.iloc[0]; h0, l0 = x.High.values[done].max(), x.Low.values[done].min()
        hF, lF = x.High.values.max(), x.Low.values.min(); c0 = x.Close.values[done][-1]; cF = x.Close.values[-1]
        e.append(((hF - lF) / (h0 - l0), 100 * (cF - c0) / o))
    ext[cp] = np.array(e)
rows = []
for cp in [3, 9, 10, 12, 14]:
    rc, nc = f'r{cp}', f'n{cp}'
    for i in range(len(F)):
        d = F.dow.iat[i]
        same = np.where(F.dow.values[:i] == d)[0][-N:]; anyd = np.arange(max(0, i - N), i)
        if len(same) < N or len(anyd) < N: continue
        x = F[rc].iat[i]; xn = F[nc].iat[i]
        res = {}
        for tag, idx in [('wk', same), ('all', anyd)]:
            m, lo, hi = band(F[rc].values[idx]); mn, lon, hin = band(F[nc].values[idx])
            res[tag] = ('Above' if x > hi else 'Below' if x < lo else 'Neutral', x / m,
                        'Above' if xn > hin else 'Below' if xn < lon else 'Neutral')
        rows.append(dict(cp=cp, i=i, year=F.year.iat[i], wk=res['wk'][0], all=res['all'][0], rat_wk=res['wk'][1],
                         rat_all=res['all'][1], nwk=res['wk'][2], nall=res['all'][2], grow=ext[cp][i, 0], rest_net=ext[cp][i, 1],
                         atr_now=x / (100 * F.atr14.iat[i] / F.o.iat[i]) if F.atr14.iat[i] > 0 else np.nan))
R = pd.DataFrame(rows).dropna(subset=['grow'])
R['sp'] = np.where(R.year >= 2025, '2025-26', '2018-24')
R.to_pickle('/home/claude/byk/dash_R.pkl')
for cp, G in R.groupby('cp'):
    print(f'\n=== checkpoint end of {cp:02d}:00 ET hour   (n={len(G)})')
    for tag in ['wk', 'all']:
        sh = G[tag].value_counts(normalize=True).reindex(['Above', 'Neutral', 'Below']) * 100
        med = G.groupby(tag).grow.median().reindex(['Above', 'Neutral', 'Below'])
        print(f'  {tag:3s} share A/N/B {sh.values.round(0)}  | final range ÷ range so far, median: A {med.Above:.2f} N {med.Neutral:.2f} B {med.Below:.2f}')
    # what matters operationally: does the ratio to the baseline predict how much the day still extends?
    for sp, H in G.groupby('sp'):
        rw = stats.spearmanr(H.rat_wk, H.grow)[0]; ra = stats.spearmanr(H.rat_all, H.grow)[0]
        print(f'  {sp}: Spearman(so-far ÷ baseline median, growth still to come)  same-weekday {rw:+.3f}  all-days {ra:+.3f}')
    # rest-of-day direction after a net-move status (momentum or fade?)
    t = G.groupby('nwk').rest_net.agg(['mean', 'count', lambda s: 100 * (s > 0).mean()]).reindex(['Above', 'Neutral', 'Below'])
    print('  net status (same weekday) -> rest-of-day net: ' + ' | '.join(f'{k} {t.loc[k, "mean"]:+.3f}% up {t.loc[k, "<lambda_0>"]:.0f}% (n {int(t.loc[k, "count"])})' for k in t.index))
# Monday direction vs other days (full day net), and Monday-only vs always-long Sharpe
print('\n=== Monday direction')
for sp in ['2018-24', '2025-26']:
    X = F[F.sp == sp]; m = X.net[X.dow == 0]; o = X.net[X.dow != 0]
    t = stats.ttest_ind(m, o, equal_var=False)
    sh_l = X.net.mean() / X.net.std() * np.sqrt(252); mo = np.where(X.dow == 0, X.net, 0.0)
    sh_m = mo.mean() / mo.std() * np.sqrt(252)
    print(f'  {sp}: Mon mean {m.mean():+.3f}% up {100*(m>0).mean():.0f}% vs other days {o.mean():+.3f}% up {100*(o>0).mean():.0f}% | Welch t {t.statistic:+.2f} p {t.pvalue:.3f} | Sharpe always-long (session only) {sh_l:.2f} vs Monday-only {sh_m:.2f}')
for y, X in F.groupby('year'):
    m = X.net[X.dow == 0]; o = X.net[X.dow != 0]
    print(f'   {y}: Mon {m.mean():+.2f}% up {100*(m>0).mean():.0f}%  | others {o.mean():+.2f}% up {100*(o>0).mean():.0f}%')
