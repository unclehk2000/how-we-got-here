"""Follow-ups from the 10/07 chart.
(1) Qualifier grid, fixed before looking: ATR5 in {0.6, 0.7, 0.8, 1.0}% x coil (range / ATR5 pts) in {any, <=0.20, <=0.15}.
    Scored against the definitions the chart points to: 2 SD past the range at the London extreme (by 04:59), and 0.30% close by 06:59.
(2) The 08:00 UK sweep seen on the chart: in the first 30 min after 08:00 UK, price trades beyond one side of the domain
    range and the half-hour closes back inside it. Does the day then expand the OTHER way?"""
import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
b['uk'] = b.ts.dt.tz_localize('America/New_York', ambiguous='NaT', nonexistent='NaT').dt.tz_convert('Europe/London')
b['ukhm'] = b.uk.dt.hour * 100 + b.uk.dt.minute
rows = []; prevC = np.nan
for d, x in b.groupby('tday'):
    on = x[(x.hm >= 1800) | (x.hm <= 229)]; lor = x[(x.hm >= 200) & (x.hm <= 229)]
    lon = x[(x.hm >= 230) & (x.hm <= 459)]; c5 = x[x.hm == 459]; c7 = x[x.hm == 659]; last = x[x.hm == 1659]
    ukw = x[(x.ukhm >= 800) & (x.ukhm <= 829) & (x.hm >= 230) & (x.hm <= 459)]
    if len(on) > 300 and len(lor) >= 28 and len(c5) == 1 and len(c7) == 1 and len(lon) > 140:
        P = lor.Close.iloc[-1]; H, L = lor.High.max(), lor.Low.min(); R = H - L
        hi, lo = on.High.max(), on.Low.min()
        tr = (max(hi, prevC) - min(lo, prevC)) if not np.isnan(prevC) else np.nan
        C5, C7 = c5.Close.iloc[0], c7.Close.iloc[0]
        extUp = (lon.High.max() - H) / R; extDn = (L - lon.Low.min()) / R
        sw = 0; ukC = np.nan
        if len(ukw) >= 25:
            su, sd = ukw.High.max() > H, ukw.Low.min() < L; ukC = ukw.Close.iloc[-1]
            if su and not sd and ukC < H: sw = 1        # swept the high, closed back inside
            if sd and not su and ukC > L: sw = -1       # swept the low, closed back inside
        rows.append(dict(year=d.year, R=R, trp=100 * tr / P, trpts=tr,
                         e_sdx=max(extUp, extDn) >= 2.0, dir_sdx=1 if extUp >= extDn else -1,
                         e_p7=(C7 >= H * 1.003) or (C7 <= L * 0.997), dir_p7=1 if C7 > H else (-1 if C7 < L else 0),
                         e_p5=(C5 >= H * 1.003) or (C5 <= L * 0.997), dir_p5=1 if C5 > H else (-1 if C5 < L else 0),
                         sw=sw, ukC=ukC, C5=C5, C7=C7))
    prevC = last.Close.iloc[0] if len(last) else np.nan
Q = pd.DataFrame(rows)
Q['atr'] = Q.trp.rolling(5).mean(); Q['atrpts'] = Q.trpts.rolling(5).mean(); Q = Q.dropna(subset=['atr']).copy()
Q['coil'] = Q.R / Q.atrpts; Q['sp'] = np.where(Q.year >= 2025, 'test', 'train')
print('(1) Qualifier grid. Columns: flags% | precision% | recall%  (train / test)')
for dn in ['e_sdx', 'e_p7', 'e_p5']:
    lab = {'e_sdx': '2 SD at the London extreme', 'e_p7': '0.30% close by 06:59', 'e_p5': '0.30% close by 04:59 (current)'}[dn]
    print(f"\n  Definition: {lab}   base rate train {100*Q[Q.sp=='train'][dn].mean():.1f}% / test {100*Q[Q.sp=='test'][dn].mean():.1f}%")
    for a in [0.6, 0.7, 0.8, 1.0]:
        for c in [9, 0.20, 0.15]:
            F = (Q.atr >= a) & (Q.coil <= c); out = []
            for sp in ['train', 'test']:
                m = Q.sp == sp; f, e = F[m], Q[dn][m]
                out.append(f"{100*f.mean():5.1f} | {100*e[f].mean():5.1f} | {100*f[e].mean():5.1f}")
            print(f"    ATR>={a:.1f}% coil{'<=' + str(c) if c < 9 else ' any ':7s}  train {out[0]}   test {out[1]}")
print('\n(2) 08:00 UK sweep of a domain side that closes back inside (first 30 min after 08:00 UK)')
for sp in ['train', 'test']:
    Z = Q[Q.sp == sp]
    for s_, nm in [(1, 'swept HIGH'), (-1, 'swept LOW')]:
        S = Z[Z.sw == s_]
        if len(S) == 0: continue
        opp5 = (S.dir_p5 == -s_) & S.e_p5; same5 = (S.dir_p5 == s_) & S.e_p5
        opp7 = (S.dir_p7 == -s_) & S.e_p7; same7 = (S.dir_p7 == s_) & S.e_p7
        mv5 = -s_ * (S.C5 - S.ukC); mv7 = -s_ * (S.C7 - S.ukC)   # points in the opposite direction from the 08:30 UK close
        lng5 = (S.C5 - S.ukC); lng7 = (S.C7 - S.ukC)
        print(f"  {sp} {nm:10s} n{len(S):3d} ({100*len(S)/len(Z):.1f}% of days) | expands the OTHER way: by 04:59 {100*opp5.mean():.1f}% / by 06:59 {100*opp7.mean():.1f}%"
              f" | same way {100*same5.mean():.1f}% / {100*same7.mean():.1f}% | move the other way from 08:30 UK: {mv5.mean():+.1f} pt to 04:59, {mv7.mean():+.1f} pt to 06:59 (always-long {lng5.mean():+.1f} / {lng7.mean():+.1f})")
    base5 = Z.e_p5.mean() / 2; base7 = Z.e_p7.mean() / 2
    print(f"  {sp} reference: any one direction expands {100*base5:.1f}% (04:59) / {100*base7:.1f}% (06:59) of all days")
