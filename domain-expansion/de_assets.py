"""Per-asset day table for Domain Expansion (same definitions as the indicator), NQ and ES."""
import pandas as pd, numpy as np
def seg(x, a, z): return x[(x.hm >= a) & (x.hm <= z)]
def build(sym):
    b = pd.read_pickle(f'/home/claude/twin/bars_{sym}.pkl').sort_values('ts')
    rows = []; prev = None
    for d, x in b.groupby('tday'):
        ev = x[x.hm >= 1800]; lor = seg(x, 200, 229); post = seg(x, 230, 459); c1659 = x[x.hm == 1659]
        ok = len(lor) >= 28 and len(post) >= 140 and post.hm.iloc[-1] == 459 and len(ev) > 0
        if ok and prev is not None:
            on = pd.concat([ev, seg(x, 0, 229)])
            H, L = lor.High.max(), lor.Low.min(); R = H - L; P = lor.Close.iloc[-1]; C5 = post.Close.iloc[-1]
            if R > 0:
                pc = prev['c1659']
                tr = max(on.High.max(), pc) - min(on.Low.min(), pc)
                e2 = seg(x, 1800, 1959)
                cb = max(prev['h14'], e2.High.max()) - min(prev['l14'], e2.Low.min())
                up = post.High.max() - H; dn = L - post.Low.min()
                rows.append(dict(tday=d, year=d.year, P=P, R=R, tr=tr, cb=cb,
                                 xsd=max(up, dn) / R,                               # London extreme past the range, SD
                                 cpct=100 * max(C5 - H, L - C5) / P))               # 04:59 close past the range, % of price
        if len(c1659) and ok:
            s14 = seg(x, 1400, 1659)
            prev = dict(c1659=c1659.Close.iloc[0], h14=s14.High.max(), l14=s14.Low.min())
    F = pd.DataFrame(rows).sort_values('tday').reset_index(drop=True)
    F['blk'] = (F.tday.diff().dt.days > 10).cumsum()
    F['atr'] = F.groupby('blk').tr.transform(lambda s: s.rolling(5).mean())     # points, today's overnight included
    F = F.dropna(subset=['atr']).reset_index(drop=True)
    F['atr_pct'] = 100 * F.atr / F.P; F['cb_pct'] = 100 * F.cb / F.P; F['r_pct'] = 100 * F.R / F.P
    F['coil'] = F.R / F.atr; F['cbR'] = F.cb / F.R
    F['sym'] = sym; F['sp'] = np.where(F.year >= 2025, '2025-26', 'pre-2025')
    return F
A = pd.concat([build('NQ'), build('ES')])
A.to_pickle('/home/claude/byk/de_assets.pkl')
C = A[A.year >= 2023]
print('2023-26 medians (same period for both):')
print(C.groupby('sym')[['r_pct', 'atr_pct', 'cb_pct', 'cpct', 'coil', 'cbR', 'xsd']].median().round(3).to_string())
m = C.groupby('sym')[['r_pct', 'atr_pct', 'cb_pct']].median()
print('\nES / NQ ratio of medians:', (m.loc['ES'] / m.loc['NQ']).round(3).to_dict())
q = C.groupby('sym').cpct.quantile([0.75, 0.83, 0.90]).unstack().round(3)
print('\n04:59 close past the range (% of price), upper quantiles:'); print(q.to_string())
