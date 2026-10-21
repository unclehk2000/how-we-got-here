#!/usr/bin/env python3
"""
DIRECTION LAB - backdate any NQ directional rule from a price you could actually have traded.

  python direction_lab.py --data "hist/*.csv"                 # run every built-in signal
  python direction_lab.py --data "hist/*.csv" --only byakugan_sweep --months

Each signal is a function  f(d, r, D, B) -> None | (entry_px, exit_px, direction)
  d = trading date, r = that day's row of the session table D, B[d] = (times, highs, lows, closes) of RTH 1-min bars.
Add your own at the bottom of SIGNALS. Rules for an honest test:
  - entry_px must be a price that existed at a time when every input the rule uses was already known
  - a rule that only becomes known at the close (e.g. "never swept") is not a trade
Outputs per signal: trades, win %, mean %, t, same trades taken long (drift control), by year, months positive,
month-to-month heterogeneity (chi2), and the Bonferroni threshold for the number of signals you ran.
Needs hydra.py in the same folder (data loaders) plus numpy, pandas, scipy.
"""
import argparse, glob, math, sys
from datetime import time as T
import numpy as np, pandas as pd
from scipy import stats
from hydra import load, RTH0, RTH1, MIN_RTH, FOMC

def build(patterns, tz_shift=1.0):
    nq = load(patterns, tz_shift)
    vk = nq.groupby(['td', 'k']).v.sum().reset_index().sort_values('v').drop_duplicates('td', keep='last')
    nq = nq.merge(vk[['td', 'k']], on=['td', 'k']).sort_values('dt').reset_index(drop=True)
    def win(g, a, b): t = g.t; return g[(t >= a) & (t < b)] if a < b else g[(t >= a) | (t < b)]
    rows, B = [], {}
    for td, g in nq.groupby('td'):
        rth = g[(g.t >= RTH0) & (g.t <= RTH1)]
        if len(rth) < MIN_RTH: continue
        asia, lon, pre, r79 = win(g, T(20, 0), T(0, 0)), win(g, T(2, 0), T(5, 0)), win(g, T(5, 0), T(9, 30)), win(g, T(7, 0), T(9, 0))
        if len(r79) < 60 or len(asia) < 30 or len(lon) < 60: continue
        rows.append(dict(td=td, k=g.k.iloc[0], ro=rth.o.iloc[0], rh=rth.h.max(), rl=rth.l.min(), rc=rth.c.iloc[-1],
                         h79=r79.h.max(), l79=r79.l.min(), ah=asia.h.max(), al=asia.l.min(), lh=lon.h.max(), ll=lon.l.min(),
                         ph=pre.h.max(), pl=pre.l.min()))
        B[td] = (rth.t.values, rth.h.values, rth.l.values, rth.c.values)
    D = pd.DataFrame(rows).set_index('td')
    prev = D.shift(1); ok = (D.index.to_series().diff().dt.days <= 4) & (D.k == prev.k)
    D['pc'] = prev.rc.where(ok); D['prev_td'] = pd.Series(D.index, index=D.index).shift(1).where(ok)
    D['mid79'] = (D.h79 + D.l79) / 2; D['bias'] = np.where(D.ro > D.mid79, 1, -1)
    D['AL'] = np.where(D.bias == 1, np.maximum(D.ah, D.lh), np.minimum(D.al, D.ll))
    D['pre_swept'] = np.where(D.bias == 1, D.ph > D.AL, D.pl < D.AL)
    D['dist'] = 100 * (D.AL - D.ro).abs() / D.ro
    return D, B

def px_at(bars, t0):            # last close before clock time t0
    t, h, l, c = bars; i = np.flatnonzero(t < t0); return c[i[-1]] if len(i) else None

# ------------------------------------------------------------------ built-in signals
def byakugan_sweep(d, r, D, B):
    """Byakugan target zone: AL extreme 0.30-1.00% away, not swept pre-open; enter AT the level when RTH trades through it."""
    if r.pre_swept or not (0.30 <= r.dist <= 1.00): return None
    t, h, l, c = B[d]; hit = np.flatnonzero(h >= r.AL) if r.bias == 1 else np.flatnonzero(l <= r.AL)
    return None if not len(hit) else (r.AL, c[-1], r.bias)
def byakugan_fade_noon(d, r, D, B):
    """No sweep of a 0.15-1.00% AL level by 12:00 -> fade the bias from the 12:00 price."""
    if r.pre_swept or not (0.15 <= r.dist <= 1.00): return None
    t, h, l, c = B[d]; m = t < T(12, 0)
    if (h[m] >= r.AL).any() if r.bias == 1 else (l[m] <= r.AL).any(): return None
    return (px_at(B[d], T(12, 0)), c[-1], -r.bias)
