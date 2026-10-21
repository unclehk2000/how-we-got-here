#!/usr/bin/env python3
"""
COT LAB - test CFTC Traders-in-Financial-Futures positioning against forward NQ returns and range.

  python cot_lab.py --cot COT_NQ_TFF_2015_2026.csv --minute "hist/*.csv"        # 1-min NQ files (uses hydra.py loaders)
  python cot_lab.py --cot COT_NQ_TFF.csv --weekly nq_weekly.csv                  # Barchart weekly export, for long history

COT csv columns: report_date,open_interest,am_long,am_short,lev_long,lev_short (one row per Tuesday report).
Timing: a report dated Tuesday is published Friday 15:30 ET.
  minute mode: entry at the first RTH open after release (Monday), exit h weeks later at the RTH open.
  weekly mode: entry at the release-week Friday close, exit h Friday closes later.
Reports delayed by the Oct-Dec 2025 government shutdown are excluded (--exclude to change).
Prints: correlation of each feature with forward 1w/4w return and next-week range (Newey-West p, Bonferroni),
COT-index extremes, whether COT adds to next-week range beyond past range, and the latest positioning snapshot.
"""
import argparse, glob, math, sys
import numpy as np, pandas as pd
from scipy import stats

def features(C):
    C = C.copy()
    C['am'] = (C.am_long - C.am_short) / C.open_interest * 100
    C['lev'] = (C.lev_long - C.lev_short) / C.open_interest * 100
    for g in ('am', 'lev'):
        for w in (26, 52, 156):
            lo, hi = C[g].rolling(w).min(), C[g].rolling(w).max(); C[f'{g}_idx{w}'] = 100 * (C[g] - lo) / (hi - lo)
        for w in (52, 156): C[f'{g}_z{w}'] = (C[g] - C[g].rolling(w).mean()) / C[g].rolling(w).std()
        C[f'{g}_d1'] = C[g].diff(); C[f'{g}_d4'] = C[g].diff(4)
    return C

def daily_from_minute(pats):
    from datetime import time as T
    from hydra import load, sessions, pick_active
    df = load(pats); S = pick_active(sessions(df, T(9, 25))); S = S[S.n_rth >= 200].copy()
    prev = S.shift(1); gap = S.index.to_series().diff().dt.days
    r = np.where(S.k == prev.k, np.log(S.ro / prev.ro), np.log(prev.rc / prev.ro))    # switch day: overnight set to 0
    S['r'] = pd.Series(r, index=S.index).where(gap <= 4); S['lr'] = np.log(S.rh / S.rl); return S

def forward_minute(C, S, h):
    days = S.index; ret, rng, past = [], [], []
    for t in C.index:
        i = days.searchsorted(t + pd.Timedelta(days=4))
        ok = i < len(days) and (days[i] - t).days <= 7
        j = days.searchsorted(days[i] + pd.Timedelta(days=7 * h)) if ok else len(days)
        if not ok or j >= len(days) or (days[j] - days[i]).days > 7 * h + 3 or S.r.iloc[i + 1:j + 1].isna().any():
            ret.append(np.nan); rng.append(np.nan); past.append(np.nan); continue
        ret.append(100 * (math.exp(S.r.iloc[i + 1:j + 1].sum()) - 1)); rng.append(100 * S.lr.iloc[i:j].mean())
        p = S.lr.iloc[max(0, i - 20):i]; past.append(100 * p.mean() if len(p) == 20 else np.nan)
    return ret, rng, past

def forward_weekly(C, W, h):
    fri = W.index; ret, rng, past = [], [], []
    for t in C.index:
        i = fri.searchsorted(t + pd.Timedelta(days=3))           # week bar containing the release Friday
        if i + h >= len(fri) or (fri[i] - t).days > 7: ret.append(np.nan); rng.append(np.nan); past.append(np.nan); continue
        ret.append(100 * (W.c.iloc[i + h] / W.c.iloc[i] - 1)); rng.append(100 * np.log(W.h.iloc[i + 1] / W.l.iloc[i + 1]))
        past.append(100 * np.log(W.h.iloc[max(0, i - 3):i + 1] / W.l.iloc[max(0, i - 3):i + 1]).mean() if i >= 3 else np.nan)
    return ret, rng, past

