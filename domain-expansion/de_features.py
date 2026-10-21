"""Feature set for predicting a Domain Expansion day (04:59 close >= 0.3% beyond the 02:00-02:29 range).
Every feature uses only data available at the 02:29 close. Times ET unless noted (UK = ET + 5h most of the year)."""
import pandas as pd, numpy as np, datetime as dt
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
FOMC = pd.to_datetime(['2018-01-31','2018-03-21','2018-05-02','2018-06-13','2018-08-01','2018-09-26','2018-11-08','2018-12-19',
 '2022-01-26','2022-03-16','2022-05-04','2022-06-15','2022-07-27','2022-09-21','2022-11-02','2022-12-14',
 '2023-02-01','2023-03-22','2023-05-03','2023-06-14','2023-07-26','2023-09-20','2023-11-01','2023-12-13',
 '2024-01-31','2024-03-20','2024-05-01','2024-06-12','2024-07-31','2024-09-18','2024-11-07','2024-12-18',
 '2025-01-29','2025-03-19','2025-05-07','2025-06-18','2025-07-30','2025-09-17','2025-10-29','2025-12-10',
 '2026-01-28','2026-03-18','2026-04-29','2026-06-17','2026-07-29','2026-09-16','2026-10-28','2026-12-09'])
def nth_sunday(y, m, n):
    d = dt.date(y, m, 1); d += dt.timedelta(days=(6 - d.weekday()) % 7); return d + dt.timedelta(weeks=n - 1)
def last_sunday(y, m):
    d = dt.date(y, m + 1, 1) - dt.timedelta(days=1); return d - dt.timedelta(days=(d.weekday() + 1) % 7)
def mismatch(day):
    y = day.year; d = day.date()
    return (nth_sunday(y, 3, 2) <= d < last_sunday(y, 3)) or (last_sunday(y, 10) <= d < nth_sunday(y, 11, 1))
