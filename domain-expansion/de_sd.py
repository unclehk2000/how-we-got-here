"""How far past the 02:00-02:29 domain range does price travel on Domain Expansion days?
SD k = k domain ranges beyond the domain high (up days) or low (down days). Measured 02:30 -> 04:59.
Also: the counter-move beyond the OTHER side first, all days for comparison, and the % of price that one range is."""
import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
rows = []
for d, x in b.groupby('tday'):
    lor = x[(x.hm >= 200) & (x.hm <= 229)]; post = x[(x.hm >= 230) & (x.hm <= 459)]
    if len(lor) < 28 or len(post) < 140 or post.hm.iloc[-1] != 459: continue
    H, L = lor.High.max(), lor.Low.min(); R = H - L
    if R <= 0: continue
    C5 = post.Close.iloc[-1]; up = C5 >= H * 1.003; dn = C5 <= L * 0.997
    hiSD = (post.High.max() - H) / R; loSD = (L - post.Low.min()) / R
    # time of the extreme in the expansion direction
    if up: ext, opp, cl, ti = hiSD, loSD, (C5 - H) / R, post.hm.values[post.High.values.argmax()]
    elif dn: ext, opp, cl, ti = loSD, hiSD, (L - C5) / R, post.hm.values[post.Low.values.argmin()]
    else: ext = opp = cl = ti = np.nan
    rows.append(dict(year=d.year, exp=up or dn, dir=1 if up else (-1 if dn else 0), Rpct=100 * R / lor.Close.iloc[-1],
                     ext=ext, opp=opp, close=cl, t_ext=ti, best=max(hiSD, loSD)))
Q = pd.DataFrame(rows); Q['sp'] = np.where(Q.year >= 2025, 'test', 'train')
for sp in ['train', 'test']:
    Z = Q[Q.sp == sp]; E = Z[Z.exp]
    print(f"\n===== {sp}: {len(Z)} days, {len(E)} expansion days ({100*len(E)/len(Z):.1f}%)")
    print(f"  one domain range = {Z.Rpct.median():.3f}% of price (median); so 0.30% = {0.30/Z.Rpct.median():.2f} ranges on a median day; on expansion days the range is {E.Rpct.median():.3f}%")
    for c, lab in [('ext', 'furthest point past the broken side'), ('close', '04:59 close past the broken side'), ('opp', 'counter-move past the other side')]:
        v = E[c].clip(lower=0)
        print(f"  {lab:38s} mean {v.mean():.2f} SD | median {v.median():.2f} | 25-75% {v.quantile(.25):.2f}-{v.quantile(.75):.2f} | 10-90% {v.quantile(.1):.2f}-{v.quantile(.9):.2f}")
    lad = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6]
    print('  reach ladder on expansion days (furthest point >= k SD):', {k: round(100 * (E.ext >= k).mean(), 1) for k in lad})
    print('  reach ladder, ALL days, either side (for comparison)    :', {k: round(100 * (Z.best >= k).mean(), 1) for k in lad})
    h = pd.cut(E.ext, [0, .5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 99]).value_counts(sort=False)
    print('  where the move topped out (share of expansion days per bucket):', {str(k): round(100 * v / len(E), 1) for k, v in h.items()})
    tt = pd.Series(E.t_ext.values)
    print('  time of the extreme: before 03:00', round(100 * (tt < 300).mean(), 1), '% | 03:00-03:59', round(100 * ((tt >= 300) & (tt < 400)).mean(), 1), '% | 04:00-04:59', round(100 * (tt >= 400).mean(), 1), '%')
