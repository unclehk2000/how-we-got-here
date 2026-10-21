"""Diagnose the 10/07 miss (chart: domain range ~26 pts = 0.08% of price, overnight ATR(5) 0.67% / 207 pts,
04:59 close 0.14% below the low ~= 1.7 SD, the -0.3% line hit only after 05:00).
Candidate fixes, each scored on precision (flagged days that expanded) and recall (expansion days that were flagged):
  definitions: 0.30% by 04:59 (current) | 2 SD by 04:59 | 0.30% by 06:59
  qualifiers : ATR5 >= 1.00% (current) | coil = domain range / ATR5 (pts) in the bottom third | either | both"""
import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
rows = []; prevC = np.nan
for d, x in b.groupby('tday'):
    on = x[(x.hm >= 1800) | (x.hm <= 229)]; lor = x[(x.hm >= 200) & (x.hm <= 229)]
    c5 = x[x.hm == 459]; c7 = x[x.hm == 659]; last = x[x.hm == 1659]
    if len(on) > 300 and len(lor) >= 28 and len(c5) == 1 and len(c7) == 1:
        P = lor.Close.iloc[-1]; H, L = lor.High.max(), lor.Low.min(); R = H - L
        hi, lo = on.High.max(), on.Low.min()
        tr = (max(hi, prevC) - min(lo, prevC)) if not np.isnan(prevC) else np.nan
        def beyond(c):  # signed distance past the range: +pct, +SD
            if c > H: return (c - H) / H * 100, (c - H) / R
            if c < L: return (L - c) / L * 100, (L - c) / R
            return 0.0, 0.0
        p5, s5 = beyond(c5.Close.iloc[0]); p7, s7 = beyond(c7.Close.iloc[0])
        rows.append(dict(tday=d, year=d.year, R=R, Rpct=100 * R / P, trp=100 * tr / P, trpts=tr, p5=p5, s5=s5, p7=p7, s7=s7))
    prevC = last.Close.iloc[0] if len(last) else np.nan
Q = pd.DataFrame(rows).sort_values('tday').reset_index(drop=True)
Q['atr'] = Q.trp.rolling(5).mean(); Q['atrpts'] = Q.trpts.rolling(5).mean(); Q = Q.dropna(subset=['atr']).copy()
Q['coil'] = Q.R / Q.atrpts
Q['sp'] = np.where(Q.year >= 2025, 'test', 'train')
Tr = Q[Q.sp == 'train']
coil_cut = Tr.coil.quantile(1/3)
print(f"coil = domain range / overnight ATR(5) in points. Bottom-third cut (train) = {coil_cut:.3f}. The 10/07 chart: 26/207 = {26/207:.3f}")
print('coil distribution train:', Tr.coil.quantile([.1, .25, .33, .5, .75]).round(3).to_dict())
defs = {'0.30% by 04:59 (current)': Q.p5 >= 0.30, '2 SD by 04:59': Q.s5 >= 2.0, '0.30% by 06:59': Q.p7 >= 0.30}
quals = {'ATR >= 1.00% (current)': Q.atr >= 1.0, 'coiled (bottom third)': Q.coil <= coil_cut,
         'ATR or coiled': (Q.atr >= 1.0) | (Q.coil <= coil_cut), 'ATR and coiled': (Q.atr >= 1.0) & (Q.coil <= coil_cut)}
for dn, E in defs.items():
    print(f"\n=== Expansion defined as: {dn}")
    for sp in ['train', 'test']:
        m = Q.sp == sp; base = E[m].mean()
        print(f"  {sp}: base rate {100*base:.1f}%")
        for qn, F in quals.items():
            f = F[m]; e = E[m]
            prec = e[f].mean(); rec = f[e].mean(); flagged = f.mean()
            print(f"     {qn:24s} flags {100*flagged:5.1f}% of days | precision {100*prec:5.1f}% (lift {prec/base:4.2f}x) | recall {100*rec:5.1f}%")