def seg(x, a, z): return x[(x.hm >= a) & (x.hm <= z)]
def rng(s): return s.High.max() - s.Low.min() if len(s) else np.nan
rows = []; prev = None; nw = dict(lo=np.nan, hi=np.nan, wk=None)
for d, x in b.groupby('tday'):
    ev = x[x.hm >= 1800]; mo_ = seg(x, 0, 229)
    on = pd.concat([ev, mo_]); lor = seg(x, 200, 229); c5 = x[x.hm == 459]; c1659 = x[x.hm == 1659]
    ok = len(lor) >= 28 and len(c5) == 1 and len(on) > 300 and len(ev) > 0 and ev.hm.iloc[0] == 1800
    if ok and prev is not None:
        P = lor.Close.iloc[-1]; H, L = lor.High.max(), lor.Low.min(); R = H - L; C5 = c5.Close.iloc[0]
        o18 = ev.Open.iloc[0]; pc = prev['c1659']
        asia = ev[ev.hm >= 2000]; mid = x[x.hm == 0]; MO = mid.Open.iloc[0] if len(mid) else np.nan
        pct = lambda v: 100 * v / P
        # NWOG: first session of a new ISO week
        wk = d.isocalendar()[:2]
        if wk != nw['wk']:
            nw = dict(lo=min(pc, o18), hi=max(pc, o18), wk=wk)
        nce = (nw['lo'] + nw['hi']) / 2
        onH, onL = on.High.max(), on.Low.min()
        f = dict(tday=d, year=d.year, exp=(C5 >= H * 1.003) or (C5 <= L * 0.997),
                 expDir=1 if C5 >= H * 1.003 else (-1 if C5 <= L * 0.997 else 0),
                 # baseline volatility (true range overnight, today)
                 on_tr=pct(max(onH, pc) - min(onL, pc)),
                 # settlement window prior day 16:14 -> 16:59 ET (21:14-21:59 UK)
                 sw_net=pct(prev['c1659'] - prev['c1614']), sw_abs=abs(pct(prev['c1659'] - prev['c1614'])), sw_rng=pct(prev['sw_rng']),
                 # NDOG and NWOG
                 ndog=pct(o18 - pc), ndog_abs=abs(pct(o18 - pc)),
                 nwog_size=pct(nw['hi'] - nw['lo']), nwog_ce_dist=pct(P - nce),
                 nwog_inside=float(nw['lo'] <= P <= nw['hi']), week_first=float(wk != prev['wk']),
                 # true day open (00:00 ET)
                 mo_dist=pct(P - MO), mo_abs=abs(pct(P - MO)), mo_in_lor=float(L <= MO <= H) if not np.isnan(MO) else np.nan,
                 # hour ranges: 23:00-23:59 ET, and 18:00-18:59 ET (= 23:00-00:00 UK)
                 r2300=pct(rng(seg(x, 2300, 2359))), r1800=pct(rng(seg(x, 1800, 1859))),
                 # CBDR (14:00-20:00) and flout (15:00-00:00)
                 cbdr=pct(max(prev['h1400'], seg(x, 1800, 1959).High.max()) - min(prev['l1400'], seg(x, 1800, 1959).Low.min())),
                 flout=pct(max(prev['h1500'], seg(x, 1800, 2359).High.max()) - min(prev['l1500'], seg(x, 1800, 2359).Low.min())),
                 # Asia
                 asia=pct(rng(asia)), asia_sw_lor=float((H > asia.High.max()) or (L < asia.Low.min())),
                 # LOR geometry
                 lor_pct=pct(R), lor_oct=(P - L) / R if R > 0 else 0.5, lor_vs_asia=R / rng(asia) if rng(asia) > 0 else np.nan,
                 # overnight path
                 on_move=pct(P - o18), on_pos=(P - onL) / (onH - onL) if onH > onL else 0.5,
                 # prior-day liquidity
                 pdh_dist=pct(prev['H'] - P), pdl_dist=pct(P - prev['L']),
                 pdh_swept=float(onH > prev['H']), pdl_swept=float(onL < prev['L']),
                 # prior day
                 pd_rng=pct(prev['H'] - prev['L']), pd_ret=pct(prev['c1659'] - prev['o18']), pd_clv=(prev['c1659'] - prev['L']) / (prev['H'] - prev['L']),
                 pd_rth_rng=pct(prev['rth_rng']), pd_exp=float(prev['exp']),
                 # daily structure vs the day before
                 st_bull=float(prev['H'] > prev['pH'] and prev['L'] > prev['pL']), st_bear=float(prev['H'] < prev['pH'] and prev['L'] < prev['pL']),
                 st_inside=float(prev['H'] <= prev['pH'] and prev['L'] >= prev['pL']), st_outside=float(prev['H'] > prev['pH'] and prev['L'] < prev['pL']),
                 # calendar / events
                 dow=d.dayofweek, mon=float(d.dayofweek == 0), fri=float(d.dayofweek == 4),
                 fomc=float(d in FOMC), fomc_eve=float((d + pd.offsets.BDay(1)) in FOMC),
                 nfp=float(d.dayofweek == 4 and d.day <= 7), dst_mis=float(mismatch(d)), month=d.month,
                 P=P, c1659=c1659.Close.iloc[0] if len(c1659) else np.nan)
        rows.append(f)
    if len(c1659) and ok:
        rth = seg(x, 930, 1614); swb = seg(x, 1615, 1659); c1614 = x[x.hm == 1614]
        prev = dict(c1659=c1659.Close.iloc[0], c1614=c1614.Close.iloc[0] if len(c1614) else np.nan, sw_rng=rng(swb),
                    H=x.High.max(), L=x.Low.min(), o18=ev.Open.iloc[0], rth_rng=rng(rth),
                    h1400=seg(x, 1400, 1659).High.max(), l1400=seg(x, 1400, 1659).Low.min(),
                    h1500=seg(x, 1500, 1659).High.max(), l1500=seg(x, 1500, 1659).Low.min(),
                    pH=prev['H'] if prev else np.nan, pL=prev['L'] if prev else np.nan, wk=d.isocalendar()[:2],
                    exp=(c5.Close.iloc[0] >= lor.High.max() * 1.003) or (c5.Close.iloc[0] <= lor.Low.min() * 0.997))
    elif not ok:
        prev = None if prev is None else prev   # keep last good prior day
F = pd.DataFrame(rows).sort_values('tday').reset_index(drop=True)
# rolling features (prior days only, except ATR5 which includes today's overnight, known at 02:30)
# rolling windows never span the 2019-21 data gap: compute inside contiguous blocks
F['blk'] = (F.tday.diff().dt.days > 10).cumsum()
F['cl'] = F.groupby('blk').c1659.ffill()
def roll(g):
    g = g.copy()
    g['atr5'] = g.on_tr.rolling(5).mean()
    pc = g.cl.shift(1)
    g['ret5'] = (pc / pc.shift(5) - 1) * 100
    g['ret20'] = (pc / pc.shift(20) - 1) * 100
    hi20 = pc.rolling(20).max(); lo20 = pc.rolling(20).min()
    g['pos20'] = (g.P - lo20) / (hi20 - lo20)
    g['vol5'] = g.pd_rng.rolling(5).mean()
    for c in ['lor_pct', 'asia', 'sw_rng', 'r2300', 'r1800', 'cbdr']:
        g[c + '_rel'] = g[c] / g[c].shift(1).rolling(20, min_periods=15).mean()
    return g
F = pd.concat([roll(g) for _, g in F.groupby('blk')])
F['sp'] = np.where(F.year >= 2025, 'test', 'train')
F = F.dropna(subset=['atr5', 'ret20', 'pos20']).reset_index(drop=True)
F.to_pickle('/home/claude/byk/de_F.pkl')
print(F.shape, F.groupby('sp').exp.agg(['mean', 'size']).round(3).to_dict())
print('NaN share per feature (top):', F.isna().mean().sort_values(ascending=False).head(6).round(3).to_dict())
