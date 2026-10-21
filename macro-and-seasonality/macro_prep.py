"""Daily NQ / ES frame with macro features known before each trading day (HYDRA rule: nothing from the future).
Sources: NQ / ES 1-minute days (days_*.pkl, trading day 18:00 → 17:00 ET, ADR20 known before the day),
VIX daily close (CBOE via datasets/finance-vix, 1990 → Sep 2026), DXY rebuilt daily from the Fed H.10 noon rates with
the ICE weights (datasets/exchange-rates, 1999 → Oct 2026; daily changes correlate 0.987 with DXY futures),
US 10Y monthly average yield (datasets/bond-yields-us-10y, FRED GS10, 1953 → Aug 2026).
Writes macro_NQ.pkl / macro_ES.pkl."""
import pandas as pd, numpy as np
HM = '/home/claude/hm/'
vix = pd.read_csv('vix_daily.csv', parse_dates=['DATE']).set_index('DATE').CLOSE.rename('vix')
dxy = pd.read_pickle('dxy_rec.pkl').dxy
y10 = pd.read_csv('bond-yields-us-10y/data/monthly.csv', parse_dates=['Date']).set_index('Date').Rate.rename('y10')

def known_before(s, idx):
    """value of series s on the last date strictly before each trading day in idx"""
    s = s.sort_index(); pos = s.index.searchsorted(idx, side='left') - 1
    out = np.where(pos >= 0, s.values[np.clip(pos, 0, None)], np.nan)
    return pd.Series(out, index=idx)

# VIX features
v20 = vix.rolling(20).mean(); vrank = vix.rolling(252).apply(lambda a: (a[:-1] < a[-1]).mean(), raw=True)
# DXY weekly (Friday) 4-week change and 1-week change, and DXY 20-day realised vol vs its 1-year median
wk = dxy.resample('W-FRI').last().dropna()
dx4w = np.log(wk).diff(4); dx1w = np.log(wk).diff(1)
dret = np.log(dxy).diff(); dvol = dret.rolling(20).std() * np.sqrt(252)
dvolRel = np.log(dvol / dvol.rolling(252).median())
# 10Y: last completed month's change (month m-1 vs m-2), known through month m
y10c = y10.diff()

for root in ('NQ', 'ES'):
    D = pd.read_pickle(HM + f'days_{root}.pkl'); T = D[D.anchor == 'TD'].set_index('tday').sort_index().copy()
    T['lR'] = np.log(T.R)
    for k in (1, 2, 3): T[f'lR{k}'] = T.lR.shift(k)
    T['dow'] = T.index.dayofweek; T['mon'] = T.index.month
    idx = T.index
    T['vix'] = known_before(vix, idx); T['vix20'] = known_before(v20, idx); T['vrank'] = known_before(vrank, idx)
    T['vixD'] = vix.reindex(idx).values                       # same-day VIX close (descriptive only)
    T['vixPrev'] = T.vix
    T['ivrv'] = np.log(T.vix / np.sqrt(252)) - np.log(T.adr * 100)      # implied daily sigma vs ADR20
    T['vspike'] = np.log(T.vix / T.vix20)
    T['dx4'] = known_before(dx4w.shift(0), idx); T['dx1'] = known_before(dx1w, idx)
    # Pine uses the last COMPLETED week: a Friday value is known from the following Monday (strictly before the day)
    T['dvol'] = known_before(dvolRel, idx)
    T['dxD'] = (np.log(dxy).diff()).reindex(idx).values              # same-day DXY change (noon to noon, descriptive)
    m = idx.to_period('M')
    yc = y10c.copy(); yc.index = yc.index.to_period('M')
    T['y10m'] = [yc.get(p - 1, np.nan) for p in m]                     # last completed month's change, in % points
    T['y10'] = [y10.get((p - 1).to_timestamp(), np.nan) for p in m]
    # targets
    T['RTHup'] = np.nan
    P = pd.read_pickle(HM + f'prof_{root}.pkl')
    if 'rthO' in P.columns:
        T['RTHup'] = (P.rthC > P.rthO).astype(float).reindex(idx)
        T['rthR'] = (P.rthR / (P.adr * P.tdO)).reindex(idx) if 'rthR' in P.columns else np.nan
    T['vixChg'] = np.log(T.vixD / T.vixPrev)
    T.to_pickle(f'macro_{root}.pkl')
    print(root, len(T), T[['vix', 'ivrv', 'vspike', 'dx4', 'dvol', 'y10m']].describe().loc[['count', 'mean', 'std']].round(3).to_string())