def nw_p(x, y, L):
    x = (x - x.mean()) / x.std(); y = (y - y.mean()) / y.std(); u = x * y; n = len(u); m = u.mean(); v = ((u - m) ** 2).mean()
    for l in range(1, L + 1): v += 2 * (1 - l / (L + 1)) * ((u[l:] - m) * (u[:-l] - m)).mean()
    t = m / math.sqrt(v / n); return t, 2 * (1 - stats.norm.cdf(abs(t)))

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--cot', required=True); ap.add_argument('--minute', nargs='*'); ap.add_argument('--weekly')
    ap.add_argument('--exclude', default='2025-09-30:2025-12-31'); a = ap.parse_args()
    C = pd.read_csv(a.cot, parse_dates=['report_date']).set_index('report_date').sort_index(); C = features(C)
    x0, x1 = a.exclude.split(':') if a.exclude else ('1900-01-01', '1900-01-01')
    C['valid'] = ~((C.index >= x0) & (C.index <= x1))
    if a.weekly:
        W = pd.read_csv(a.weekly, dtype=str); W = W[W.Time.str.match(r'\d{4}-\d\d-\d\d', na=False)]
        W = pd.DataFrame({'h': pd.to_numeric(W.High).values, 'l': pd.to_numeric(W.Low).values, 'c': pd.to_numeric(W.Latest).values},
                         index=pd.to_datetime(W.Time) + pd.Timedelta(days=4)).sort_index()   # Monday-dated bars -> Friday
        fw = lambda h: forward_weekly(C, W, h)
    elif a.minute:
        S = daily_from_minute(a.minute); fw = lambda h: forward_minute(C, S, h)
    else: sys.exit('give --minute files or --weekly file')
    C['ret1'], C['rng1'], C['rng_past'] = fw(1); C['ret4'] = fw(4)[0]
    G = C[C.valid & C.ret1.notna()]
    if G.empty: sys.exit('no weeks overlap between COT and price data')
    print(f'weeks tested {len(G)} ({G.index.min().date()} -> {G.index.max().date()})  1w mean {G.ret1.mean():+.3f}% up {100 * (G.ret1 > 0).mean():.0f}%')
    feats = ['am', 'lev'] + [c for c in C if c.startswith(('am_', 'lev_')) and c not in ('am_long', 'am_short', 'lev_long', 'lev_short')]
    rows = []
    for f in feats:
        for tgt, L in (('ret1', 2), ('ret4', 6), ('rng1', 2)):
            g = C[C.valid & C[f].notna() & C[tgt].notna()]
            if len(g) < 60: continue
            t, p = nw_p(g[f].values, g[tgt].values, L)
            rows.append(dict(feature=f, target=tgt, n=len(g), rho=round(stats.spearmanr(g[f], g[tgt])[0], 3), t_nw=round(t, 2), p=round(p, 4)))
    R = pd.DataFrame(rows); bon = 0.05 / len(R)
    for tg in ('ret1', 'ret4', 'rng1'):
        print(f'\n== {tg}  (Bonferroni p < {bon:.5f})'); print(R[R.target == tg].sort_values('p').head(8).to_string(index=False))
    print('\n== extremes (COT index) -> next-week return')
    for f in ('am_idx52', 'am_idx156', 'lev_idx52', 'lev_idx156'):
        for lab, m in (('>=80', G[f] >= 80), ('<=20', G[f] <= 20)):
            g = G[m]
            if len(g) >= 5:
                print(f'  {f:10s} {lab}  n={len(g):3d}  1w {g.ret1.mean():+.3f}%  up {100 * (g.ret1 > 0).mean():.0f}%  4w {g.ret4.mean():+.3f}%  MW p {stats.mannwhitneyu(g.ret1, G[~m].ret1).pvalue:.3f}')
    V = C[C.valid].dropna(subset=['rng1', 'rng_past', 'am_idx156'])
    y = np.log(V.rng1); X0 = np.column_stack([np.ones(len(V)), np.log(V.rng_past)]); X1 = np.column_stack([X0, V.am_idx156])
    r2 = lambda X: 1 - ((y - X @ np.linalg.lstsq(X, y, rcond=None)[0]) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    print(f'\n== next-week range: R2 past 4-week range only {r2(X0):.3f}  + am_idx156 {r2(X1):.3f}')
    last = C.iloc[-1]
    print(f'\n== latest report {C.index[-1].date()}: asset mgr net {last.am:+.1f}% OI (52w idx {last.am_idx52:.0f}, 156w idx {last.am_idx156:.0f}, wk chg {last.am_d1:+.1f})'
          f' | lev funds net {last.lev:+.1f}% OI (52w idx {last.lev_idx52:.0f}, 156w idx {last.lev_idx156:.0f}, wk chg {last.lev_d1:+.1f})')
