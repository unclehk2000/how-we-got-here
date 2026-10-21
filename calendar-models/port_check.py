"""Port of the Pine logic: ADR20 from 15-minute bars (adrCalc) and dayType, compared with the research tables."""
import pandas as pd, numpy as np, datetime as dt
from events import FOMC, CPI, NFP
b = pd.read_pickle('/home/claude/t3/bars_NQ_all.pkl')
b = b[b.ts >= '2025-06-01']
b15 = b.set_index('ts').resample('15min', label='left', closed='left').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}).dropna().reset_index()
def dkey(t): return t.year * 10000 + t.month * 100 + t.day
def akey(an, t): return dkey(t + pd.Timedelta(hours=6)) if an == 0 else dkey(t)
def inwin(an, m): return True if an == 0 else (m < 1020 if an == 1 else (570 <= m < 975))
WB = {0: 92, 1: 68, 2: 27}
D = pd.read_pickle('days_NQ.pkl')
FO = set(int(d.strftime('%Y%m%d')) for d in FOMC); NP = set(int(d.strftime('%Y%m%d')) for d in NFP); CP = set(int(d.strftime('%Y%m%d')) for d in CPI)
def addd(k, n):
    d = dt.date(k // 10000, (k // 100) % 100, k % 100) + dt.timedelta(days=n); return d.year * 10000 + d.month * 100 + d.day
def dtype(k, pk):
    d = dt.date(k // 10000, (k // 100) % 100, k % 100); dow = (d.weekday() + 1) % 7 + 1   # Pine: Sun=1..Sat=7
    hol = any(addd(k, j) in NP for j in range(1, 6 - dow + 1)) if 2 <= dow <= 5 else False
    return 'FOMC' if k in FO else 'NFP' if k in NP else 'CPI' if k in CP else 'POST' if pk in FO else 'PRE' if addd(k, 1) in FO else 'HOLLOW' if hol else 'NORMAL'
for an, nm in ((0, 'TD'), (1, 'MID'), (2, 'RTH')):
    rs = []; o = h = l = None; n = 0; piw = None; pdk = None; adr_at = {}; prevk = None; types = {}
    for r in b15.itertuples():
        m = r.ts.hour * 60 + r.ts.minute; dk = akey(an, r.ts); iw = inwin(an, m)
        st = iw and ((not piw) or dk != pdk)
        if st:
            if o is not None and n >= 0.94 * WB[an] and o > 0:
                rs.append((h - l) / o); rs = rs[-20:]
            o, h, l, n = r.Open, r.High, r.Low, 1
            adr_at[dk] = np.mean(rs) if len(rs) >= 15 else np.nan
            types[dk] = dtype(dk, prevk); prevk = dk
        elif iw and o is not None:
            h = max(h, r.High); l = min(l, r.Low); n += 1
        piw, pdk = iw, dk
    A = D[D.anchor == nm].copy(); A['k'] = A.tday.dt.strftime('%Y%m%d').astype(int)
    A['adr_pine'] = A.k.map(adr_at); A['type_pine'] = A.k.map(types)
    A = A.dropna(subset=['adr_pine'])
    A = A[A.tday >= '2025-08-01']
    rel = (A.adr_pine / A.adr - 1).abs()
    print(f'{nm}: days {len(A)} · ADR Pine vs research: median |diff| {rel.median()*100:.3f}% · max {rel.max()*100:.2f}% · type agreement {(A.type_pine == A.type).mean()*100:.1f}%')
    bad = A[A.type_pine != A.type]
    if len(bad): print('   type mismatches:', bad[['tday', 'type', 'type_pine']].head(8).to_string(index=False))
