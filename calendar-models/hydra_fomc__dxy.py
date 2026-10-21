"""Deep DXY on FOMC days (DXY futures 5-min, Jan 2023 – Aug 2026, CT → ET). What DXY does in each stage, how NQ / ES move
against it, whether DXY's stage-1 move tells anything about stage 2, and DXY's own context at 13:59."""
import numpy as np, pandas as pd, re, json
from scipy import stats
X = pd.read_csv('/mnt/user-data/uploads/DXY_2023_2026_5min_continuous.csv')
X['ts'] = pd.to_datetime(X.Date + ' ' + X.Time) + pd.Timedelta(hours=1); X = X.sort_values('ts')
X['tday'] = (X.ts + pd.Timedelta(hours=6)).dt.normalize(); X['m'] = ((X.ts.dt.hour * 60 + X.ts.dt.minute) - 1080) % 1440
M = lambda h, mi: ((h * 60 + mi) - 1080) % 1440
def at_close(g, h, mi):           # last 5-min bar that has closed by h:mi
    k = g[g.m + 5 <= M(h, mi)]; return k.Close.iloc[-1] if len(k) else np.nan
def at_open(g, h, mi):
    k = g[g.m >= M(h, mi)]; return k.Open.iloc[0] if len(k) else np.nan
DXD = {}
for td, g in X.groupby('tday'):
    c = g.Contract.value_counts().index[0]; g = g[g.Contract == c]
    if len(g) < 150: continue
    DXD[td] = g
days = sorted(DXD)
dxday = pd.DataFrame({'O': [DXD[d].Open.iloc[0] for d in days], 'H': [DXD[d].High.max() for d in days], 'L': [DXD[d].Low.min() for d in days],
                      'C': [DXD[d].Close.iloc[-1] for d in days]}, index=pd.DatetimeIndex(days))
dxday['rng20'] = (dxday.H - dxday.L).rolling(20).mean().shift(1)
out = {}
for sym in ('NQ', 'ES'):
    F = pd.read_pickle(f'fomc_{sym}.pkl'); F = F[F.index.isin(DXD.keys())]
    rows = []
    for d, r in F.iterrows():
        g = DXD[d]
        o18 = g.Open.iloc[0]; c1359 = at_close(g, 14, 0); o1400 = at_open(g, 14, 0); c1429 = at_close(g, 14, 30); o1430 = at_open(g, 14, 30); c1614 = at_close(g, 16, 15)
        i = dxday.index.get_loc(d); rng20 = dxday.rng20.iloc[i]
        mon = dxday[(dxday.index.year == d.year) & (dxday.index.month == d.month) & (dxday.index < d)]
        pre = g[g.m + 5 <= M(14, 0)]
        mH = max(mon.H.max() if len(mon) else -np.inf, pre.High.max()); mL = min(mon.L.min() if len(mon) else np.inf, pre.Low.min())
        MOd = mon.O.iloc[0] if len(mon) else o18
        c4w = dxday.C.iloc[i - 20] if i >= 20 else np.nan
        rows.append(dict(tday=d, dx_s1=(c1429 - o1400) / rng20, dx_s2=(c1614 - o1430) / rng20, dx_pre=(c1359 - o18) / rng20,
                         dx_moPos=(c1359 - mL) / (mH - mL), dx_dMO=(c1359 - MOd) / rng20, dx_4w=(c1359 - c4w) / rng20 if c4w == c4w else np.nan))
    D = pd.DataFrame(rows).set_index('tday').join(F)
    D['other1'] = (np.sign(D.dx_s1) * np.sign(D.s1) < 0).astype(float)
    D['other2'] = (np.sign(D.dx_s2) * np.sign(D.s2) < 0).astype(float)
    D['dx1big'] = D.dx_s1.abs() >= D.dx_s1.abs().median()
    D.to_pickle(f'dxy_{sym}.pkl')
    n = len(D); half = D.index < '2025-01-01'
    def rate(mask, col):
        x = D[mask][col].dropna(); return x.mean(), len(x)
    print(f'\n========== {sym}: {n} FOMC days with DXY futures (2023-02 → 2026-07)')
    for nm, col in (('stage 1 other way to DXY', 'other1'), ('stage 2 other way to DXY', 'other2')):
        a, na = rate(np.ones(n, bool), col); b, nb = rate(half, col); c, nc = rate(~half, col)
        print(f'  {nm:28s} {a * 100:3.0f}% (n {na}) · 2023–24 {b * 100:3.0f}% · 2025–26 {c * 100:3.0f}% · binomial p {stats.binomtest(int(round(a * na)), na, 0.5).pvalue:.3f}')
    for lab, mk in (('DXY stage-1 move big (≥ median)', D.dx1big), ('DXY stage-1 move small', ~D.dx1big)):
        a, na = rate(mk.values, 'other1'); print(f'  {lab:34s} stage 1 other way {a * 100:3.0f}% (n {na})')
    # lead: does DXY's stage-1 sign tell NQ's stage 2 / post-14:30 sign?
    s = np.sign(D.dx_s1)
    for tgt, lab in (('s2', 'stage 2'), ('nAM', 'next NY AM')):
        opp = (np.sign(D[tgt]) == -s).mean()
        k = int((np.sign(D[tgt]) == -s).sum()); p = stats.binomtest(k, n, 0.5).pvalue
        h1 = (np.sign(D[tgt]) == -s)[half].mean(); h2 = (np.sign(D[tgt]) == -s)[~half].mean()
        print(f'  DXY stage 1 → {lab:12s} opposite to DXY s1 {opp * 100:3.0f}% (p {p:.3f}) · 2023–24 {h1 * 100:3.0f}% · 2025–26 {h2 * 100:3.0f}%')
    # was the stage-1 contrarian pair followed by stage-2 continuation?
    for cond, lab in ((D.other1 == 1, 'stage 1 went other way to DXY'), (D.other1 == 0, 'stage 1 went with DXY')):
        x = D[cond]
        print(f'  {lab:32s} n {len(x):2d} · stage 2 continues stage 1 {((x.s1 * x.s2) > 0).mean() * 100:3.0f}% · |s2| {x.m_s2.median():.2f} ADR · post range {x.postRng.median():.2f}')
    # DXY context at 13:59
    for lab, mk in (('DXY in its month premium (≥0.75)', D.dx_moPos >= 0.75), ('DXY in its month discount (≤0.25)', D.dx_moPos <= 0.25), ('DXY up into 14:00 (pre > 0)', D.dx_pre > 0), ('DXY 4-week up', D.dx_4w > 0)):
        x, y = D[mk], D[~mk]
        if len(x) < 5: print(f'  {lab}: n {len(x)}'); continue
        def bp(a, b):
            n1, n0 = len(a), len(b); pp = (a.sum() + b.sum()) / (n1 + n0); se = np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n0)); return 2 * stats.norm.sf(abs((a.mean() - b.mean()) / se)) if se > 0 else 1
        print(f'  {lab:34s} n {len(x):2d} · {sym} stage 1 up {x.y_s1.mean() * 100:3.0f}% vs {y.y_s1.mean() * 100:3.0f}% (p {bp(x.y_s1, y.y_s1):.2f}) · stage 2 up {x.y_s2.mean() * 100:3.0f}% vs {y.y_s2.mean() * 100:3.0f}% (p {bp(x.y_s2, y.y_s2):.2f}) · post up {x.y_post.mean() * 100:3.0f}% vs {y.y_post.mean() * 100:3.0f}% (p {bp(x.y_post, y.y_post):.2f})')
    out[sym] = dict(n=n)
