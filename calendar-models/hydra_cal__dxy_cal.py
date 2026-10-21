"""DXY futures (5-minute, Feb 2023 – Jul 2026) against NQ / ES in the same windows on NFP days, NFP-week Mon–Thu and the
day after FOMC, with normal days (Vizard type 6) as the baseline. Moves in each market's own ADR20 units. BIG = DXY's move at
least its median for that window on event days."""
import numpy as np, pandas as pd, json
from scipy import stats
from common import *
import common as CM
exec(open('/home/claude/hm/hydra_fomc/dxy.py').read().split('out = {}')[0].replace("pd.read_pickle(f'fomc_{sym}.pkl')", "None"))
WIN = {'nfp': [('s1', (8, 30), (8, 50)), ('s2', (8, 50), (9, 30)), ('am', (9, 30), (11, 0)), ('post', (8, 30), (16, 15))],
       'wk': [('am', (9, 30), (11, 0)), ('rth', (9, 30), (16, 15))], 'fa': [('am', (9, 30), (11, 0)), ('rth', (9, 30), (16, 15))]}
OUT = {}
for sym in ('NQ', 'ES'):
    G = CM.days(sym); D = CM.ctx(sym); T = day_type(D.index)
    def moves(d, w0, w1):
        if d not in DXD or d not in G or d not in dxday.index: return None
        g = Day(G[d]); x = DXD[d]; a20 = dxday.rng20.loc[d]; A = D.adr.loc[d]
        ix = (g.c(w1[0], w1[1] - 1) if w1[1] else g.c(w1[0] - 1, 59)) - g.o(*w0)
        dx = at_close(x, *w1) - at_open(x, *w0)
        if not (a20 > 0 and A > 0) or np.isnan(ix) or np.isnan(dx) or ix == 0 or dx == 0: return None
        return ix / A, dx / a20
    for ev in ('nfp', 'wk', 'fa'):
        F = pd.read_pickle(f'{ev}_{sym}.pkl'); OUT.setdefault(ev, {}).setdefault(sym, {})
        print(f'\n===== {ev} {sym}')
        for nm, w0, w1 in WIN[ev]:
            R = [(d, *m) for d in F.index if (m := moves(d, w0, w1))]
            N_ = [m for d in D.index[(D.index >= '2023-02-01')] if T[d] == 6 and (m := moves(d, w0, w1))]
            X = pd.DataFrame(R, columns=['d', 'ix', 'dx']).set_index('d')
            oth = (np.sign(X.ix) != np.sign(X.dx)); n = len(X); h = X.index < '2025-01-01'
            thr = X.dx.abs().median(); big = X.dx.abs() >= thr
            base = np.mean([np.sign(a) != np.sign(b) for a, b in N_])
            k = int(oth.sum()); pb = stats.binomtest(k, n, 0.5).pvalue
            pn = stats.binomtest(k, n, base).pvalue
            kb = int(oth[big].sum()); nb = int(big.sum()); pbig = stats.binomtest(kb, nb, 0.5).pvalue
            r = dict(n=n, other=float(oth.mean()), h1=float(oth[h].mean()), h2=float(oth[~h].mean()), p50=pb, normal=float(base), n_norm=len(N_), p_vs_norm=pn,
                     thr=float(thr), big=float(oth[big].mean()), nbig=nb, bh1=float(oth[big & h].mean()), bh2=float(oth[big & ~h].mean()), pbig=pbig,
                     small=float(oth[~big].mean()), nsmall=int((~big).sum()), ixBig=float(X.ix[big].abs().median()), ixSmall=float(X.ix[~big].abs().median()))
            OUT[ev][sym][nm] = r
            print(f"  {nm:5s} other way {r['other'] * 100:3.0f}% (n {n}; 23–24 {r['h1'] * 100:.0f}%, 25–26 {r['h2'] * 100:.0f}%; p vs 50% {pb:.3f}) · normal days {base * 100:.0f}% (n {len(N_)}; p vs normal {pn:.3f})"
                  f" · BIG (≥{thr:.2f} DXY ADR) {r['big'] * 100:.0f}% (n {nb}; {r['bh1'] * 100:.0f}/{r['bh2'] * 100:.0f}; p {pbig:.3f}) vs small {r['small'] * 100:.0f}% · |ix| big {r['ixBig']:.2f} small {r['ixSmall']:.2f}")
json.dump(OUT, open('dxy_cal.json', 'w'))
