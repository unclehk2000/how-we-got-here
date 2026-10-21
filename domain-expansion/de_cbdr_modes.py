"""Does CBDR (14:00-20:00 ET range, % of price) add to each qualifier, for each expansion measure?
SD mode: coiled = domain range / overnight ATR(5, points) <= 0.20; target = furthest point past the range 02:30-04:59 >= 2 SD.
% mode : volatile = overnight ATR(5) >= 1.00%; target = 04:59 close >= 0.3% past the range."""
import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
F = pd.read_pickle('/home/claude/byk/de_F.pkl')
ext = {}
for d, x in b.groupby('tday'):
    lor = x[(x.hm >= 200) & (x.hm <= 229)]; post = x[(x.hm >= 230) & (x.hm <= 459)]
    if len(lor) < 28 or len(post) < 100: continue
    H, L = lor.High.max(), lor.Low.min(); R = H - L
    if R <= 0: continue
    c5 = post.Close.iloc[-1]
    ext[d] = dict(R=R, xsd=max(post.High.max() - H, L - post.Low.min()) / R, csd=max(c5 - H, L - c5) / R)
E = pd.DataFrame.from_dict(ext, orient='index'); F = F.join(E, on='tday')
F['on_pts'] = F.on_tr * F.P / 100
F['atr_pts'] = F.groupby('blk').on_pts.transform(lambda s: s.rolling(5).mean())
F['coil'] = F.R / F.atr_pts
F['sd2'] = F.xsd >= 2.0; F['sdc2'] = F.csd >= 2.0
F['cb'] = F.cbdr >= 0.80
F['cb_rng'] = F.cbdr * F.P / 100 / F.R           # CBDR as multiples of the domain range
F = F.dropna(subset=['coil'])
def table(f1, tgt, name, f2='cb'):
    print(f"\n{name}")
    for sp in ['train', 'test']:
        Z = F[F.sp == sp]; a, c = Z[f1], Z[f2]
        cells = {'both': Z[a & c], f'{f1} only': Z[a & ~c], 'CBDR only': Z[~a & c], 'neither': Z[~a & ~c]}
        print(f"  {sp:5s} base {100*Z[tgt].mean():4.1f}% | " + ' | '.join(f"{k} {100*v[tgt].mean():4.1f}% (n{len(v)})" for k, v in cells.items()))
F['coiled'] = F.coil <= 0.20; F['volatile'] = F.atr5 >= 1.0
table('volatile', 'exp', '% mode: 0.3% close at 04:59 | volatile (ATR >= 1%) x CBDR >= 0.80%')
table('coiled', 'sd2', 'SD mode: 2 SD at the London extreme | coiled (<= 0.20) x CBDR >= 0.80%')
table('coiled', 'sdc2', 'SD mode: 2 SD at the 04:59 close | coiled x CBDR >= 0.80%')
# CBDR measured against the domain range (the SD-mode analogue): wide = CBDR >= k ranges
for k in [4, 5, 6]:
    F['cbw'] = F.cb_rng >= k
    table('coiled', 'sd2', f'SD mode (London extreme): coiled x CBDR >= {k} domain ranges', f2='cbw')
print('\ncoil and CBDR-in-ranges correlation:', round(F[['coil', 'cb_rng']].corr().iloc[0, 1], 2))
