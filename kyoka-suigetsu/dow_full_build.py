"""Per-day tables from the merged NQ set (2018-2026): full trading day (18:00-16:59 ET) and the 09:30-16:14 window,
plus the running range / net at the end of each hour slot (18:00 ... 16:00), as the indicator stores them."""
import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ_full.pkl').sort_values('ts')
SLOTS = [18,19,20,21,22,23,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
rows, cum = [], []
for d, x in b.groupby('tday'):
    if len(x) < 1000 or d.dayofweek > 4: continue
    o = x.Open.iloc[0]; H = x.High.values; L = x.Low.values; C = x.Close.values; hr = (x.hm.values // 100)
    rh = np.maximum.accumulate(H); rl = np.minimum.accumulate(L)
    cr, cn = [], []
    for s in SLOTS:
        idx = np.where(hr == s)[0]
        if len(idx): k = idx[-1]; cr.append(100 * (rh[k] - rl[k]) / o); cn.append(100 * (C[k] - o) / o)
        else: cr.append(cr[-1] if cr else 0.0); cn.append(cn[-1] if cn else 0.0)
    r = x[(x.hm >= 930) & (x.hm <= 1614)]
    rows.append(dict(tday=d, year=d.year, dow=d.dayofweek, o=o, H=H.max(), L=L.min(), c=C[-1],
                     rng=100 * (H.max() - L.min()) / o, net=100 * (C[-1] - o) / o,
                     hi_hr=x.hm.values[H.argmax()] // 100, lo_hr=x.hm.values[L.argmin()] // 100,
                     rth_rng=100 * (r.High.max() - r.Low.min()) / r.Open.iloc[0] if len(r) > 350 else np.nan,
                     rth_net=100 * (r.Close.iloc[-1] - r.Open.iloc[0]) / r.Open.iloc[0] if len(r) > 350 else np.nan))
    cum.append(cr + cn)
F = pd.DataFrame(rows)
C = pd.DataFrame(cum, columns=[f'r{s}' for s in SLOTS] + [f'n{s}' for s in SLOTS])
F = pd.concat([F, C], axis=1)
# daily true range / ATR14 from completed days (prior close available within the set)
F['pc'] = F.c.shift(1)
F['tr'] = np.maximum(F.H, F.pc) - np.minimum(F.L, F.pc)
F['atr14'] = F.tr.rolling(14).mean().shift(1)
F['sp'] = np.where(F.year >= 2025, '2025-26', '2018-24')
F.to_pickle('/home/claude/byk/dow_full.pkl')
print(F.shape, F.groupby('year').size().to_dict())
