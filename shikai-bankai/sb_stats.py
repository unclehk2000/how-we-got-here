"""SB Map card research. NQ + ES + RTY 1-minute 2018–26, ET. Per trading day (18:00 → 16:59):
overnight range 18:00–09:29 → mid; 09:30 open; mirror = the same distance on the other side of the open.
Reach times of the mid and the mirror from 09:30 (minutes); London 02:00–04:59 high / low and when they are taken after 05:00;
session ranges (Asia 18:00–23:59, London 02:00–04:59, NY 08:00–16:59) against ADR20. Writes sb_rows.pkl."""
import numpy as np, pandas as pd
rows = []
for sym in ('NQ', 'ES', 'RTY'):
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl')[['ts', 'Open', 'High', 'Low', 'Close', 'tday', 'hm']]
    b['m'] = (b.hm // 100) * 60 + b.hm % 100
    day = b.groupby('tday').agg(H=('High', 'max'), L=('Low', 'min'))
    adr = (day.H - day.L).rolling(20).mean().shift(1)
    for td, g in b.groupby('tday'):
        ev = g[g.m >= 1080]; early = g[g.m < 1080]
        on = pd.concat([ev, early[early.m < 570]])
        rth = early[(early.m >= 570) & (early.m < 1020)]
        if len(on) < 600 or len(rth) < 400 or rth.m.iloc[0] != 570 or np.isnan(adr.get(td, np.nan)):
            continue
        A = adr[td]
        oH, oL = on.High.max(), on.Low.min(); mid = (oH + oL) / 2
        O = rth.Open.iloc[0]; up = mid > O; d = abs(mid - O); mir = 2 * O - mid
        hh, ll = rth.High.values, rth.Low.values
        hm_ = np.where(hh >= mid)[0] if up else np.where(ll <= mid)[0]
        hr = np.where(ll <= mir)[0] if up else np.where(hh >= mir)[0]
        lon = early[(early.m >= 120) & (early.m < 300)]
        after = early[(early.m >= 300) & (early.m < 1020)]
        asia = ev[ev.m < 1440] if len(ev) else ev
        ny = early[(early.m >= 480) & (early.m < 1020)]
        r = dict(sym=sym, tday=td, adr=A, O=O, mid=mid, up=up, d=d, dA=d / A, dP=100 * d / O,
                 tMid=int(hm_[0]) if len(hm_) else np.nan, tMir=int(hr[0]) if len(hr) else np.nan)
        if len(lon) > 150 and len(after) > 600:
            lH, lL = lon.High.max(), lon.Low.min()
            th = after[after.High > lH]; tl = after[after.Low < lL]
            r.update(lH=lH, lL=lL, tLH=int(th.m.iloc[0]) if len(th) else np.nan, tLL=int(tl.m.iloc[0]) if len(tl) else np.nan,
                     rL=(lH - lL) / A)
        if len(asia) > 300:
            r['rA'] = (asia.High.max() - asia.Low.min()) / A
        if len(ny) > 500:
            r['rN'] = (ny.High.max() - ny.Low.min()) / A
        rows.append(r)
R = pd.DataFrame(rows)
R['half'] = np.where(R.tday < '2025-01-01', '18-24', '25-26')
R.to_pickle('/home/claude/sb/sb_rows.pkl')
print(len(R), R.groupby('sym').size().to_dict())
print('dA quantiles', R.dA.quantile([.1, .2, .3, .4, .5, .6, .7, .8, .9]).round(3).to_dict())
print('dP quantiles', R.dP.quantile([.2, .4, .5, .6, .8]).round(3).to_dict())
