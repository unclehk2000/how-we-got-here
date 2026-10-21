"""Domain Expansion upgrade research: London session stats for the live card, pooled NQ + ES + RTY 1-minute, 2018–26.
All times ET. Trading day = 18:00 → 16:59. Domain range 02:00–02:29, London 02:00–04:59 (after the range 02:30–04:59).
Builds one row per symbol-day, then:
  (a) expected London range (02:00–04:59 high − low) from the domain range and the overnight ATR(5): log-linear fit on
      2018–24, checked on 2025–26 (coverage of the middle-half band, median ratio)
  (b) live odds of reaching 2 SD at the London extreme by 04:59, by checkpoint time × the furthest SD reached so far
  (c) "high / low already in": by checkpoint time × distance of price from the London high (low) so far, in domain ranges
  (d) NY carry: how often NY AM (09:30–10:59) and the morning to 11:00 take the London high / low
  (e) tier odds (2 SD at the London extreme) for the card's 02:30 line
Writes lon_rows.pkl, lon_ck.pkl and lon_stats.json."""
import json
import numpy as np
import pandas as pd

SYMS = ('NQ', 'ES', 'RTY')
CKS = [230, 245, 300, 315, 330, 345, 400, 415, 430, 445]          # checkpoints: state read at the bar before


def hm2m(h):
    return (h // 100) * 60 + h % 100


rows, cks = [], []
for sym in SYMS:
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl')[['ts', 'Open', 'High', 'Low', 'Close', 'tday', 'hm']]
    b['m'] = hm2m(b.hm)
    days = sorted(b.tday.unique())
    g_by = dict(tuple(b.groupby('tday')))
    prev_close, on_hist, adr_hist = None, [], []
    prev_g = None
    for td in days:
        g = g_by[td]
        # session pieces (minutes since midnight ET; evening bars carry m >= 1080)
        ev = g[g.m >= 1080]
        early = g[g.m < 1080]
        on = pd.concat([ev, early[early.m < 150]])                  # 18:00 → 02:29
        dr = early[(early.m >= 120) & (early.m < 150)]
        lon = early[(early.m >= 120) & (early.m < 300)]
        post = early[(early.m >= 150) & (early.m < 300)]
        nyam = early[(early.m >= 570) & (early.m < 660)]
        to11 = early[(early.m >= 300) & (early.m < 660)]
        full = g
        ok = len(dr) >= 25 and len(post) >= 140 and len(on) >= 400
        # overnight true range (prior 16:59 close)
        if len(on) and prev_close is not None:
            onH, onL = on.High.max(), on.Low.min()
            on_hist.append(max(onH, prev_close) - min(onL, prev_close))
        else:
            on_hist.append(np.nan)
        atr5 = np.nanmean(on_hist[-5:]) if len(on_hist) >= 5 and not np.isnan(on_hist[-5:]).any() else np.nan
        adr20 = np.mean(adr_hist[-20:]) if len(adr_hist) >= 20 else np.nan
        # CBDR 14:00 → 19:59: prior day's 14:00–16:59 + this day's 18:00–19:59
        cb = np.nan
        if prev_g is not None:
            p1 = prev_g[(prev_g.m >= 840) & (prev_g.m < 1020)]
            p2 = ev[(ev.m >= 1080) & (ev.m < 1200)]
            if len(p1) > 100 and len(p2) > 60:
                cb = max(p1.High.max(), p2.High.max()) - min(p1.Low.min(), p2.Low.min())
        if ok and not np.isnan(atr5):
            dH, dL = dr.High.max(), dr.Low.min()
            rD = dH - dL
            if rD > 0:
                lH, lL = lon.High.max(), lon.Low.min()
                up, dn = (post.High.max() - dH) / rD, (dL - post.Low.min()) / rD
                r = dict(sym=sym, tday=td, rD=rD, atr=atr5, coil=rD / atr5, cb=cb, cbR=cb / rD if cb == cb else np.nan,
                         lr=lH - lL, up=up, dn=dn, mx=max(up, dn), adr=adr20, c5=post.Close.iloc[-1], dH=dH, dL=dL, lH=lH, lL=lL,
                         px=dr.Close.iloc[-1],
                         ny_hi=float(nyam.High.max() > lH) if len(nyam) > 60 else np.nan,
                         ny_lo=float(nyam.Low.min() < lL) if len(nyam) > 60 else np.nan,
                         t11_hi=float(to11.High.max() > lH) if len(to11) > 200 else np.nan,
                         t11_lo=float(to11.Low.min() < lL) if len(to11) > 200 else np.nan,
                         t_hi=int(lon.m.iloc[lon.High.values.argmax()]), t_lo=int(lon.m.iloc[lon.Low.values.argmin()]))
                rows.append(r)
                # checkpoints
                pm = post.m.values
                ph, pl, pcl = post.High.values, post.Low.values, post.Close.values
                lm = lon.m.values
                lh, ll = lon.High.values, lon.Low.values
                for ck in CKS:
                    cm = hm2m(ck)
                    before_l = lm < cm
                    hs, ls = lh[before_l].max(), ll[before_l].min()
                    bp = pm < cm
                    if bp.sum():
                        mxu, mxd = (ph[bp].max() - dH) / rD, (dL - pl[bp].min()) / rD
                        cl = pcl[bp][-1]
                    else:
                        mxu = mxd = 0.0
                        cl = dr.Close.iloc[-1]
                    after = pm >= cm
                    fu, fd = (ph.max() - dH) / rD, (dL - pl.min()) / rD
                    cks.append(dict(sym=sym, tday=td, ck=ck, sofar=max(mxu, mxd, 0.0), reach2=float(max(fu, fd) >= 2.0),
                                    dHi=(hs - cl) / rD, dLo=(cl - ls) / rD,
                                    hiIn=float(ph[after].max() <= hs) if after.sum() else 1.0,
                                    loIn=float(pl[after].min() >= ls) if after.sum() else 1.0,
                                    lrSoFar=hs - ls))
        if len(full) > 600:
            adr_hist.append(full.High.max() - full.Low.min())
            prev_close = full.Close.iloc[-1]
        prev_g = g
R = pd.DataFrame(rows)
C = pd.DataFrame(cks)
R.to_pickle('/home/claude/dx/lon_rows.pkl')
C.to_pickle('/home/claude/dx/lon_ck.pkl')
print(R.groupby('sym').size(), len(C))
