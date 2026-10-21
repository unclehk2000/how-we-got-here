"""How often do the qualifiers catch the BIG London expansions (close >= 0.5% past the domain range by 04:59), like 10/01 (0.8%)?"""
import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
rows = []; prevC = np.nan
for d, x in b.groupby('tday'):
    on = x[(x.hm >= 1800) | (x.hm <= 229)]; lor = x[(x.hm >= 200) & (x.hm <= 229)]; c5 = x[x.hm == 459]; last = x[x.hm == 1659]
    if len(on) > 300 and len(lor) >= 28 and len(c5) == 1:
        P = lor.Close.iloc[-1]; H, L = lor.High.max(), lor.Low.min(); C5 = c5.Close.iloc[0]
        hi, lo = on.High.max(), on.Low.min(); tr = (max(hi, prevC) - min(lo, prevC)) if not np.isnan(prevC) else np.nan
        past = (C5 - H) / H * 100 if C5 > H else ((L - C5) / L * 100 if C5 < L else 0)
        rows.append(dict(year=d.year, R=H - L, trp=100 * tr / P, trpts=tr, past=past))
    prevC = last.Close.iloc[0] if len(last) else np.nan
Q = pd.DataFrame(rows); Q['atr'] = Q.trp.rolling(5).mean(); Q['atrpts'] = Q.trpts.rolling(5).mean(); Q = Q.dropna().copy()
Q['coil'] = Q.R / Q.atrpts; Q['sp'] = np.where(Q.year >= 2025, 'test', 'train')
v2 = Q.atr >= 1.0; v3 = (Q.atr >= 0.6) & (Q.coil <= 0.20)
for sp in ['train', 'test']:
    m = Q.sp == sp; big = m & (Q.past >= 0.5)
    print(f"{sp}: big days (>=0.5%) {big.sum()} = {100*big.sum()/m.sum():.1f}% of days | caught by old (ATR>=1%) {100*v2[big].mean():.0f}% | new (ATR>=0.6% & coil<=0.20) {100*v3[big].mean():.0f}% | either {100*(v2|v3)[big].mean():.0f}%"
          f" | big-day rate when flagged: old {100*(Q.past[m & v2] >= 0.5).mean():.1f}% new {100*(Q.past[m & v3] >= 0.5).mean():.1f}% either {100*(Q.past[m & (v2|v3)] >= 0.5).mean():.1f}%")

# two-route qualifier: volatile (ATR >= 1.0%) OR coiled (ATR >= 0.6% and coil <= 0.20), scored on both expansion definitions
rows = []; prevC = np.nan
for d, x in b.groupby('tday'):
    on = x[(x.hm >= 1800) | (x.hm <= 229)]; lor = x[(x.hm >= 200) & (x.hm <= 229)]; lon = x[(x.hm >= 230) & (x.hm <= 459)]
    c5 = x[x.hm == 459]; last = x[x.hm == 1659]
    if len(on) > 300 and len(lor) >= 28 and len(c5) == 1 and len(lon) > 140:
        P = lor.Close.iloc[-1]; H, L = lor.High.max(), lor.Low.min(); R = H - L; C5 = c5.Close.iloc[0]
        hi, lo = on.High.max(), on.Low.min(); tr = (max(hi, prevC) - min(lo, prevC)) if not np.isnan(prevC) else np.nan
        rows.append(dict(year=d.year, R=R, trp=100 * tr / P, trpts=tr,
                         sdx=max(lon.High.max() - H, L - lon.Low.min()) / R >= 2.0,
                         p5=(C5 >= H * 1.003) or (C5 <= L * 0.997)))
    prevC = last.Close.iloc[0] if len(last) else np.nan
Z = pd.DataFrame(rows); Z['atr'] = Z.trp.rolling(5).mean(); Z['atrpts'] = Z.trpts.rolling(5).mean(); Z = Z.dropna().copy()
Z['coil'] = Z.R / Z.atrpts; Z['sp'] = np.where(Z.year >= 2025, 'test', 'train')
rules = {'volatile only (ATR>=1.0%)': Z.atr >= 1.0, 'coiled only (ATR>=0.6% & coil<=0.20)': (Z.atr >= 0.6) & (Z.coil <= 0.20)}
rules['either route'] = rules['volatile only (ATR>=1.0%)'] | rules['coiled only (ATR>=0.6% & coil<=0.20)']
for dn, lab in [('sdx', '2 SD at the London extreme'), ('p5', '0.30% close by 04:59')]:
    print(f"\nDefinition: {lab}")
    for sp in ['train', 'test']:
        m = Z.sp == sp; e = Z[dn][m]
        print(f"  {sp} base {100*e.mean():.1f}%")
        for rn, F in rules.items():
            f = F[m]
            print(f"    {rn:38s} flags {100*f.mean():5.1f}% | precision {100*e[f].mean():5.1f}% | recall {100*f[e].mean():5.1f}%")
