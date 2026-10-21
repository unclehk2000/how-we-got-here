"""Gran Rey Cero claims, tested on NQ / ES 1-minute data 2018–26 (DXY futures 2023-02 → 2026-08).
A. Up-close frequency by day type and anchor (TD 18:00→16:59, MID 00:00→16:59, RTH 09:30→16:14).
B. Day after CPI: directional continuation, several definitions, vs any day → next day.
C. CPI 08:30 release candle (1 / 5 / 15 min) size ÷ ADR20: terciles for wild / average / quiet; 08:30–09:00 range.
D. DXY cross-check: NQ / ES closing against DXY's direction ("contrarian close") on CPI days vs normal days,
   and NQ up-close conditional on DXY's direction that day and on its 4-week trend.
Every rate with a Wilson 95% interval (the ± margin of error) and a two-proportion test against the baseline.
Writes cpi_claims.json."""
import pandas as pd, numpy as np, json
from scipy import stats
from events import CPI
OUT = {}
def wilson(k, n, z=1.96):
    if n == 0: return (np.nan, np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h
def ztest(k1, n1, k2, n2):
    if min(n1, n2) == 0: return np.nan
    p = (k1 + k2) / (n1 + n2); se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return float(2 * (1 - stats.norm.cdf(abs((k1 / n1 - k2 / n2) / se)))) if se > 0 else np.nan
def rate(s):
    s = s.dropna(); k, n = int(s.sum()), int(len(s)); p, lo, hi = wilson(k, n)
    return dict(p=p, lo=lo, hi=hi, moe=(hi - lo) / 2, k=k, n=n)
def fmt(r): return f"{r['p']*100:4.0f}% ±{r['moe']*100:2.0f} (n{r['n']})" if r['n'] else '—'
def comp(name, a, b, extra=''):
    ra, rb = rate(a), rate(b); pv = ztest(ra['k'], ra['n'], rb['k'], rb['n'])
    print(f'   {name:48s} {fmt(ra)}  vs  {fmt(rb)}  p={pv:.3f} {extra}')
    return dict(a=ra, b=rb, p=pv)

DXY = pd.read_csv('/mnt/user-data/uploads/DXY_2023_2026_5min_continuous.csv')
DXY['ts'] = pd.to_datetime(DXY.Date + ' ' + DXY.Time) + pd.Timedelta(hours=1)            # CT → ET
DXY = DXY.sort_values('ts'); DXY['tday'] = (DXY.ts + pd.Timedelta(hours=6)).dt.normalize(); DXY['mod'] = DXY.ts.dt.hour * 60 + DXY.ts.dt.minute
def win(x, a, z):
    s = x[(x['mod'] >= a) & (x['mod'] < z)]
    return (s.Open.iloc[0], s.Close.iloc[-1]) if len(s) else (np.nan, np.nan)
drows = []
for td, x in DXY.groupby('tday'):
    if td.dayofweek >= 5 or len(x) < 150: continue
    r = dict(tday=td, dO=x.Open.iloc[0], dC=x.Close.iloc[-1])
    r['dRo'], r['dRc'] = win(x, 570, 975); r['dPo'], r['dPc'] = win(x, 510, 975)
    drows.append(r)
DX = pd.DataFrame(drows).set_index('tday')
wk = DX.dC.resample('W-FRI').last().dropna(); w4 = np.log(wk).diff(4)
DX['dx4'] = [w4[w4.index < t].iloc[-1] if (w4.index < t).any() else np.nan for t in DX.index]

for root in ('NQ', 'ES'):
    print('=' * 110, '\n', root); R = OUT.setdefault(root, {})
    D = pd.read_pickle(f'days_{root}.pkl'); P = pd.read_pickle(f'prof_{root}.pkl')
    b = pd.read_pickle(f'/home/claude/t3/bars_{root}_all.pkl'); b['mod'] = b.ts.dt.hour * 60 + b.ts.dt.minute
    # ── A. up-close by anchor
    print(' A. up-close frequency (close > open)')
    for an in ('TD', 'MID', 'RTH'):
        X = D[D.anchor == an].set_index('tday')
        for per, m in (('2018–26', X.year > 0), ('2018–24', X.year <= 2024), ('2025–26', X.year >= 2025)):
            c = comp(f'{an} {per}: CPI vs normal', X[m & (X.type == 'CPI')].up, X[m & (X.type == 'NORMAL')].up)
            R.setdefault('up', {}).setdefault(an, {})[per] = c
    # 08:30 → 16:14 (after the release)
    g = b[(b['mod'] >= 510) & (b['mod'] < 975)].groupby('tday')
    post = pd.DataFrame(dict(o=g.Open.first(), c=g.Close.last()))
    post['up'] = (post.c > post.o).astype(float)
    T = D[D.anchor == 'TD'].set_index('tday')[['type', 'year']].join(post, how='inner')
    for per, m in (('2018–26', T.year > 0), ('2018–24', T.year <= 2024), ('2025–26', T.year >= 2025)):
        c = comp(f'08:30→16:14 {per}: CPI vs normal', T[m & (T.type == 'CPI')].up, T[m & (T.type == 'NORMAL')].up)
        R.setdefault('up', {}).setdefault('POST', {})[per] = c
    # ── B. day after CPI
    print(' B. day after CPI: continuation of the CPI day direction')
    X = D[D.anchor == 'TD'].set_index('tday').sort_index()
    X['dir'] = np.sign(X.C - X.O); X['nDir'] = X.dir.shift(-1); X['nC'] = X.C.shift(-1); X['nH'] = X.H.shift(-1); X['nL'] = X.L.shift(-1)
    X['c2c'] = np.sign(X.nC - X.C)
    defs = {'next TD closes the same way (open→close)': lambda d: (d.nDir == d.dir).astype(float).where((d.dir != 0) & (d.nDir != 0) & d.nDir.notna()),
            'next TD close beyond CPI close in CPI direction': lambda d: (d.c2c == d.dir).astype(float).where((d.dir != 0) & (d.c2c != 0) & d.c2c.notna()),
            'next TD takes CPI extreme in CPI direction': lambda d: np.where(d.dir > 0, d.nH > d.H, d.nL < d.L).astype(float) * 1.0 + 0 * d.dir}
    Pr = P.copy(); Pr['nd'] = Pr.nextDir
    for name, f in defs.items():
        v = f(X); v = pd.Series(v, index=X.index).where(X.nC.notna())
        for per, m in (('2018–26', X.year > 0), ('2018–24', X.year <= 2024), ('2025–26', X.year >= 2025)):
            c = comp(f'{name} {per}', v[m & (X.type == 'CPI')], v[m & (X.type == 'NORMAL')])
            R.setdefault('next', {}).setdefault(name, {})[per] = c
    v = pd.Series(np.where((Pr.dir * Pr.nd) != 0, (Pr.dir == Pr.nd).astype(float), np.nan), index=Pr.index)
    for per, m in (('2018–26', Pr.year > 0), ('2018–24', Pr.year <= 2024), ('2025–26', Pr.year >= 2025)):
        c = comp(f'next RTH closes the same way as CPI RTH {per}', v[m & (Pr.type == 'CPI')], v[m & (Pr.type == 'NORMAL')])
        R.setdefault('next', {}).setdefault('RTH same way', {})[per] = c
    # ── C. 08:30 release candle size
    print(' C. 08:30 candle size ÷ (TD open × ADR20) on CPI days (terciles) and normal days (median)')
    TD = D[D.anchor == 'TD'].set_index('tday')
    for L in (1, 5, 15, 30):
        s = b[(b['mod'] >= 510) & (b['mod'] < 510 + L)].groupby('tday')
        rr = ((s.High.max() - s.Low.min())).rename('r')
        Z = TD[['type', 'O', 'adr', 'year']].join(rr, how='inner'); Z['x'] = Z.r / (Z.O * Z.adr)
        c = Z[Z.type == 'CPI'].x; nrm = Z[Z.type == 'NORMAL'].x
        q = np.quantile(c, [1 / 3, 2 / 3])
        tr = np.quantile(Z[(Z.type == 'CPI') & (Z.year <= 2024)].x, [1 / 3, 2 / 3]); te = Z[(Z.type == 'CPI') & (Z.year >= 2025)].x
        print(f'   {L:2d}m: CPI terciles {q[0]:.3f} / {q[1]:.3f} (median {c.median():.3f}, n{len(c)}) · normal median {nrm.median():.3f} · CPI ÷ normal {c.median()/nrm.median():.1f}× · '
              f'2025–26 split by 2018–24 cut-offs: quiet {np.mean(te < tr[0])*100:.0f}% avg {np.mean((te >= tr[0]) & (te < tr[1]))*100:.0f}% wild {np.mean(te >= tr[1])*100:.0f}%')
        R.setdefault('candle', {})[L] = dict(q33=float(q[0]), q67=float(q[1]), med=float(c.median()), nrm=float(nrm.median()), n=int(len(c)))
    # ── D. DXY cross-check
    print(' D. DXY cross-check, Feb 2023 – Aug 2026 (DXY futures)')
    J = TD[['type', 'O', 'C', 'year']].join(P[['rthO', 'rthC']], how='left').join(post[['o', 'c']], how='left').join(DX, how='inner')
    J['nqTD'] = np.sign(J.C - J.O); J['dxTD'] = np.sign(J.dC - J.dO)
    J['nqR'] = np.sign(J.rthC - J.rthO); J['dxR'] = np.sign(J.dRc - J.dRo)
    J['nqP'] = np.sign(J.c - J.o); J['dxP'] = np.sign(J.dPc - J.dPo)
    for w, (a, d_) in {'TD': ('nqTD', 'dxTD'), 'RTH': ('nqR', 'dxR'), '08:30→16:14': ('nqP', 'dxP')}.items():
        ok = (J[a] != 0) & (J[d_] != 0) & J[a].notna() & J[d_].notna()
        con = (J[a] != J[d_]).astype(float).where(ok)
        c = comp(f'{w}: closed against DXY · CPI vs normal', con[J.type == 'CPI'], con[J.type == 'NORMAL'])
        R.setdefault('dxy', {})[w] = c
        call = rate(con); print(f'      all days {fmt(call)}')
        R['dxy'][w]['all'] = call
        up = (J[a] > 0).astype(float).where(ok)
        for ty in ('CPI', 'NORMAL'):
            m = J.type == ty
            c1 = rate(up[m & (J[d_] < 0)]); c2 = rate(up[m & (J[d_] > 0)])
            print(f'      {ty:6s} {root} up when DXY fell {fmt(c1)} · when DXY rose {fmt(c2)}')
            R['dxy'][w][f'{ty}_upIfDxDn'] = c1; R['dxy'][w][f'{ty}_upIfDxUp'] = c2
    ok = J.dx4.notna()
    for ty in ('CPI', 'NORMAL'):
        m = (J.type == ty) & ok & (J.nqTD != 0)
        c1 = rate((J.nqTD > 0).astype(float)[m & (J.dx4 < 0)]); c2 = rate((J.nqTD > 0).astype(float)[m & (J.dx4 > 0)])
        print(f'      {ty:6s} {root} TD up-close after DXY 4-week fall {fmt(c1)} · after a rise {fmt(c2)}')
        R['dxy'][f'{ty}_up_dx4dn'] = c1; R['dxy'][f'{ty}_up_dx4up'] = c2
json.dump(OUT, open('cpi_claims.json', 'w'), indent=1, default=float)
