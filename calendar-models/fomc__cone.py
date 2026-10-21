"""FOMC shock cone: how far price has typically travelled from the 14:00 open by each 5-minute step to 16:15, up and down
separately, in units of ADR20 (trading day, completed days). Quantiles 50% and 80% across FOMC days 2018–26, plus the same
on ordinary days for scale. Writes cone.json."""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/hm'); from events import FOMC
FO = set(pd.Timestamp(d) for d in FOMC)
out = {}
for sym in ['NQ', 'ES']:
    b = pd.read_pickle(f'/home/claude/t3/bars_{sym}_all.pkl')
    b = b[(b.ts.dt.normalize() == b.tday) & (b.hm >= 1400) & (b.hm <= 1614)]
    D = pd.read_pickle(f'/home/claude/hm/days_{sym}.pkl'); adr = D[D.anchor == 'TD'].set_index('tday').adr
    b = b.join(adr, on='tday')
    b['t'] = (b.hm // 100 - 14) * 60 + b.hm % 100                       # minutes after 14:00
    rows = {}
    for td, g in b.groupby('tday'):
        if g.t.min() > 0 or g.t.max() < 130 or pd.isna(g.adr.iloc[0]): continue
        o = g.Open.iloc[0]; a = g.adr.iloc[0] * o
        hi = g.High.cummax().values; lo = g.Low.cummin().values; tt = g.t.values
        u = [(hi[tt < k].max() - o) / a if (tt < k).any() else 0 for k in range(5, 140, 5)]
        d = [(o - lo[tt < k].min()) / a if (tt < k).any() else 0 for k in range(5, 140, 5)]
        rows[td] = u + d
    M = pd.DataFrame(rows).T; n = M.shape[1] // 2
    F = M[M.index.isin(FO)]; O = M[~M.index.isin(FO)]
    q = lambda X, p, s: np.round(X.iloc[:, s].quantile(p).values, 3).tolist()
    out[sym] = dict(n=len(F), u50=q(F, .5, slice(0, n)), u80=q(F, .8, slice(0, n)), d50=q(F, .5, slice(n, None)), d80=q(F, .8, slice(n, None)),
                    ou80=q(O, .8, slice(0, n)), od80=q(O, .8, slice(n, None)))
    s = out[sym]
    print(f"{sym}: {len(F)} FOMC days · by 14:30 up q50 {s['u50'][5]:.2f} q80 {s['u80'][5]:.2f}, down q50 {s['d50'][5]:.2f} q80 {s['d80'][5]:.2f} ADR · "
          f"by 16:15 up {s['u50'][-1]:.2f}/{s['u80'][-1]:.2f}, down {s['d50'][-1]:.2f}/{s['d80'][-1]:.2f} · ordinary-day q80 by 16:15 up {s['ou80'][-1]:.2f} down {s['od80'][-1]:.2f}")
json.dump(out, open('cone.json', 'w'))
