"""Senbonzakura statistics. For every trading day (18:00 → 17:00 ET) and every half-hour mark j (18:00 + 30j min):
X = (close − price at the mark) / ADR20, for two closes: the trading-day close (16:59 bar) and the RTH close (16:14 bar).
ADR20 = mean high − low of the previous 20 trading days. Output: quantiles of X per mark, the share of the day's
variance still ahead at each mark (for the implied curve), and per-day rows for the tests."""
import numpy as np, pandas as pd, pickle, sys
Q = [0.01, 0.025, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.975, 0.99]
NJ = 46
def days(sym):
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl')
    hm = b.hm.values
    m = ((hm // 100) * 60 + hm % 100 - 1080) % 1440            # minutes since 18:00
    b = b.assign(m=m)
    out = []
    for td, g in b.groupby('tday', sort=True):
        mm = g.m.values; c = g.Close.values
        rec = dict(tday=td, O=g.Open.values[0], H=g.High.max(), L=g.Low.min(), m0=mm[0], m1=mm[-1], n=len(g))
        last = mm <= 1379
        rec['C_TD'] = c[last][-1] if last.any() else np.nan
        r = mm <= 1334                                            # 16:14 bar
        rec['C_RTH'] = c[r][-1] if r.any() and mm[r][-1] >= 1320 else np.nan
        P = np.full(NJ, np.nan)
        P[0] = g.Open.values[0] if mm[0] <= 5 else np.nan
        idx = np.searchsorted(mm, np.arange(1, NJ) * 30, side='left') - 1   # last bar before the mark
        ok = idx >= 0
        P[1:][ok] = c[idx[ok]]
        rec['P'] = P
        out.append(rec)
    D = pd.DataFrame(out).set_index('tday')
    D['rng'] = D.H - D.L
    D['adr'] = D.rng.rolling(20).mean().shift(1)
    D['full'] = (D.m0 <= 5) & (D.m1 >= 1375) & (D.n >= 1000)
    return D
if __name__ == '__main__':
    for s in ('NQ', 'ES', 'RTY'):
        D = days(s); D.to_pickle(f'/home/claude/hm/senbon/days_{s}.pkl')
        print(s, len(D), 'days', int(D.full.sum()), 'full', D.index.min().date(), '→', D.index.max().date())
