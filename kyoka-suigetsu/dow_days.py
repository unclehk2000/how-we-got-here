"""Day-of-week day table, NQ 1-min (2018 + 2022-Aug 2026). RTH = 09:30-16:14 ET (close of the 16:14 bar).
OR = 09:30-09:44. OR hold = first side broken after 09:45 still beyond at the 16:14 close.
10:00-10:30 reversal (my definition; the sheet's exact rule wasn't written down): the RTH high or low so far is set
inside 10:00-10:29 and price moves >= 40 pts away from it before 10:30."""
import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
rows = []
for d, x in b.groupby('tday'):
    r = x[(x.hm >= 930) & (x.hm <= 1614)]
    if len(r) < 350 or r.hm.iloc[0] != 930 or r.hm.iloc[-1] != 1614: continue
    o, c = r.Open.iloc[0], r.Close.iloc[-1]; H, L = r.High.max(), r.Low.min()
    orb = r[r.hm <= 944]; oh, ol = orb.High.max(), orb.Low.min()
    aft = r[r.hm >= 945]; up_i = np.argmax(aft.High.values > oh) if (aft.High.values > oh).any() else None
    dn_i = np.argmax(aft.Low.values < ol) if (aft.Low.values < ol).any() else None
    first = None
    if up_i is not None and (dn_i is None or up_i < dn_i): first = 1
    elif dn_i is not None and (up_i is None or dn_i < up_i): first = -1
    hold = np.nan if first is None else float(c > oh if first > 0 else c < ol)
    w = r[(r.hm >= 1000) & (r.hm <= 1029)]; pre = r[r.hm < 1000]
    rev = False
    hi_run, lo_run = pre.High.max(), pre.Low.min()
    for hh, ll in zip(w.High.values, w.Low.values):
        if hh > hi_run: hi_run = hh; top_new = True
        if ll < lo_run: lo_run = ll
    # reversal off a high/low set inside the window
    wh, wl = w.High.values, w.Low.values
    for i in range(len(w)):
        if wh[i] >= max(pre.High.max(), wh[:i + 1].max()) and (wh[i] - wl[i:].min()) >= 40: rev = True; break
        if wl[i] <= min(pre.Low.min(), wl[:i + 1].min()) and (wh[i:].max() - wl[i]) >= 40: rev = True; break
    hi_hr = r.hm.values[r.High.values.argmax()] // 100; lo_hr = r.hm.values[r.Low.values.argmin()] // 100
    rows.append(dict(tday=d, year=d.year, dow=d.dayofweek, o=o, c=c, rng=100 * (H - L) / o, net=100 * (c - o) / o, up=c > o,
                     or_first=first, or_hold=hold, rev=rev, hi_hr=hi_hr, lo_hr=lo_hr, rng_pts=H - L))
D = pd.DataFrame(rows); D = D[D.dow <= 4]; D['sp'] = np.where(D.year >= 2025, '2025-26', '2018-24')
D.to_pickle('/home/claude/byk/dow_D.pkl'); print(D.shape, D.groupby('year').size().to_dict())
