"""RTH gap research for the RTH gap mapping indicator. NQ + ES + RTY 1-minute 2018–26, all times ET.
RTH gap = prior RTH close (close of the 16:14 bar) → today's 09:30 open, same contract only; early closes (no 16:14 bar)
and roll switches dropped. G = open − prior close (signed). Edges: top = max(open, close), bottom = min.
CE = midpoint. Fill = price trades back to the prior close. ±k SD = k × |G| beyond the top (+) and below the bottom (−);
'cont' = the side beyond the open (gap direction), 'over' = the side beyond the prior close (past the fill).
Windows: same RTH (09:30–16:14); 'staircase life' = until the 5th next 09:30 open (the gap is one of the last 5);
20 sessions = until the 20th next 09:30 open. Size vs average = |G| ÷ mean |G| of the previous 20 gaps (every day kept).
Regime: CPI day / NFP day (08:30 releases, dates from Desgarrón / Gran Rey Cero), else normal.
Writes rg_rows.pkl."""
import json
import numpy as np
import pandas as pd

ND = json.load(open('/home/claude/rg/news_dates.json'))
CPI = set(pd.to_datetime(ND['cpi']))
NFP = set(pd.to_datetime(ND['nfp']))
rows = []
for sym in ('NQ', 'ES', 'RTY'):
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl')[['ts', 'Open', 'High', 'Low', 'Close', 'Contract', 'tday', 'hm']].reset_index(drop=True)
    H, L = b.High.values, b.Low.values
    hm = b.hm.values
    # index of each day's 09:30 bar and 16:14 bar
    i930 = b.index[hm == 930]
    i1614 = b.index[hm == 1614]
    d930 = pd.Series(i930, index=b.tday.values[i930])
    d1614 = pd.Series(i1614, index=b.tday.values[i1614])
    d930 = d930[~d930.index.duplicated()]
    d1614 = d1614[~d1614.index.duplicated()]
    days = list(d930.index)
    opens = list(d930.values)
    hist = []
    for k, td in enumerate(days):
        if k == 0:
            continue
        pd_ = days[k - 1]
        if pd_ not in d1614.index:
            continue
        ic, io = d1614[pd_], d930[td]
        if b.Contract.values[ic] != b.Contract.values[io]:
            continue
        C, O = b.Close.values[ic], b.Open.values[io]
        G = O - C
        g = abs(G)
        avg = np.mean(hist[-20:]) if len(hist) >= 20 else np.nan
        hist.append(g)
        if g <= 0:
            continue
        up = G > 0
        top, bot = max(O, C), min(O, C)
        ce = (O + C) / 2
        # windows
        e_rth = d1614.get(td, np.nan)
        if np.isnan(e_rth):
            continue
        e_rth = int(e_rth) + 1
        e5 = opens[k + 5] if k + 5 < len(opens) else None
        e20 = opens[k + 20] if k + 20 < len(opens) else None

        def reach(a, e):
            hh, ll = H[a:e], L[a:e]
            return dict(ce=bool(ll.min() <= ce) if up else bool(hh.max() >= ce),
                        fill=bool(ll.min() <= C) if up else bool(hh.max() >= C),
                        c1=bool(hh.max() >= top + g) if up else bool(ll.min() <= bot - g),
                        c2=bool(hh.max() >= top + 2 * g) if up else bool(ll.min() <= bot - 2 * g),
                        o1=bool(ll.min() <= bot - g) if up else bool(hh.max() >= top + g),
                        o2=bool(ll.min() <= bot - 2 * g) if up else bool(hh.max() >= top + 2 * g))
        r = dict(sym=sym, tday=td, C=C, O=O, G=G, g=g, pct=100 * g / C, up=up, avg20=avg, ratio=g / avg if avg == avg and avg > 0 else np.nan,
                 cpi=td in CPI, nfp=td in NFP, dow=td.dayofweek)
        for nm, e in (('rth', e_rth), ('w5', e5), ('w20', e20)):
            if e is None:
                continue
            for kk, v in reach(io, e).items():
                r[f'{kk}_{nm}'] = v
        # first-touch minute of CE and fill in RTH (minutes after 09:30)
        hh, ll = H[io:e_rth], L[io:e_rth]
        hitce = np.where(ll <= ce)[0] if up else np.where(hh >= ce)[0]
        hitf = np.where(ll <= C)[0] if up else np.where(hh >= C)[0]
        r['ce_min'] = int(hitce[0]) if len(hitce) else np.nan
        r['fill_min'] = int(hitf[0]) if len(hitf) else np.nan
        # older gaps: after the staircase life (from the 5th next open to the 20th next open)
        if e5 is not None and e20 is not None:
            for kk, v in reach(e5, e20).items():
                r[f'{kk}_5to20'] = v
        rows.append(r)
R = pd.DataFrame(rows)
R['regime'] = np.where(R.cpi, 'CPI', np.where(R.nfp, 'NFP', 'normal'))
R['half'] = np.where(R.tday < '2025-01-01', '18-24', '25-26')
R.to_pickle('/home/claude/rg/rg_rows.pkl')
print(R.groupby('sym').size(), R.regime.value_counts())
