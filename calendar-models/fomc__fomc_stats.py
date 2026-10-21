"""FOMC decision days, NQ and ES 1-minute Jan 2018 – Oct 2026 (ES to Aug 2026), for Vizard's stages card.
Windows (ET): stage 1 = 14:00 open → 14:29 close (statement); stage 2 = 14:30 open → 16:14 close (press conference to the
RTH close); RTH = 09:30 open → 16:14 close; NY AM = 09:30 open → 10:59 close. Gap = 09:30 open − prior day's 16:14 close.
Baseline = ordinary days (not an FOMC day, not the day after). Each rate is shown for 2018–24 and 2025–26 with a test
against the baseline over 2018–26. Writes fomc_stats.json and the per-meeting records for the script."""
import sys, json, numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, '/home/claude/hm'); from events import FOMC
FO = set(pd.Timestamp(d) for d in FOMC)


def wilson(k, n, z=1.96):
    if n == 0: return (np.nan, np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, c - h, c + h)


def two_prop(k1, n1, k0, n0):
    if not n1 or not n0: return np.nan
    p = (k1 + k0) / (n1 + n0); se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n0))
    return 2 * (1 - stats.norm.cdf(abs((k1 / n1 - k0 / n0) / se))) if se > 0 else 1.0


def rth_table(sym):
    b = pd.read_pickle(f'/home/claude/t3/bars_{sym}_all.pkl')
    b = b[b.ts.dt.normalize() == b.tday]                                   # the calendar day of the trade date
    hm = b.hm
    def first_open(a):
        x = b[(hm >= a) & (hm <= a + 4)]; return x.groupby('tday').Open.first()
    def last_close(a, z):
        x = b[(hm >= a) & (hm <= z)]; return x.groupby('tday').Close.last()
    def hi_lo(a, z):
        x = b[(hm >= a) & (hm <= z)].groupby('tday'); return x.High.max(), x.Low.min()
    T = pd.DataFrame(dict(o930=first_open(930), c1059=last_close(930, 1059), o1400=first_open(1400), c1429=last_close(1400, 1429),
                          o1430=first_open(1430), c1614=last_close(930, 1614), c1359=last_close(930, 1359)))
    T['lastm'] = b[(hm >= 930) & (hm <= 1614)].groupby('tday').hm.max()
    T['amH'], T['amL'] = hi_lo(930, 1059)
    T['rH'], T['rL'] = hi_lo(930, 1614)
    T['pH'], T['pL'] = hi_lo(930, 1359)
    T = T[(T.lastm >= 1600) & T.o930.notna()].copy()                        # full RTH sessions only
    T['pc'] = T.c1614.shift(1)
    T['gap'] = T.o930 - T.pc
    T['fomc'] = T.index.isin(FO)
    T['post'] = pd.Series(T.fomc.values, index=T.index).shift(1, fill_value=False).values
    T['s1'] = T.c1429 - T.o1400; T['s2'] = T.c1614 - T.o1430; T['rth'] = T.c1614 - T.o930; T['am'] = T.c1059 - T.o930
    T['amN'] = T.am.shift(-1)                                                # next day's NY AM
    T['yr'] = T.index.year; T['per'] = np.where(T.yr <= 2024, 'A', 'B')
    return T


def rate_block(name, hit, sel, base, T, extra=''):
    """hit: boolean / NaN series; sel: event days; base: baseline days"""
    out = dict(name=name)
    for nm, m in (('A', T.per == 'A'), ('B', T.per == 'B'), ('all', T.per.notna())):
        s = sel & m & hit.notna(); bb = base & m & hit.notna()
        k, n = int(hit[s].sum()), int(s.sum()); kb, nb = int(hit[bb].sum()), int(bb.sum())
        out[nm] = dict(k=k, n=n, p=k / n if n else np.nan, ci=wilson(k, n)[1:], kb=kb, nb=nb, pb=kb / nb if nb else np.nan, pv=two_prop(k, n, kb, nb))
    a, bq = out['A'], out['B']
    out['held'] = bool(out['all']['pv'] < 0.05 and np.sign(a['p'] - a['pb']) == np.sign(bq['p'] - bq['pb']) == np.sign(out['all']['p'] - out['all']['pb']))
    print(f"  {name:46s} all {out['all']['p'] * 100:5.1f}% (n {out['all']['n']:3d}) vs {out['all']['pb'] * 100:5.1f}% p {out['all']['pv']:.3f} | "
          f"18–24 {a['p'] * 100:5.1f}/{a['pb'] * 100:5.1f} | 25–26 {bq['p'] * 100:5.1f}/{bq['pb'] * 100:5.1f} | {'HELD' if out['held'] else 'no'} {extra}")
    return out


