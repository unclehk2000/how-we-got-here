"""Odds rows for every day type (with Wilson 95% margins): up-close by anchor, closing against DXY (2023-02 → 2026-08),
NQ / ES up-close when DXY fell / rose that trading day, and the next trading day closing the same way.
Glyph: ✓ = differs from normal days at p < 0.05 and the 2025–26 gap has the same sign; ✗ = p < 0.05 in 2018–24 but
flipped in 2025–26; ≈ = not distinguishable from normal days. Writes odds.json."""
import pandas as pd, numpy as np, json
from scipy import stats
TYPES = ['FOMC', 'NFP', 'CPI', 'POST', 'PRE', 'HOLLOW', 'NORMAL']
def wilson(k, n, z=1.96):
    if n == 0: return (np.nan, np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h
def rate(s):
    s = pd.Series(s).dropna(); k, n = int(s.sum()), int(len(s)); p, lo, hi = wilson(k, n)
    return dict(p=float(p) if n else None, moe=float((hi - lo) / 2) if n else None, n=n, k=k)
def pz(a, b):
    if not a['n'] or not b['n']: return 1.0
    p = (a['k'] + b['k']) / (a['n'] + b['n']); se = np.sqrt(p * (1 - p) * (1 / a['n'] + 1 / b['n']))
    return float(2 * (1 - stats.norm.cdf(abs((a['k'] / a['n'] - b['k'] / b['n']) / se)))) if se > 0 else 1.0
def glyph(full, base, tr, trb, te, teb):
    if pz(full, base) >= 0.05: return '≈'
    d1 = full['p'] - base['p']; d2 = (te['p'] or 0) - (teb['p'] or 0)
    return '✓' if np.sign(d1) == np.sign(d2) else '✗'

DXY = pd.read_csv('/mnt/user-data/uploads/DXY_2023_2026_5min_continuous.csv')
DXY['ts'] = pd.to_datetime(DXY.Date + ' ' + DXY.Time) + pd.Timedelta(hours=1)
DXY = DXY.sort_values('ts'); DXY['tday'] = (DXY.ts + pd.Timedelta(hours=6)).dt.normalize()
DX = DXY.groupby('tday').agg(dO=('Open', 'first'), dC=('Close', 'last'), nb=('Open', 'size'))
DX = DX[(DX.index.dayofweek < 5) & (DX.nb >= 150)]
OUT = {}
for root in ('NQ', 'ES'):
    D = pd.read_pickle(f'days_{root}.pkl'); R = OUT.setdefault(root, {})
    TD = D[D.anchor == 'TD'].set_index('tday').sort_index()
    TD['dir'] = np.sign(TD.C - TD.O); TD['nDir'] = TD.dir.shift(-1)
    nxt = ((TD.nDir == TD.dir).astype(float)).where((TD.dir != 0) & (TD.nDir != 0) & TD.nDir.notna())
    J = TD.join(DX, how='inner'); J['dx'] = np.sign(J.dC - J.dO)
    ok = (J.dir != 0) & (J.dx != 0)
    con = (J.dir != J.dx).astype(float).where(ok); upJ = (J.dir > 0).astype(float).where(ok)
    for t in TYPES:
        T = R.setdefault(t, {})
        for an in ('TD', 'MID', 'RTH'):
            X = D[D.anchor == an].set_index('tday')
            f = lambda m: rate(X[m].up)
            a, b = f(X.type == t), f(X.type == 'NORMAL')
            tr, trb = f((X.type == t) & (X.year <= 2024)), f((X.type == 'NORMAL') & (X.year <= 2024))
            te, teb = f((X.type == t) & (X.year >= 2025)), f((X.type == 'NORMAL') & (X.year >= 2025))
            T[f'up_{an}'] = dict(r=a, base=b, g=glyph(a, b, tr, trb, te, teb), tr=tr, te=te, p=pz(a, b))
        m = TD.type == t; mb = TD.type == 'NORMAL'
        a, b = rate(nxt[m]), rate(nxt[mb])
        T['next'] = dict(r=a, base=b, g=glyph(a, b, rate(nxt[m & (TD.year <= 2024)]), rate(nxt[mb & (TD.year <= 2024)]), rate(nxt[m & (TD.year >= 2025)]), rate(nxt[mb & (TD.year >= 2025)])), p=pz(a, b))
        m = J.type == t; mb = J.type == 'NORMAL'
        a, b = rate(con[m]), rate(con[mb])
        T['dxy'] = dict(r=a, base=b, g='≈' if pz(a, b) >= 0.05 else '✓', p=pz(a, b), upDn=rate(upJ[m & (J.dx < 0)]), upUp=rate(upJ[m & (J.dx > 0)]),
                        bUpDn=rate(upJ[mb & (J.dx < 0)]), bUpUp=rate(upJ[mb & (J.dx > 0)]))
        print(root, t, {k: (f"{v['r']['p']*100:.0f}±{v['r']['moe']*100:.0f} vs {v['base']['p']*100:.0f} {v['g']}" if v['r']['n'] else '—') for k, v in T.items()})
json.dump(OUT, open('odds.json', 'w'), indent=1)
