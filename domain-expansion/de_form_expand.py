"""'First 30 min the domain range forms, next 30 min the domain expands' (London 02:00-02:30 -> 02:30-03:00).
Placebo: the same form-then-expand pair at every other half-hour of the exchange day (18:00 -> 16:59 ET).
Per start time S: range window [S, S+30), expansion window [S+30, S+60).
Trade: stop-entry at the first touch of the range high/low inside the expansion window, stop at the opposite side,
exit at the expansion window's last close. 1 pt cost. Compared with always-long from the same entry to the same exit."""
import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl')
mm = (b.hm // 100) * 60 + b.hm % 100
b['sm'] = (mm - 18 * 60) % 1440           # session minute: 0 = 18:00
b = b[b.sm < 1380]
days = np.sort(b.tday.unique()); di = {d: i for i, d in enumerate(days)}
N = len(days)
G = {k: np.full((N, 1380), np.nan) for k in ['o', 'h', 'l', 'c']}
r_ = b.tday.map(di).values; c_ = b.sm.values
for k, col in [('o', 'Open'), ('h', 'High'), ('l', 'Low'), ('c', 'Close')]:
    G[k][r_, c_] = b[col].values
year = pd.DatetimeIndex(days).year.values
sp = np.where(year >= 2025, 'test', 'train')
def lab(s): t = (s + 18 * 60) % 1440; return f"{t//60:02d}:{t%60:02d}"
out = []
for s in range(0, 1380 - 60 + 1, 30):
    fh, fl = G['h'][:, s:s+30], G['l'][:, s:s+30]
    eo, eh, el, ec = G['o'][:, s+30:s+60], G['h'][:, s+30:s+60], G['l'][:, s+30:s+60], G['c'][:, s+30:s+60]
    ok = (np.isnan(fh).sum(1) <= 2) & (np.isnan(eh).sum(1) <= 2)
    for i in np.where(ok)[0]:
        H, L = np.nanmax(fh[i]), np.nanmin(fl[i]); R = H - L
        if R <= 0: continue
        hh, ll, oo, cc = eh[i], el[i], eo[i], ec[i]
        v = ~np.isnan(hh); hh, ll, oo, cc = hh[v], ll[v], oo[v], cc[v]
        up = hh > H; dn = ll < L
        ext = max(np.max(hh) - H, L - np.min(ll), 0) / R
        rec = dict(start=lab(s), s=s, sp=sp[i], R=R, brk=up.any() or dn.any(), one=up.any() != dn.any(), ext=ext,
                   ratio=(np.max(hh) - np.min(ll)) / R)
        iu = np.argmax(up) if up.any() else 99; idn = np.argmax(dn) if dn.any() else 99
        if min(iu, idn) < 99 and iu != idn:
            side = 1 if iu < idn else -1; j0 = min(iu, idn)
            e = max(H, oo[j0]) if side > 0 else min(L, oo[j0]); stop = L if side > 0 else H
            pnl = None
            for j in range(j0, len(hh)):
                if (ll[j] <= stop) if side > 0 else (hh[j] >= stop):
                    pnl = side * (stop - e); break
            if pnl is None: pnl = side * (cc[-1] - e)
            rec.update(side=side, r=(pnl - 1) / R, pnl=pnl - 1, bench=cc[-1] - e)
        out.append(rec)
X = pd.DataFrame(out)
X.to_pickle('/home/claude/byk/de_X.pkl')
def tstat(v): v = v.dropna(); return v.mean() / (v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 2 else np.nan
agg = []
for (st, s, spl), g in X.groupby(['start', 's', 'sp']):
    tr = g[g.side.notna()]
    agg.append(dict(start=st, s=s, sp=spl, n=len(g), brk=100*g.brk.mean(), one=100*g.one.mean(), ext_med=g.ext.median(),
                    ratio_med=g.ratio.median(), R_pts=g.R.median(), trade_R=tr.r.mean(), t=tstat(tr.r),
                    vs_long=(tr.pnl - tr.bench).mean()))
A = pd.DataFrame(agg).sort_values(['sp', 's'])
pd.set_option('display.width', 200)
for spl in ['train', 'test']:
    Z = A[A.sp == spl].drop(columns=['s', 'sp']).round(3)
    print(f"\n===== {spl}: range forms [S, S+30) -> expands [S+30, S+60)")
    print(Z.to_string(index=False))
