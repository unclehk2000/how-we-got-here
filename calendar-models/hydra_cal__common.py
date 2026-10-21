"""Shared loaders for the economic-calendar HYDRA studies (NFP day, NFP week Mon–Thu, day after FOMC).
1-minute front-month bars in ET grouped by CME trading day (18:00 → 17:00); per-day context (O H L C, ADR20 in points,
month open, prior day high / low, ATH) from Senbonzakura's ctx tables; release dates from Vizard."""
import numpy as np, pandas as pd, re, pickle, os
S = open('/home/claude/hm/Vizard.pine', encoding='utf-8').read()
def dates(name, nxt):
    blk = S[S.index(name + ' '):S.index(nxt + ' ')]
    return sorted(set(pd.Timestamp(x) for x in re.findall(r'20\d{6}', blk)))
FO, CP, NP = dates('S_FOMC', 'S_CPI'), dates('S_CPI', 'S_NFP'), dates('S_NFP', 'LAST_DATE')
M = lambda hh, mm: ((hh * 60 + mm) - 1080) % 1440                         # minutes after 18:00
VIX = pd.read_csv('/home/claude/mac/vix_daily.csv', parse_dates=['DATE']).set_index('DATE').CLOSE
def days(sym):
    """{tday: dict(m, O, H, L, C)} cached"""
    p = f'/home/claude/hm/hydra_cal/days_{sym}.pkl'
    if os.path.exists(p): return pickle.load(open(p, 'rb'))
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl')
    hm = b.hm.values; b = b.assign(m=((hm // 100) * 60 + hm % 100 - 1080) % 1440)
    G = {}
    for td, g in b.groupby('tday'):
        G[td] = dict(m=g.m.values, O=g.Open.values, H=g.High.values, L=g.Low.values, C=g.Close.values)
    pickle.dump(G, open(p, 'wb')); return G
class Day:
    def __init__(self, g): self.m, self.O, self.H, self.L, self.C = g['m'], g['O'], g['H'], g['L'], g['C']
    def full(self): return self.m[0] <= 5 and self.m[-1] >= 1375
    def c(self, hh, mi):                       # close of the bar at hh:mi (or the last one before)
        k = np.searchsorted(self.m, M(hh, mi), side='right') - 1; return self.C[k] if k >= 0 else np.nan
    def o(self, hh, mi):                       # open of the bar at hh:mi (or the first one after, within 2 min)
        k = np.searchsorted(self.m, M(hh, mi), side='left')
        return self.O[k] if k < len(self.m) and self.m[k] <= M(hh, mi) + 2 else np.nan
    def rng(self, a, b):                       # high, low of bars a (inclusive) … b (exclusive), minutes after 18:00
        s = (self.m >= a) & (self.m < b)
        return (self.H[s].max(), self.L[s].min()) if s.any() else (np.nan, np.nan)
def ctx(sym): return pd.read_pickle(f'/home/claude/hm/senbon/ctx_{sym}.pkl')
def day_type(D_index):
    """Vizard's dayType: 0 FOMC · 1 NFP · 2 CPI · 3 day after FOMC · 4 FOMC day 1 · 5 NFP week Mon–Thu · 6 normal"""
    idx = list(D_index); out = {}
    fo, np_, cp = set(FO), set(NP), set(CP)
    for i, d in enumerate(idx):
        pk = idx[i - 1] if i > 0 else None
        dw = d.dayofweek                                         # Mon 0 … Fri 4
        hol = dw <= 3 and any((d + pd.Timedelta(days=j)) in np_ for j in range(1, 5 - dw))
        nxt = d + pd.Timedelta(days=1)
        out[d] = 0 if d in fo else 1 if d in np_ else 2 if d in cp else 3 if pk in fo else 4 if nxt in fo else 5 if hol else 6
    return pd.Series(out)
def common_feats(D, i, c, preH, preL, d):
    """features shared by every study: price c at the snapshot, the day's high / low so far"""
    A = D.adr.iloc[i]; MO = D.MO.iloc[i]
    mon = D[(D.index.year == d.year) & (D.index.month == d.month) & (D.index < d)]
    mH = max(mon.H.max() if len(mon) else -np.inf, preH); mL = min(mon.L.min() if len(mon) else np.inf, preL)
    wk0 = d - pd.Timedelta(days=d.dayofweek); wk = D[(D.index >= wk0) & (D.index < d)]
    WO = wk.O.iloc[0] if len(wk) else D.O.iloc[i]
    wH = max(wk.H.max() if len(wk) else -np.inf, preH); wL = min(wk.L.min() if len(wk) else np.inf, preL)
    PDH, PDL = D.PDH.iloc[i], D.PDL.iloc[i]
    vp = VIX[VIX.index < d]; v = vp.iloc[-1] if len(vp) else np.nan; va = vp.iloc[-20:].mean() if len(vp) >= 20 else np.nan
    pdPos = (c - PDL) / (PDH - PDL) if PDH > PDL else np.nan
    moPos = (c - mL) / (mH - mL) if mH > mL else np.nan
    return dict(adr=A, price=c, moPos=moPos, dMO=(c - MO) / A, wkPos=(c - wL) / (wH - wL) if wH > wL else np.nan, dWO=(c - WO) / A,
                pdPos=pdPos, pdRng=(PDH - PDL) / A, pdDir=np.sign(D.C_TD.iloc[i - 1] - D.O.iloc[i - 1]),
                t5=(c - D.C_TD.iloc[i - 5]) / A, t20=(c - D.C_TD.iloc[i - 20]) / A, adrPct=A / c * 100,
                athDist=(max(D.ATHp.iloc[i], preH) - c) / A, vix=v, vixRel=v / va - 1 if va else np.nan, dom=d.day, dow=d.dayofweek,
                moPrem=float(moPos >= 0.75), moDisc=float(moPos <= 0.25), abovePDH=float(pdPos > 1), belowPDL=float(pdPos < 0),
                PDH=PDH, PDL=PDL, MO=MO)
