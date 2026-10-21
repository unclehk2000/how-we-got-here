"""Why fixed-% ATR misses days: compare the fixed 1.00% bar with ATR bars set relative to the market's own recent level.
rel = ATR5 / ATR50 (5-overnight average vs 50-overnight average). Expansion = 0.30% close past the range by 04:59."""
import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
rows = []; prevC = np.nan
for d, x in b.groupby('tday'):
    on = x[(x.hm >= 1800) | (x.hm <= 229)]; lor = x[(x.hm >= 200) & (x.hm <= 229)]; c5 = x[x.hm == 459]; last = x[x.hm == 1659]
    if len(on) > 300 and len(lor) >= 28 and len(c5) == 1:
        P = lor.Close.iloc[-1]; H, L = lor.High.max(), lor.Low.min(); C5 = c5.Close.iloc[0]
        hi, lo = on.High.max(), on.Low.min(); tr = (max(hi, prevC) - min(lo, prevC)) if not np.isnan(prevC) else np.nan
        rows.append(dict(year=d.year, trp=100 * tr / P, exp=(C5 >= H * 1.003) or (C5 <= L * 0.997), today=100 * tr / P))
    prevC = last.Close.iloc[0] if len(last) else np.nan
Q = pd.DataFrame(rows); print('days with a missing true range:', Q.trp.isna().sum(), 'of', len(Q))
Q['atr5'] = Q.trp.rolling(5).mean(); Q['atr50'] = Q.trp.rolling(50, min_periods=40).mean()
Q = Q.dropna(subset=['atr5', 'atr50']).copy(); Q['rel'] = Q.atr5 / Q.atr50; Q['sp'] = np.where(Q.year >= 2025, 'test', 'train')
print('Share of days clearing a fixed 1.00% bar, by year:', (Q.groupby('year').atr5.apply(lambda s: (s >= 1.0).mean()) * 100).round(0).to_dict())
print('Median 5-overnight ATR by year (%):', Q.groupby('year').atr5.median().round(2).to_dict())
rules = {'fixed ATR5 >= 1.00%': Q.atr5 >= 1.0, 'fixed ATR5 >= 0.70%': Q.atr5 >= 0.7,
         'relative ATR5/ATR50 >= 1.0': Q.rel >= 1.0, 'relative ATR5/ATR50 >= 1.2': Q.rel >= 1.2,
         "today's overnight alone >= 1.00%": Q.today >= 1.0}
for sp in ['train', 'test']:
    m = Q.sp == sp; e = Q.exp[m]
    print(f"\n{sp}: base rate {100*e.mean():.1f}%")
    for rn, F in rules.items():
        f = F[m]
        print(f"  {rn:34s} flags {100*f.mean():5.1f}% | precision {100*e[f].mean():5.1f}% | recall {100*f[e].mean():5.1f}%")

print('\nExpansion odds (0.30% close by 04:59) by 5-overnight ATR band')
bands = [0, 0.4, 0.6, 0.8, 1.0, 1.25, 9]
for sp in ['train', 'test']:
    Z = Q[Q.sp == sp]
    g = Z.groupby(pd.cut(Z.atr5, bands, right=False), observed=True).exp.agg(['mean', 'size']); g['mean'] = (100 * g['mean']).round(1)
    print(f"  {sp}:", {str(k): (r['mean'], int(r['size'])) for k, r in g.iterrows()})