def byakugan_open(d, r, D, B):
    """Raw Byakugan bias taken at the 09:30 open."""
    return (r.ro, r.rc, r.bias)
def gap_fade(d, r, D, B):
    """Fade the overnight gap from the open."""
    if pd.isna(r.pc) or r.ro == r.pc: return None
    return (r.ro, r.rc, -int(np.sign(r.ro - r.pc)))
def first30_follow(d, r, D, B):
    """Follow the 09:30-10:00 move from 10:00 to the close."""
    p = px_at(B[d], T(10, 0)); return (p, r.rc, int(np.sign(p - r.ro))) if p != r.ro else None
def last30_momentum(d, r, D, B):
    """Gao et al. intraday momentum: sign(prev close -> 15:30) traded 15:30 -> 16:00."""
    if pd.isna(r.pc): return None
    p0, p1 = px_at(B[d], T(15, 30)), px_at(B[d], T(16, 0)); return (p0, p1, int(np.sign(p0 - r.pc))) if p0 != r.pc else None
FOMC_SET = set(pd.to_datetime(FOMC))
def pre_fomc(d, r, D, B):
    """Long 14:00 the day before FOMC -> 14:00 FOMC day (Lucca-Moench pre-announcement drift)."""
    if d not in FOMC_SET or pd.isna(r.prev_td): return None
    return (px_at(B[r.prev_td], T(14, 0)), px_at(B[d], T(14, 0)), 1)
def always_long(d, r, D, B):
    """Benchmark: long 09:30 -> close every day."""
    return (r.ro, r.rc, 1)
SIGNALS = dict(always_long=always_long, byakugan_open=byakugan_open, byakugan_sweep=byakugan_sweep,
               byakugan_fade_noon=byakugan_fade_noon, gap_fade=gap_fade, first30_follow=first30_follow,
               last30_momentum=last30_momentum, pre_fomc=pre_fomc)

# ------------------------------------------------------------------ evaluation
def run(name, f, D, B, months=False):
    rec = []
    for d, r in D.iterrows():
        o = f(d, r, D, B)
        if o is None or o[0] is None or o[1] is None: continue
        e, x, s = o; rec.append((d, s, 100 * s * (x / e - 1), 100 * (x / e - 1)))
    if not rec: print(f'{name}: no trades'); return None
    R = pd.DataFrame(rec, columns=['d', 'dir', 'ret', 'long_ret']).set_index('d')
    t = R.ret.mean() / R.ret.std() * math.sqrt(len(R)); dd = R.ret - R.long_ret
    t_vs = dd.mean() / dd.std() * math.sqrt(len(R)) if dd.std() > 0 else float('nan')
    Y = R.groupby(R.index.year).ret.agg(['size', 'mean', lambda s: 100 * (s > 0).mean()]).round(3)
    M = R.groupby(R.index.to_period('M')).ret.sum()
    ct = pd.crosstab(R.index.to_period('M'), R.ret > 0)
    het = stats.chi2_contingency(ct)[1] if ct.shape[1] == 2 and len(ct) > 1 else float('nan')
    print(f'\n## {name}: {(SIGNALS[name].__doc__ or "").strip()}')
    print(f'   trades {len(R)}  win {100 * (R.ret > 0).mean():.1f}%  mean {R.ret.mean():+.3f}%  t {t:+.2f}  | same trades long: mean {R.long_ret.mean():+.3f}%  (signal - long t {t_vs:+.2f})')
    print('   by year: ' + '  '.join(f'{y}: n={int(a)} {b:+.3f}% win {c:.0f}%' for y, (a, b, c) in Y.iterrows()))
    print(f'   months positive {(M > 0).sum()}/{len(M)}   month heterogeneity chi2 p {het:.3f}')
    if months: print(M.round(3).to_string())
    return dict(signal=name, n=len(R), win=round(100 * (R.ret > 0).mean(), 1), mean=round(R.ret.mean(), 4), t=round(t, 2))

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--data', nargs='+', required=True); ap.add_argument('--only', nargs='*'); ap.add_argument('--months', action='store_true')
    ap.add_argument('--tz-shift', type=float, default=1.0); a = ap.parse_args()
    D, B = build(a.data, a.tz_shift); print(f'{len(D)} sessions {D.index.min().date()} -> {D.index.max().date()}')
    names = a.only or list(SIGNALS); out = [x for x in (run(n, SIGNALS[n], D, B, a.months) for n in names) if x]
    k = len([n for n in names if n != 'always_long'])
    print(f'\n{k} signals tested -> Bonferroni 5% two-sided needs |t| > {stats.norm.ppf(1 - 0.025 / max(k, 1)):.2f}')
    print(pd.DataFrame(out).set_index('signal').to_string())
