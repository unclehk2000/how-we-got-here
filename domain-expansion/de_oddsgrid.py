"""Odds lookup for the indicator label: ATR band x coiled, pooled 2018-2026 (train/test shown for stability).
Two definitions: 2 SD past the range at the London extreme (default) and 0.30% close past the range at 04:59."""
import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
rows = []; prevC = np.nan
for d, x in b.groupby('tday'):
    on = x[(x.hm >= 1800) | (x.hm <= 229)]; lor = x[(x.hm >= 200) & (x.hm <= 229)]; lon = x[(x.hm >= 230) & (x.hm <= 459)]
    c5 = x[x.hm == 459]; last = x[x.hm == 1659]
    if len(on) > 300 and len(lor) >= 28 and len(c5) == 1 and len(lon) > 140:
        P = lor.Close.iloc[-1]; H, L = lor.High.max(), lor.Low.min(); R = H - L; C5 = c5.Close.iloc[0]
        hi, lo = on.High.max(), on.Low.min(); tr = (max(hi, prevC) - min(lo, prevC)) if not np.isnan(prevC) else (hi - lo)
        rows.append(dict(year=d.year, R=R, trp=100 * tr / P, trpts=tr, rngp=100 * (hi - lo) / P,
                         sdx=max(lon.High.max() - H, L - lon.Low.min()) / R >= 2.0, p5=(C5 >= H * 1.003) or (C5 <= L * 0.997)))
    prevC = last.Close.iloc[0] if len(last) else np.nan
Z = pd.DataFrame(rows); Z['atr'] = Z.trp.rolling(5).mean(); Z['rng'] = Z.rngp.rolling(5).mean(); Z['atrpts'] = Z.trpts.rolling(5).mean()
Z = Z.dropna(subset=['atr']).copy(); Z['coil'] = Z.R / Z.atrpts; Z['sp'] = np.where(Z.year >= 2025, 'test', 'train')
print(f"plain range vs true range ATR: median ratio {np.median(Z.rng / Z.atr):.3f}")
Z['band'] = pd.cut(Z.atr, [0, 0.6, 0.8, 1.0, 99], right=False, labels=['<0.60', '0.60-0.80', '0.80-1.00', '1.00+'])
Z['coiled'] = np.where(Z.coil <= 0.20, 'coiled', 'not coiled')
for dn, lab in [('sdx', '2 SD at the London extreme'), ('p5', '0.30% close at 04:59')]:
    print(f"\n=== {lab}: base {100*Z[dn].mean():.1f}%")
    for sp in ['all', 'train', 'test']:
        S = Z if sp == 'all' else Z[Z.sp == sp]
        t = S.pivot_table(index='band', columns='coiled', values=dn, aggfunc=['mean', 'size'], observed=False)
        out = {f"{bnd}/{c}": f"{100*t[('mean', c)][bnd]:.0f}% (n{int(t[('size', c)][bnd])})" for bnd in t.index for c in ['coiled', 'not coiled']}
        print(f"  {sp:5s}", out)