def mean_block(name, v, sel, base, T):
    out = dict(name=name)
    for nm, m in (('A', T.per == 'A'), ('B', T.per == 'B'), ('all', T.per.notna())):
        x = v[sel & m].dropna(); y = v[base & m].dropna()
        out[nm] = dict(n=len(x), m=x.mean(), mb=y.mean(), ratio=x.mean() / y.mean(), pv=stats.mannwhitneyu(x, y).pvalue if len(x) > 3 else np.nan)
    a, bq = out['A'], out['B']
    out['held'] = bool(out['all']['pv'] < 0.05 and np.sign(a['ratio'] - 1) == np.sign(bq['ratio'] - 1) == np.sign(out['all']['ratio'] - 1))
    print(f"  {name:46s} all ×{out['all']['ratio']:.2f} (n {out['all']['n']}) p {out['all']['pv']:.3f} | 18–24 ×{a['ratio']:.2f} | 25–26 ×{bq['ratio']:.2f} | {'HELD' if out['held'] else 'no'}")
    return out


RES = {}
REC = {}
for sym in ['NQ', 'ES']:
    T = rth_table(sym)
    F, P = T.fomc, T.post
    base = ~T.fomc & ~T.post
    R = {}
    print(f'\n══ {sym}: {F.sum()} FOMC days, {base.sum()} baseline days, {T.index.min():%b %Y} – {T.index.max():%b %Y}')
    print(' stage directions (up = closed the window higher)')
    for k, lab in (('s1', 'stage 1 up (14:00–14:30)'), ('s2', 'stage 2 up (14:30–16:14)'), ('rth', 'RTH up (09:30–16:14)')):
        R[k + '_up'] = rate_block(lab, (T[k] > 0).where(T[k] != 0), F, base, T)
    print(' size: mean |move| as % of the 09:30 open, FOMC ÷ baseline')
    for k, lab in (('s1', '|stage 1|'), ('s2', '|stage 2|'), ('rth', '|RTH|'), ('am', '|NY AM|')):
        R[k + '_abs'] = mean_block(lab, (T[k].abs() / T.o930), F, base, T)
    R['amN_abs'] = mean_block('|next-day NY AM| (day after FOMC)', (T.am.abs() / T.o930), P, base, T)
    print(' stage 2 against stage 1')
    R['s2_vs_s1'] = rate_block('stage 2 opposite to stage 1', (np.sign(T.s2) != np.sign(T.s1)).where((T.s1 != 0) & (T.s2 != 0)), F, base, T)
    print(' next day NY AM direction vs the FOMC stages (baseline: same windows on ordinary days → next NY AM)')
    for k, lab in (('s1', 'next NY AM matches stage 1'), ('s2', 'next NY AM matches stage 2'), ('rth', 'next NY AM matches RTH')):
        hit = (np.sign(T.amN) == np.sign(T[k])).where((T.amN != 0) & (T[k] != 0) & T.amN.notna())
        R['nx_' + k] = rate_block(lab, hit, F, base, T)
        # drift-adjusted expectation: if NY AM ignored the stage, matches would come from the two up-rates alone
        sel = F & hit.notna(); pS = (T[k][sel] > 0).mean(); pN = (T.am[base] > 0).mean()
        R['nx_' + k]['expected'] = pS * pN + (1 - pS) * (1 - pN)
        R['nx_' + k]['index'] = R['nx_' + k]['all']['p'] / R['nx_' + k]['expected'] * 100
        R['nx_' + k]['index_base'] = R['nx_' + k]['all']['p'] / R['nx_' + k]['all']['pb'] * 100
        print(f"      drift-expected {R['nx_' + k]['expected'] * 100:.1f}% → index {R['nx_' + k]['index']:.0f} (vs ordinary-day match {R['nx_' + k]['index_base']:.0f})")
    print(' FOMC morning gap')
    up = T.gap > 0
    fillR = np.where(up, T.rL <= T.pc, T.rH >= T.pc); fillP = np.where(up, T.pL <= T.pc, T.pH >= T.pc)
    g0 = T.gap.abs() > 0
    R['gap_fill'] = rate_block('gap filled by 16:14', pd.Series(fillR, T.index).where(g0), F, base, T)
    R['gap_fill14'] = rate_block('gap filled before 14:00', pd.Series(fillP, T.index).where(g0), F, base, T)
    print(' day after FOMC: its own gap during NY AM (open-side quarter = the quarter of the gap next to the 09:30 open)')
    ce = (T.pc + T.o930) / 2; q75 = T.pc + 0.75 * T.gap
    ceTap = np.where(up, T.amL <= ce, T.amH >= ce)
    qHeld = np.where(up, T.amL > q75, T.amH < q75)
    qHeldR = np.where(up, T.rL > q75, T.rH < q75)
    R['nx_ce'] = rate_block('NY AM taps the gap 50%', pd.Series(ceTap, T.index).where(g0), P, base, T)
    R['nx_q'] = rate_block('NY AM holds the open-side quarter', pd.Series(qHeld, T.index).where(g0), P, base, T)
    R['nx_qR'] = rate_block('RTH holds the open-side quarter', pd.Series(qHeldR, T.index).where(g0), P, base, T)
    R['nx_am_dir'] = rate_block('day-after NY AM continues FOMC RTH direction', (np.sign(T.am) == np.sign(T.rth.shift(1))).where((T.am != 0) & (T.rth.shift(1) != 0)), P, base, T)
    RES[sym] = R
    # per-meeting records for the script: date, stage 1 / stage 2 / RTH move (pts), 09:30 open, next NY AM (pts)
    REC[sym] = T[F][['s1', 's2', 'rth', 'o930', 'amN', 'gap']].copy()
    T.to_pickle(f'rth_{sym}.pkl')

