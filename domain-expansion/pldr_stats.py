"""Pre-London dealing range (00:00–00:59 ET) for Domain Expansion v9. NQ + ES + RTY 1-minute 2018–26, all times ET.
Per trading day: the range high / low / CE (midpoint), then how often price takes the high / low (trades beyond it)
  - before London (01:00–01:59), and
  - by the end of London (01:00–04:59), and in London itself (02:00–04:59)
plus how often London trades through the CE, and whether the domain range (02:00–02:29) forming inside the
pre-London range changes the 2 SD odds (merged with lon_rows.pkl). Prints the numbers and their stability by half and symbol."""
import numpy as np
import pandas as pd

rows = []
for sym in ('NQ', 'ES', 'RTY'):
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl')[['High', 'Low', 'Close', 'tday', 'hm']]
    b = b[b.hm < 1700]
    m = (b.hm // 100) * 60 + b.hm % 100
    b = b.assign(m=m)
    for td, g in b[(b.m < 300)].groupby('tday'):
        pr = g[g.m < 60]
        t1 = g[(g.m >= 60) & (g.m < 120)]
        lon = g[(g.m >= 120) & (g.m < 300)]
        if len(pr) < 50 or len(t1) < 50 or len(lon) < 160:
            continue
        pH, pL = pr.High.max(), pr.Low.min()
        if pH <= pL:
            continue
        ce = (pH + pL) / 2
        hi1, lo1 = t1.High.max() > pH, t1.Low.min() < pL
        hiL, loL = lon.High.max() > pH, lon.Low.min() < pL
        c2 = t1.Close.iloc[-1]
        rows.append(dict(sym=sym, tday=td, pR=pH - pL, hi1=hi1, lo1=lo1, hiL=hiL, loL=loL,
                         hi5=hi1 or hiL, lo5=lo1 or loL,
                         ceL=bool(((lon.Low <= ce) & (lon.High >= ce)).any()),
                         out2=c2 > pH or c2 < pL,
                         ceRet=bool(((lon.Low <= ce) & (lon.High >= ce)).any()) if (c2 > pH or c2 < pL) else np.nan))
P = pd.DataFrame(rows)
P['half'] = np.where(P.tday < '2025-01-01', '18-24', '25-26')
P['either5'] = P.hi5 | P.lo5
P['both5'] = P.hi5 & P.lo5
P['either1'] = P.hi1 | P.lo1
P['eitherL'] = P.hiL | P.loL
P['bothL'] = P.hiL & P.loL
cols = ['hi1', 'lo1', 'either1', 'hiL', 'loL', 'eitherL', 'bothL', 'hi5', 'lo5', 'either5', 'both5', 'ceL', 'out2', 'ceRet']
print('n', len(P))
print((P[cols].astype(float).mean() * 100).round(1).to_string())
print((P.groupby('half')[cols].mean() * 100).round(1).T)
print((P.groupby('sym')[cols].mean() * 100).round(1).T)

# domain range inside the pre-London range vs the 2 SD odds
R = pd.read_pickle('/home/claude/dx/lon_rows.pkl')
M = R.merge(P, on=['sym', 'tday'])
pr = {}
for sym in ('NQ', 'ES', 'RTY'):
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl')[['High', 'Low', 'tday', 'hm']]
    x = b[b.hm < 100].groupby('tday').agg(pH=('High', 'max'), pL=('Low', 'min'))
    for td, r in x.iterrows():
        pr[(sym, td)] = (r.pH, r.pL)
M['pH'] = [pr.get((s, t), (np.nan, np.nan))[0] for s, t in zip(M.sym, M.tday)]
M['pL'] = [pr.get((s, t), (np.nan, np.nan))[1] for s, t in zip(M.sym, M.tday)]
M['inside'] = (M.dH <= M.pH) & (M.dL >= M.pL)
M['r2'] = (M.mx >= 2.0).astype(float)
M['ratio'] = M.rD / (M.pH - M.pL)
print('\n2 SD odds by domain range inside the pre-London range')
print(M.groupby('inside').r2.agg(['mean', 'size']).round(3))
print(M.groupby(['half', 'inside']).r2.mean().unstack().round(3))
print(M.groupby(['sym', 'inside']).r2.mean().unstack().round(3))
print(M.groupby([M.coil <= 0.2, 'inside']).r2.agg(['mean', 'size']).round(3))
# cluster bootstrap over dates
rng = np.random.default_rng(7)
dates = M.tday.unique()
gi = {d: M.index[M.tday == d].values for d in dates}
diff0 = M[M.inside].r2.mean() - M[~M.inside].r2.mean()
bs = []
for _ in range(1000):
    pick = rng.choice(dates, len(dates))
    idx = np.concatenate([gi[d] for d in pick])
    s = M.loc[idx]
    bs.append(s[s.inside].r2.mean() - s[~s.inside].r2.mean())
bs = np.array(bs)
print('diff', round(diff0, 3), 'p≈', round(2 * min((bs <= 0).mean(), (bs >= 0).mean()), 4))
P.to_pickle('/home/claude/dx/pldr_rows.pkl')
