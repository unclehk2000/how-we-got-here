"""DXY weekly trend vs NQ/ES volatility (and event days), 2023-01 → 2026-08. DXY futures 5-min (Barchart, CT → ET)."""
import pandas as pd, numpy as np
from scipy import stats
X = pd.read_csv('/mnt/user-data/uploads/DXY_2023_2026_5min_continuous.csv')
X['ts'] = pd.to_datetime(X.Date + ' ' + X.Time) + pd.Timedelta(hours=1)          # CT → ET
X = X.sort_values('ts'); X['tday'] = (X.ts + pd.Timedelta(hours=6)).dt.normalize()
d = X.groupby('tday').agg(o=('Open', 'first'), h=('High', 'max'), l=('Low', 'min'), c=('Close', 'last'))
d = d[d.index.dayofweek < 5]
# weekly: Friday close to Friday close; the trend known on a given day = last COMPLETED week's change and the 4-week change
wk = d.c.resample('W-FRI').last().dropna()
w1 = np.log(wk).diff(); w4 = np.log(wk).diff(4)
d['wk'] = d.index.to_period('W-FRI').start_time  # Saturday-start label
lastWk = pd.Series(w1.values, index=wk.index); last4 = pd.Series(w4.values, index=wk.index)
def known(series, t):
    s = series[series.index < t - pd.Timedelta(days=0)]
    return s.iloc[-1] if len(s) else np.nan
d['dxy1w'] = [known(lastWk, t) for t in d.index]; d['dxy4w'] = [known(last4, t) for t in d.index]
# DXY week-to-date move as of the prior day close (also known before the day)
d['wtd'] = np.nan
for t in d.index:
    fri = wk[wk.index < t]
    if len(fri): d.loc[t, 'wtd'] = np.log(d.c[d.index < t].iloc[-1] / fri.iloc[-1]) if (d.index < t).any() else np.nan
d['dxyR'] = (d.h - d.l) / d.o
d['dxyADR'] = d.dxyR.shift(1).rolling(20).mean()
out = []
for root in ('NQ', 'ES'):
    P = pd.read_pickle(f'prof_{root}.pkl'); P = P[(P.index >= '2023-02-01') & (P.index <= '2026-08-27')]
    P = P.join(d[['dxy1w', 'dxy4w', 'wtd', 'dxyR', 'dxyADR']], how='inner')
    P['R'] = P.rthR / (P.adr * P.tdO); P['TDR'] = (P.tdH - P.tdL) / P.tdO / P.adr
    P['abs1w'] = P.dxy1w.abs(); P['abs4w'] = P.dxy4w.abs()
    print(f'\n{root}: {len(P)} days 2023-02 → 2026-08')
    for col, lab in (('dxy1w', 'last week DXY change'), ('dxy4w', '4-week DXY change'), ('abs1w', '|last week DXY change|'), ('abs4w', '|4-week DXY change|'), ('wtd', 'DXY week-to-date')):
        for y, ylab in (('TDR', 'day range ÷ ADR'), ('R', 'RTH range ÷ ADR')):
            ok = P[[col, y]].dropna(); rho, p = stats.spearmanr(ok[col], ok[y])
            q = pd.qcut(ok[col], 3, labels=['low', 'mid', 'high']); g = ok.groupby(q, observed=True)[y].median()
            print(f'   {lab:24s} → {ylab:16s} Spearman {rho:+.3f} (p {p:.3f}) · terciles {g["low"]:.2f} / {g["mid"]:.2f} / {g["high"]:.2f}')
    # direction: does a rising-DXY week lean NQ down (contrarian)?
    ok = P.dropna(subset=['dxy1w']); up = ok.dxy1w > 0
    print(f'   NQ up-close (RTH) after a DXY up week {ok[up].up.mean()*100:.0f}% (n{up.sum()}) vs after a DXY down week {ok[~up].up.mean()*100:.0f}% (n{(~up).sum()})')
    for ty in ('NFP', 'CPI', 'FOMC', 'POST', 'PRE', 'HOLLOW'):
        e = P[P.type == ty].dropna(subset=['dxy4w'])
        if len(e) < 10: continue
        up4 = e.dxy4w > 0
        print(f'   {ty:7s} n {len(e):3d}: day range ÷ ADR when DXY 4-week up {e[up4].TDR.median():.2f} (n{up4.sum()}) vs down {e[~up4].TDR.median():.2f} (n{(~up4).sum()}) · |4w| top half {e[e.abs4w > e.abs4w.median()].TDR.median():.2f} vs bottom {e[e.abs4w <= e.abs4w.median()].TDR.median():.2f}')
    # does DXY's own volatility (prior-day range vs its ADR) lead NQ's range?
    P['dxyRel'] = (P.dxyR / P.dxyADR).shift(1)
    ok = P[['dxyRel', 'TDR']].dropna(); rho, p = stats.spearmanr(ok.dxyRel, ok.TDR)
    print(f'   yesterday DXY range ÷ its ADR → NQ day range ÷ ADR: Spearman {rho:+.3f} (p {p:.4f})')
print('\n--- stability by year and weekly-clustered view ---')
for root in ('NQ', 'ES'):
    P = pd.read_pickle(f'prof_{root}.pkl'); P = P[(P.index >= '2023-02-01') & (P.index <= '2026-08-27')]
    P = P.join(d[['dxy1w', 'dxy4w']], how='inner'); P['TDR'] = (P.tdH - P.tdL) / P.tdO / P.adr
    P['yr'] = P.index.year
    s = []
    for y, g in P.groupby('yr'):
        ok = g[['dxy4w', 'TDR']].dropna(); r = stats.spearmanr(ok.dxy4w, ok.TDR)[0]
        up = ok.dxy4w > 0; s.append(f'{y}: ρ {r:+.2f} · up {ok[up].TDR.median():.2f} / down {ok[~up].TDR.median():.2f}')
    print(root, ' | '.join(s))
    # weekly clustering: one row per week (mean day range ratio) vs 4-week change at week start
    P['wk'] = P.index.to_period('W-FRI')
    W = P.groupby('wk').agg(x=('dxy4w', 'first'), y=('TDR', 'mean')).dropna()
    r, p = stats.spearmanr(W.x, W.y); print(f'   weekly: n {len(W)} weeks · Spearman {r:+.3f} (p {p:.4f}) · rising-DXY weeks {W[W.x>0].y.median():.2f} vs falling {W[W.x<=0].y.median():.2f}')