# ── same-day NQ vs DXY on FOMC days (DXY futures 5-minute, Jan 2023 – Aug 2026)
f = pd.read_csv('/mnt/user-data/uploads/DXY_2023_2026_5min_continuous.csv')
f['ts'] = pd.to_datetime(f.Date + ' ' + f.Time) + pd.Timedelta(hours=1); f = f.sort_values('ts')
f['tday'] = (f.ts + pd.Timedelta(hours=6)).dt.normalize(); f['hm'] = f.ts.dt.hour * 100 + f.ts.dt.minute
rows = []
for td, g in f.groupby('tday'):
    if td.dayofweek >= 5: continue
    c = g.Contract.value_counts().index[0]; g = g[g.Contract == c]
    gt = g[g.ts.dt.normalize() == td]
    if len(g) < 150 or len(gt) == 0: continue
    fo = lambda a: gt[(gt.hm >= a) & (gt.hm <= a + 4)].Open.iloc[0] if ((gt.hm >= a) & (gt.hm <= a + 4)).any() else np.nan
    lc = lambda a, z: gt[(gt.hm >= a) & (gt.hm <= z)].Close.iloc[-1] if ((gt.hm >= a) & (gt.hm <= z)).any() else np.nan
    rows.append(dict(tday=td, dO=g.Open.iloc[0], dC=g.Close.iloc[-1], x930=fo(930), x1400=fo(1400), x1425=lc(1400, 1425), x1430=fo(1430), x1610=lc(930, 1610)))
DX = pd.DataFrame(rows).set_index('tday')
DX['day'] = DX.dC - DX.dO; DX['s1'] = DX.x1425 - DX.x1400; DX['s2'] = DX.x1610 - DX.x1430; DX['rth'] = DX.x1610 - DX.x930
DXR = {}
for sym in ['NQ', 'ES']:
    T = pd.read_pickle(f'rth_{sym}.pkl')
    b = pd.read_pickle(f'/home/claude/t3/bars_{sym}_all.pkl'); g = b.groupby('tday')
    T['day'] = (g.Close.last() - g.Open.first()).reindex(T.index)
    J = T.join(DX, rsuffix='_dx', how='inner')
    J['per'] = np.where(J.index.year <= 2024, 'A', 'B')
    F = J.fomc; base = ~J.fomc & ~J.post
    print(f'\n══ {sym} vs DXY futures: {F.sum()} FOMC days, {base.sum()} baseline days ({J.index.min():%b %Y} – {J.index.max():%b %Y}); periods 2023–24 / 2025–26')
    R = {}
    for k, lab in (('day', 'same trading day: other way to DXY'), ('rth', 'RTH: other way to DXY'), ('s1', 'stage 1: other way to DXY'), ('s2', 'stage 2: other way to DXY')):
        hit = (np.sign(J[k]) != np.sign(J[k + '_dx'])).where((J[k] != 0) & (J[k + '_dx'] != 0) & J[k + '_dx'].notna())
        R[k] = rate_block(lab, hit, F, base, J)
    # conditional: NQ up when DXY fell in the window (FOMC days)
    for k in ('s1', 's2', 'day'):
        s = F & (J[k + '_dx'] < 0) & (J[k] != 0); s2 = F & (J[k + '_dx'] > 0) & (J[k] != 0)
        R[k + '_cond'] = dict(up_when_dx_dn=float((J[k][s] > 0).mean()), n_dn=int(s.sum()), up_when_dx_up=float((J[k][s2] > 0).mean()), n_up=int(s2.sum()))
        print(f"   {k}: {sym} up {R[k + '_cond']['up_when_dx_dn'] * 100:.0f}% when DXY fell (n {s.sum()}), {R[k + '_cond']['up_when_dx_up'] * 100:.0f}% when it rose (n {s2.sum()})")
    DXR[sym] = R
json.dump(dict(res=RES, dxy=DXR), open('fomc_stats.json', 'w'), indent=1, default=float)
for sym in REC:
    REC[sym].to_pickle(f'rec_{sym}.pkl')
