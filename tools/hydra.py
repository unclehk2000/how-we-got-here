#!/usr/bin/env python3
"""
HYDRA - NQ pre-market decision heads. Run during ETH, before the 09:30 ET open.

  python hydra.py backtest  --data "hist/*.csv" [--cutoff 09:25] [--oos-start 2024-01] [--events events.csv]
        Walk-forward test of every head. Writes hydra_model.json (frozen coefficients + validated stats).
  python hydra.py premarket --data "recent/*.csv" [--sofr 3.9 --div 0.7] [--events events.csv]
        Today's heads from the frozen model. Appends one row to hydra_log.csv.
  python hydra.py score     --data "recent/*.csv"
        Fills realised RTH outcomes into hydra_log.csv and prints the forward record.

Data: Barchart 1-min CSVs in either format
  per-contract download  Time,Open,High,Low,Latest,...,Volume   (contract read from file name, e.g. nqz26_...)
  continuous export      Date,Time,Open,High,Low,Close,...,Volume,Contract
Barchart time stamps are US Central; --tz-shift 1 (default) converts to ET.
For the carry head include files for BOTH the expiring and the next contract.
Requires numpy, pandas, scipy.
"""
import argparse, glob, json, math, os, re, sys, warnings
from datetime import date, datetime, time as T, timedelta
import numpy as np, pandas as pd
from scipy import stats
warnings.filterwarnings('ignore')

MCODE = {'H': 3, 'M': 6, 'U': 9, 'Z': 12}; CODEM = {v: k for k, v in MCODE.items()}
PV = 20.0                      # USD per NQ point
RTH0, RTH1 = T(9, 30), T(16, 14)
MIN_RTH, MIN_LAG, MIN_PRE = 300, 200, 100
KS = [0.25, 0.5, 0.75, 1.0]
FOMC = ['2018-01-31','2018-03-21','2018-05-02','2018-06-13','2018-08-01','2018-09-26','2018-11-08','2018-12-19',
        '2022-01-26','2022-03-16','2022-05-04','2022-06-15','2022-07-27','2022-09-21','2022-11-02','2022-12-14',
        '2023-02-01','2023-03-22','2023-05-03','2023-06-14','2023-07-26','2023-09-20','2023-11-01','2023-12-13',
        '2024-01-31','2024-03-20','2024-05-01','2024-06-12','2024-07-31','2024-09-18','2024-11-07','2024-12-18',
        '2025-01-29','2025-03-19','2025-05-07','2025-06-18','2025-07-30','2025-09-17','2025-10-29','2025-12-10',
        '2026-01-28','2026-03-18','2026-04-29','2026-06-17','2026-07-29','2026-09-16','2026-10-28','2026-12-09']

# ---------------------------------------------------------------- contract calendar
def third_friday(y, m):
    d = date(y, m, 15); return d + timedelta((4 - d.weekday()) % 7)
def expiry(k): return third_friday(2000 + int(k[-2:]), MCODE[k[2].upper()])
def roll_date(k): return expiry(k) - timedelta(8)          # CME equity-index roll date (Thursday, 8 days before expiry)
def cycle(d, n=3):
    out, y = [], d.year
    while len(out) < n:
        for m in (3, 6, 9, 12):
            if third_friday(y, m) >= d and len(out) < n: out.append(f'NQ{CODEM[m]}{y % 100:02d}')
        y += 1
    return out
def active_contract(d):
    a, b, _ = cycle(d); return b if d >= roll_date(a) else a

# ---------------------------------------------------------------- data
def load(patterns, tz_shift=1.0):
    files = sorted({f for p in patterns for f in glob.glob(p)})
    if not files: sys.exit(f'no files match {patterns}')
    fr = []
    for f in files:
        d = pd.read_csv(f, dtype=str)
        if 'Contract' in d.columns:
            d = d[d['Date'].str.match(r'\d{4}-\d\d-\d\d', na=False)].copy()
            d['dt'] = d['Date'] + ' ' + d['Time']; d = d.rename(columns={'Close': 'c', 'Contract': 'k'})
        elif 'Time' in d.columns:
            d = d[d['Time'].str.match(r'\d{4}-\d\d-\d\d \d', na=False)].copy()     # intraday rows only
            m = re.search(r'nq([hmuz])(\d\d)', os.path.basename(f), re.I)
            if not m: print(f'  skip {os.path.basename(f)}: contract not in file name'); continue
            d['dt'] = d['Time']; d['k'] = f'NQ{m.group(1).upper()}{m.group(2)}'; d = d.rename(columns={'Latest': 'c'})
        else: continue
        if d.empty: continue
        d = d.rename(columns={'Open': 'o', 'High': 'h', 'Low': 'l', 'Volume': 'v'})
        dt = pd.to_datetime(d.dt)
        if dt.sort_values().diff().dt.total_seconds().median() != 60:
            print(f'  skip {os.path.basename(f)}: not 1-minute bars'); continue
        fr.append(d[['dt', 'o', 'h', 'l', 'c', 'v', 'k']])
    if not fr: sys.exit('no usable 1-minute NQ files')
    df = pd.concat(fr)
    for c in 'ohlcv': df[c] = pd.to_numeric(df[c].str.replace(',', ''), errors='coerce')
    df['dt'] = pd.to_datetime(df.dt) + timedelta(hours=tz_shift)
    df = df.dropna(subset=['o', 'h', 'l', 'c']).drop_duplicates(['dt', 'k']).sort_values('dt').reset_index(drop=True)
    df['v'] = df.v.fillna(0); df['t'] = df.dt.dt.time
    n = df.dt.dt.normalize(); df['td'] = n.where(df.dt.dt.hour < 18, n + pd.Timedelta(days=1))
    return df

def sessions(df, cutoff):
    key = ['td', 'k']
    r = df[(df.t >= RTH0) & (df.t <= RTH1)].groupby(key)
    p = df[(df.t >= T(18, 0)) | (df.t < cutoff)].groupby(key)
    S = pd.DataFrame({'oh': p.h.max(), 'ol': p.l.min(), 'ref': p.c.last(), 'n_pre': p.size(), 't_ref': p.dt.last()})
    S = S.join(pd.DataFrame({'ro': r.o.first(), 'rh': r.h.max(), 'rl': r.l.min(), 'rc': r.c.last(), 'n_rth': r.size()}), how='outer')
    S = S.join(df.groupby(key).v.sum().rename('vol')).reset_index()
    S['n_rth'] = S.n_rth.fillna(0); S['n_pre'] = S.n_pre.fillna(0)
    return S

def load_events(path):
    ev = {'fomc': set(pd.to_datetime(FOMC))}
    if path and os.path.exists(path):
        e = pd.read_csv(path, comment='#', header=None, names=['date', 'type', 'note'], dtype=str).dropna(subset=['date', 'type'])
        for d, t in zip(e.date, e.type):
            ev.setdefault(t.strip().lower(), set()).add(pd.Timestamp(d.strip()))
    return ev

def features(S, ev):
    S = S.sort_values(['k', 'td']).reset_index(drop=True)
    rng = np.log(100 * (S.rh - S.rl) / S.ro)
    S['sig'] = rng.where(S.n_rth >= MIN_RTH)
    S['ret'] = (100 * (S.rc / S.ro - 1)).where(S.n_rth >= MIN_RTH)
    lagsrc = rng.where(S.n_rth >= MIN_LAG)
    S['sig_on'] = np.log(100 * (S.oh - S.ol) / S.ref).where(S.n_pre >= MIN_PRE)
    g = S.groupby('k')
    S['cont'] = (g.td.diff().dt.days <= 4).astype(float)
    for i in (1, 2, 3):
        ok = S.groupby('k').cont.transform(lambda s: s.rolling(i).min()) == 1
        S[f'sig_l{i}'] = lagsrc.groupby(S.k).shift(i).where(ok)
    ok1 = S.cont == 1
    S['dsig_on'] = (S.sig_on - g.sig_on.shift(1)).where(ok1)
    prc = g.rc.shift(1).where(ok1 & (g.n_rth.shift(1) >= MIN_LAG))
    S['f_on_s'] = 100 * (S.ref / prc - 1)
    S['f_on'] = S.f_on_s.abs()
    S['ret_l1'] = g.ret.shift(1).where(ok1)
    wd = S.td.dt.weekday
    for i, n in enumerate(['mon', 'tue', 'wed', 'thu']): S['z_' + n] = (wd == i).astype(float)
    # NFP: first Friday of the month unless the events file lists nfp dates for that month
    S['z_nfp'] = 0.0
    listed = {(d.year, d.month) for d in ev.get('nfp', set())}
    ff = S.td[(wd == 4) & (S.td.dt.day <= 7)]
    S.loc[ff.index, 'z_nfp'] = [0.0 if (d.year, d.month) in listed else 1.0 for d in ff]
    S.loc[S.td.isin(ev.get('nfp', set())), 'z_nfp'] = 1.0
    for t, ds in ev.items():
        if t == 'nfp': continue
        S['z_' + t] = S.td.isin(ds).astype(float)
    return S

def pick_active(S):
    """one row per trading day: the contract with the highest session volume"""
    return S.sort_values('vol').drop_duplicates('td', keep='last').set_index('td').sort_index()

# ---------------------------------------------------------------- stats helpers
def ols(X, y):
    b = np.linalg.lstsq(X, y, rcond=None)[0]; e = y - X @ b
    return b, e.std(ddof=X.shape[1])
def nw_se(u, L=5):          # Newey-West long-run variance of the columns of u (n x k)
    S = u.T @ u
    for l in range(1, L + 1):
        G = u[l:].T @ u[:-l]; S += (1 - l / (L + 1)) * (G + G.T)
    return S
def nw_t(X, y, b, L=5):
    e = y - X @ b; XtXi = np.linalg.inv(X.T @ X); V = XtXi @ nw_se(X * e[:, None], L) @ XtXi
    return b / np.sqrt(np.diag(V))
def dm_test(e1, e2, L=5):   # Diebold-Mariano on squared errors; >0 stat means model 1 is worse
    d = e1 ** 2 - e2 ** 2; n = len(d)
    v = nw_se((d - d.mean())[:, None], L)[0, 0] / n
    s = d.mean() / math.sqrt(v / n); return s, 2 * (1 - stats.norm.cdf(abs(s)))
def wilson(k, n, z=1.96):
    if n == 0: return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); a = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - a) / d, (c + a) / d
def pct(x): return round(100 * float(x), 1)

def first_touch(h, l, c, o, L):
    iu = np.flatnonzero(h >= o + L); idn = np.flatnonzero(l <= o - L)
    if not len(iu) and not len(idn): return None
    side = 1 if (not len(idn) or (len(iu) and iu[0] <= idn[0])) else -1
    i = iu[0] if side == 1 else idn[0]; hh, ll = h[i:].max(), l[i:].min()
    if side == 1: ext, back, opp = hh >= o + 2 * L, ll <= o, ll <= o - L
    else:         ext, back, opp = ll <= o - 2 * L, hh >= o, hh >= o + L
    return (np.sign(c[-1] - o) == side, ext, back, opp, i)

# ---------------------------------------------------------------- backtest
def backtest(a):
    cutoff = T(*map(int, a.cutoff.split(':')))
    print(f'loading ... cutoff {a.cutoff} ET')
    df = load(a.data, a.tz_shift); ev = load_events(a.events)
    S = features(sessions(df, cutoff), ev); A = pick_active(S)
    extra = [c for c in A if c.startswith('z_') and c not in ('z_mon', 'z_tue', 'z_wed', 'z_thu', 'z_fomc', 'z_nfp')]
    extra_ok = [c for c in extra if A[c].sum() >= 8]
    cols = ['sig_l1', 'sig_l2', 'sig_l3', 'dsig_on', 'f_on', 'z_mon', 'z_tue', 'z_wed', 'z_thu', 'z_fomc', 'z_nfp'] + extra_ok
    D = A.dropna(subset=cols + ['sig']).copy()
    X = np.column_stack([np.ones(len(D))] + [D[c].values for c in cols]); y = D.sig.values; names = ['const'] + cols
    print(f'{len(A)} sessions, {len(D)} model rows {D.index.min().date()} -> {D.index.max().date()}')
    # walk-forward, monthly refit, expanding window
    oos = pd.Period(a.oos_start, 'M'); rows = []
    for mo in pd.period_range(oos, D.index.max().to_period('M'), freq='M'):
        tr = D.index < mo.start_time; te = (D.index >= mo.start_time) & (D.index <= mo.end_time)
        if te.sum() == 0 or tr.sum() < 200: continue
        b, sd = ols(X[tr], y[tr]); bA, _ = ols(X[tr][:, :4], y[tr])
        rows.append(pd.DataFrame({'fc': X[te] @ b, 'sd': sd, 'fcA': X[te][:, :4] @ bA}, index=D.index[te]))
    O = pd.concat(rows).join(D[['ro', 'rh', 'rl', 'rc', 'sig', 'k', 'ref']])
    O['naive'] = A.sig.shift(1).rolling(20, min_periods=10).mean().reindex(O.index)
    O = O.dropna(subset=['naive'])
    yo = O.sig.values; e = yo - O.fc.values; eA = yo - O.fcA.values; eN = yo - O.naive.values
    r2 = lambda err: 1 - (err ** 2).mean() / ((yo - yo.mean()) ** 2).mean()
    O['F'] = np.exp(O.fc); O['Fpts'] = O.F / 100 * O.ro
    O['up'] = O.rh - O.ro; O['dn'] = O.ro - O.rl; O['rng'] = O.rh - O.rl
    O['eff'] = (O.rc - O.ro).abs() / O.rng
    q1, q2 = np.quantile(O.F, [1 / 3, 2 / 3]); O['q'] = np.where(O.F < q1, 'Low', np.where(O.F < q2, 'Mid', 'High'))
    z10 = stats.norm.ppf(0.9)
    lo10 = np.exp(O.fc - z10 * O.sd); hi90 = np.exp(O.fc + z10 * O.sd); realp = 100 * O.rng / O.ro
    H1 = dict(n_oos=len(O), oos=f'{O.index.min().date()} -> {O.index.max().date()}',
              r2=round(r2(e), 3), corr=round(float(np.corrcoef(yo, O.fc)[0, 1]), 3),
              r2_ar3=round(r2(eA), 3), r2_naive20=round(r2(eN), 3),
              dm_vs_ar3_p=round(dm_test(e, eA)[1], 4), dm_vs_naive20_p=round(dm_test(e, eN)[1], 4),
              ratio_median=round(float((O.rng / O.Fpts).median()), 3),
              ratio_iqr=[round(float(x), 2) for x in (O.rng / O.Fpts).quantile([.25, .75])],
              cover_p10_p90=pct(((realp >= lo10) & (realp <= hi90)).mean()),
              below_p10=pct((realp < lo10).mean()), above_p90=pct((realp > hi90).mean()),
              terciles_F_pct=[round(q1, 3), round(q2, 3)])
    bands = {}
    for k in KS:
        L = k * O.Fpts; anyr = (O.up >= L) | (O.dn >= L); both = (O.up >= L) & (O.dn >= L)
        row = {'any': pct(anyr.mean()), 'both': pct(both.mean())}
        for g in ('Low', 'Mid', 'High'):
            m = O.q == g; row[g] = {'any': pct(anyr[m].mean()), 'both': pct(both[m].mean()), 'n': int(m.sum())}
        bands[str(k)] = row
    fixed = O.Fpts.median(); fx = {}
    for k in KS:
        hit = (O.up >= k * fixed) | (O.dn >= k * fixed); ct = pd.crosstab(O.q, hit)
        fx[str(k)] = {'pts': round(k * fixed), **{g: pct(hit[O.q == g].mean()) for g in ('Low', 'Mid', 'High')},
                      'chi2_p': round(float(stats.chi2_contingency(ct)[1]), 4) if ct.shape[1] == 2 else None}
    H1['bands'] = bands; H1['fixed_point_bands'] = fx
    # H2 day type
    tr_ = O.eff >= 0.5; ct = pd.crosstab(O.q, tr_)
    H2 = {g: {'trend_rate': pct(tr_[O.q == g].mean()), 'ci': [pct(x) for x in wilson(int(tr_[O.q == g].sum()), int((O.q == g).sum()))],
              'two_sided_0.5F': pct(((O.up >= .5 * O.Fpts) & (O.dn >= .5 * O.Fpts))[O.q == g].mean())} for g in ('Low', 'Mid', 'High')}
    H2['chi2_p'] = round(float(stats.chi2_contingency(ct)[1]), 4); H2['overall_trend_rate'] = pct(tr_.mean())
    # H3 post-touch behaviour vs within-day shuffle null
    print('post-touch test with shuffle null ...')
    rth = df[(df.t >= RTH0) & (df.t <= RTH1)]
    G = {key: g for key, g in rth.groupby(['td', 'k'])}
    days = []
    for d, r in O.iterrows():
        b = G.get((d, r.k))
        if b is None or len(b) < MIN_RTH: continue
        days.append((r.Fpts * 0.5, r.ro, b.h.values, b.l.values, b.c.values))
    def h3(ds):
        res = [first_touch(h, l, c, o, L) for L, o, h, l, c in ds]; res = [x for x in res if x is not None]
        arr = np.array([x[:4] for x in res], float); return arr.mean(0), len(res), [x[4] for x in res]
    real, nt, idx = h3(days); rng = np.random.default_rng(7); sims = []
    for _ in range(a.shuffles):
        P = []
        for L, o, h, l, c in days:
            prev = np.r_[o, c[:-1]]; mv, hu, ld = c - prev, h - prev, l - prev
            p = rng.permutation(len(c)); cs = o + np.cumsum(mv[p]); base = np.r_[o, cs[:-1]]
            P.append((L, o, base + hu[p], base + ld[p], cs))
        sims.append(h3(P)[0])
    sims = np.array(sims); H3 = {'n_touch_days': nt, 'n_days': len(days)}
    for j, n in enumerate(['closes_same_side', 'extends_to_1.0F', 'back_through_open', 'opposite_0.5F']):
        m = sims[:, j].mean(); p = float((np.abs(sims[:, j] - m) >= abs(real[j] - m)).mean())
        H3[n] = {'real': pct(real[j]), 'null': pct(m), 'null_95': [pct(np.percentile(sims[:, j], 2.5)), pct(np.percentile(sims[:, j], 97.5))], 'p': round(p, 3)}
    # H4 calendar coefficients (full sample, HAC)
    b, sd = ols(X, y); t = nw_t(X, y, b)
    H4 = {n: {'coef': round(float(bb), 4), 'pct_effect': pct(math.exp(bb) - 1), 't': round(float(tt), 2)} for n, bb, tt in zip(names, b, t)}
    H4['events_flag_only'] = [c[2:] for c in extra if c not in extra_ok]
    # H5 direction (rejected unless it passes)
    Dd = A.dropna(subset=['ret', 'ret_l1', 'f_on_s']).copy()
    Xd = np.column_stack([np.ones(len(Dd)), Dd.ret_l1, Dd.f_on_s, Dd.z_mon, Dd.z_tue, Dd.z_wed, Dd.z_thu, Dd.z_fomc, Dd.z_nfp]); yd = Dd.ret.values
    pr = []
    for mo in pd.period_range(oos, Dd.index.max().to_period('M'), freq='M'):
        tr = Dd.index < mo.start_time; te = (Dd.index >= mo.start_time) & (Dd.index <= mo.end_time)
        if te.sum() == 0 or tr.sum() < 200: continue
        bd, _ = ols(Xd[tr], yd[tr]); pr.append(pd.Series(Xd[te] @ bd, index=Dd.index[te]))
    pr = pd.concat(pr); yr = Dd.ret.reindex(pr.index); hit = (np.sign(pr) == np.sign(yr)); longr = (yr > 0).mean()
    H5 = {'n': len(pr), 'hit': pct(hit.mean()), 'always_long_hit': pct(longr),
          'p_vs_always_long': round(float(stats.binomtest(int(hit.sum()), len(hit), longr).pvalue), 4),
          'strategy_sum_pct': round(float((np.sign(pr) * yr).sum()), 1), 'long_sum_pct': round(float(yr.sum()), 1),
          'oos_r2': round(float(1 - ((yr - pr) ** 2).sum() / ((yr - yr.mean()) ** 2).sum()), 3)}
    H5['validated'] = bool(H5['p_vs_always_long'] < 0.05 and H5['hit'] > H5['always_long_hit'] and H5['oos_r2'] > 0)
    # H6 carry: roll window, expiry days, implied-carry history from overlapping contracts
    Dv = A.dropna(subset=['sig']).copy()
    exp_ = {d: expiry(cycle(d.date())[0]) for d in Dv.index}
    rw = np.array([(exp_[d] - timedelta(8)) <= d.date() <= exp_[d] for d in Dv.index])
    tt_r = stats.ttest_ind(Dv.sig[rw], Dv.sig[~rw], equal_var=False); tt_a = stats.ttest_ind(Dv.ret[rw].abs(), Dv.ret[~rw].abs(), equal_var=False)
    exps = sorted({expiry(cycle(d.date())[0]) for d in A.index})
    exps = [e for e in exps if A.index.min().date() <= e <= A.index.max().date()]
    H6 = {'roll_window_days': int(rw.sum()), 'range_ratio_roll_vs_other': round(float(math.exp(Dv.sig[rw].mean() - Dv.sig[~rw].mean())), 3),
          'range_p': round(float(tt_r.pvalue), 3), 'abs_ret_p': round(float(tt_a.pvalue), 3),
          'expiry_fridays': len(exps), 'expiry_fridays_with_rth_in_data': int(sum(pd.Timestamp(e) in Dv.index for e in exps))}
    C = carry_history(S)
    if a.carry_hist: C = pd.concat([C, read_carry_file(a.carry_hist)]).sort_index(); C = C[~C.index.duplicated(keep='last')]
    H6['carry_obs_days'] = len(C)
    if len(C):
        H6['carry_obs'] = {str(d.date()): round(v, 3) for d, v in C.carry.items()}
        W = C.carry.resample('W-FRI').last().dropna(); rv = A.sig.resample('W-FRI').mean()
        dW = W.diff(); nxt = rv.shift(-1).reindex(dW.index); ok = dW.notna() & nxt.notna()
        H6['weekly_pairs'] = int(ok.sum())
        if ok.sum() >= 20:
            rho, p = stats.spearmanr(dW[ok], nxt[ok]); H6['dcarry_vs_next_week_range'] = {'rho': round(rho, 3), 'p': round(p, 4)}
        else: H6['dcarry_vs_next_week_range'] = f'needs >=20 weekly pairs (have {int(ok.sum())})'
    model = dict(created=datetime.now().isoformat(timespec='minutes'), cutoff=a.cutoff, tz_shift=a.tz_shift,
                 train=f'{D.index.min().date()} -> {D.index.max().date()}', n_train=len(D),
                 names=names, coef=[float(x) for x in b], sd=float(sd), tercile_F_pct=[q1, q2],
                 H1_range=H1, H2_daytype=H2, H3_post_touch=H3, H4_calendar=H4, H5_direction=H5, H6_carry=H6)
    json.dump(model, open(a.model, 'w'), indent=1, default=str)
    O.to_csv(a.model.replace('.json', '_oos.csv'))
    print_backtest(model); print(f'\nwrote {a.model}')

def carry_history(S):
    """implied annualised carry from days where both the expiring and next contract traded (RTH close, same day)"""
    out = {}
    for d, g in S[S.n_rth >= MIN_LAG].groupby('td'):
        f, n = cycle(d.date())[:2]; gg = g.set_index('k')
        if f in gg.index and n in gg.index:
            dT = (expiry(n) - expiry(f)).days
            out[d] = math.log(gg.rc[n] / gg.rc[f]) * 365 / dT * 100
    return pd.DataFrame({'carry': pd.Series(out, dtype=float)})
def read_carry_file(p):
    """CSV: date,front,next  (settlements of expiring and next contract)"""
    c = pd.read_csv(p, parse_dates=['date']); out = {}
    for d, fr, nx in zip(c.date, c.front, c.next):
        f, n = cycle(d.date())[:2]; out[d] = math.log(nx / fr) * 365 / (expiry(n) - expiry(f)).days * 100
    return pd.DataFrame({'carry': pd.Series(out, dtype=float)})

def print_backtest(m):
    H1, H2, H3, H4, H5, H6 = (m[k] for k in ('H1_range', 'H2_daytype', 'H3_post_touch', 'H4_calendar', 'H5_direction', 'H6_carry'))
    print(f"\n=== H1 RANGE  OOS {H1['oos']}  n={H1['n_oos']}")
    print(f"  R2 {H1['r2']}  corr {H1['corr']}  | AR(3) R2 {H1['r2_ar3']} (DM p {H1['dm_vs_ar3_p']})  20d-mean R2 {H1['r2_naive20']} (DM p {H1['dm_vs_naive20_p']})")
    print(f"  realised/forecast median {H1['ratio_median']} IQR {H1['ratio_iqr']}   P10-P90 band covers {H1['cover_p10_p90']}% (target 80)")
    print('  touch of open +/- k*F      any   both |  any by tercile Low / Mid / High')
    for k, r in H1['bands'].items():
        print(f"   k={k:5s}                {r['any']:5.1f} {r['both']:5.1f} |  {r['Low']['any']:5.1f} / {r['Mid']['any']:5.1f} / {r['High']['any']:5.1f}")
    print('  fixed-point bands (does the forecast discriminate?)')
    for k, r in H1['fixed_point_bands'].items():
        print(f"   {r['pts']:5d} pts  Low {r['Low']:5.1f}  Mid {r['Mid']:5.1f}  High {r['High']:5.1f}   chi2 p {r['chi2_p']}")
    print(f"=== H2 DAY TYPE (trend day = |close-open| >= 50% of range)  chi2 p {H2['chi2_p']}")
    for g in ('Low', 'Mid', 'High'): print(f"   {g:4s} trend {H2[g]['trend_rate']}% CI {H2[g]['ci']}  two-sided {H2[g]['two_sided_0.5F']}%")
    print(f"=== H3 AFTER FIRST 0.5F TOUCH  n={H3['n_touch_days']}/{H3['n_days']}  (null = same bars shuffled within the day)")
    for k in ('closes_same_side', 'extends_to_1.0F', 'back_through_open', 'opposite_0.5F'):
        r = H3[k]; print(f"   {k:18s} {r['real']:5.1f}%  null {r['null']:5.1f}% {r['null_95']}  p {r['p']}")
    print('=== H4 MODEL TERMS (full sample, Newey-West t)')
    for n in m['names']: print(f"   {n:8s} {H4[n]['coef']:+.3f}  ({H4[n]['pct_effect']:+.1f}% range)  t {H4[n]['t']:+.2f}")
    if H4['events_flag_only']: print('   flag-only events (<8 in history):', ', '.join(H4['events_flag_only']))
    print(f"=== H5 DIRECTION  OOS n={H5['n']}  hit {H5['hit']}% vs always-long {H5['always_long_hit']}% (p {H5['p_vs_always_long']})  R2 {H5['oos_r2']}  -> {'VALIDATED' if H5['validated'] else 'REJECTED'}")
    print(f"=== H6 CARRY / ROLL  roll-window days {H6['roll_window_days']}: range x{H6['range_ratio_roll_vs_other']} (p {H6['range_p']}), |ret| p {H6['abs_ret_p']}")
    print(f"   expiry Fridays in span {H6['expiry_fridays']}, with RTH in active data {H6['expiry_fridays_with_rth_in_data']}")
    print(f"   implied-carry observations {H6['carry_obs_days']};  dCarry -> next-week range: {H6.get('dcarry_vs_next_week_range', 'n/a')}")

# ---------------------------------------------------------------- premarket
def premarket(a):
    m = json.load(open(a.model)); cutoff = T(*map(int, m['cutoff'].split(':')))
    df = load(a.data, m['tz_shift']); ev = load_events(a.events)
    if a.asof: df = df[df.dt <= pd.Timestamp(a.asof)]          # replay a past morning
    last = df.dt.max(); td = df.td.max(); tdd = td.date()
    run_t = last.time(); after_open = run_t >= RTH0
    use_cut = cutoff if after_open else (datetime.combine(tdd, run_t) + timedelta(minutes=1)).time()
    S = features(sessions(df, use_cut), ev)
    k = a.contract or active_contract(tdd)
    today = S[(S.td == td) & (S.k == k)]
    if today.empty:
        alt = S[S.td == td].sort_values('vol')
        if alt.empty: sys.exit(f'no ETH data for {tdd}')
        k = alt.k.iloc[-1]; today = alt.iloc[[-1]]
    r = today.iloc[0]
    cols = m['names'][1:]
    for c in cols:
        if c not in r.index: r[c] = 0.0
    miss = [c for c in cols if pd.isna(r[c])]
    L = []; P = L.append
    P(f"HYDRA  {tdd} ({tdd:%a})  contract {k}  as of {last:%H:%M} ET  ref {r.ref:.2f}")
    if abs((datetime.combine(tdd, use_cut) - datetime.combine(tdd, cutoff)).total_seconds()) > 600:
        P(f"  ! run time differs from model cutoff {m['cutoff']} by >10 min - refit with: backtest --cutoff {use_cut:%H:%M}")
    log = dict(date=str(tdd), run=f'{last:%H:%M}', contract=k, ref=round(r.ref, 2))
    H1 = m['H1_range']
    if miss:
        P(f"  H1 RANGE: cannot forecast - missing {miss} (need the prior 3 RTH sessions of {k} and prior close)")
    else:
        x = np.array([1.0] + [float(r[c]) for c in cols]); fc = float(x @ np.array(m['coef'])); sd = m['sd']
        F = math.exp(fc); Fp = F / 100 * r.ref; z = stats.norm.ppf(0.9)
        q1, q2 = m['tercile_F_pct']; q = 'Low' if F < q1 else ('Mid' if F < q2 else 'High')
        p10, p90 = math.exp(fc - z * sd) / 100 * r.ref, math.exp(fc + z * sd) / 100 * r.ref
        P(f"\n  H1 RANGE  forecast {F:.2f}% = {Fp:.0f} pts  (P10 {p10:.0f} / P90 {p90:.0f})  tercile {q}")
        P(f"     validated OOS: R2 {H1['r2']} vs AR(3) {H1['r2_ar3']} (DM p {H1['dm_vs_ar3_p']}); realised/forecast median {H1['ratio_median']}")
        P(f"     bands from 09:30 open (provisional anchor {r.ref:.2f}):   k    pts    up       down     hist any / both ({q} days)")
        for kk in KS:
            b = H1['bands'][str(kk)][q]; d = kk * Fp
            P(f"                                                   {kk:4.2f} {d:6.0f}  {tick(r.ref + d):9.2f} {tick(r.ref - d):9.2f}   {b['any']:5.1f} / {b['both']:4.1f}")
        P(f"     re-anchor at the open: level = open +/- k x {Fp:.0f}")
        H2 = m['H2_daytype'][q]
        P(f"\n  H2 DAY TYPE  {q}-forecast days: trend {H2['trend_rate']}% CI {H2['ci']}, two-sided {H2['two_sided_0.5F']}%   (tercile effect p {m['H2_daytype']['chi2_p']})")
        log.update(F_pct=round(F, 3), F_pts=round(Fp, 1), P10=round(p10, 1), P90=round(p90, 1), tercile=q)
        drivers = {c: round(float(x[i + 1] * m['coef'][i + 1]), 3) for i, c in enumerate(cols) if x[i + 1] != 0}
        P(f"     contributions (log pts): " + '  '.join(f'{c} {v:+.3f}' for c, v in drivers.items()))
    H3 = m['H3_post_touch']
    P(f"\n  H3 AFTER FIRST 0.5F TOUCH  closes same side {H3['closes_same_side']['real']}% (random-walk null {H3['closes_same_side']['null']}%, p {H3['closes_same_side']['p']}); "
      f"back through open {H3['back_through_open']['real']}% (null {H3['back_through_open']['null']}%, p {H3['back_through_open']['p']}); "
      f"reaches 1.0F {H3['extends_to_1.0F']['real']}% (null {H3['extends_to_1.0F']['null']}%)")
    H5 = m['H5_direction']
    P(f"\n  H5 DIRECTION  {'validated' if H5['validated'] else 'no validated edge'}: OOS hit {H5['hit']}% vs always-long {H5['always_long_hit']}% (p {H5['p_vs_always_long']})")
    # H4 calendar
    H4 = m['H4_calendar']; fl = []
    wd = ['mon', 'tue', 'wed', 'thu'][tdd.weekday()] if tdd.weekday() < 4 else None
    if wd: fl.append(f"{wd} {H4['z_' + wd]['pct_effect']:+.0f}% (t {H4['z_' + wd]['t']})")
    for t, ds in ev.items():
        if pd.Timestamp(tdd) in ds:
            h = H4.get('z_' + t); fl.append(f"{t.upper()} today" + (f" {h['pct_effect']:+.0f}% (t {h['t']})" if h else ' (flag only, not in model)'))
    if r.get('z_nfp', 0) == 1: fl.append(f"NFP (first-Friday rule) {H4['z_nfp']['pct_effect']:+.0f}% (t {H4['z_nfp']['t']})")
    up = []
    for t, ds in ev.items():
        for d in sorted(ds):
            if 0 < (d.date() - tdd).days <= 7: up.append(f"{t.upper()} {d:%a %d %b}")
    P(f"\n  H4 CALENDAR  " + ('; '.join(fl) if fl else 'no event today') + (f"   next 7d: {', '.join(up)}" if up else ''))
    # H6 carry
    f, n, _ = cycle(tdd); ef, en = expiry(f), expiry(n); rd = roll_date(f)
    P(f"\n  H6 CARRY  expiring {f} (exp {ef:%a %d %b}, roll date {rd:%a %d %b}, {(ef - tdd).days}d)  next {n} (exp {en:%d %b %Y})")
    if tdd == ef: P(f"     !! EXPIRY DAY: {f} settles at the 09:30 open (SOQ); no RTH in {f} - trade {n}")
    elif rd <= tdd < ef: P(f"     ROLL WINDOW: volume normally in {n}; continuous data switch the Sunday after expiry")
    both = df[df.k.isin([f, n])].groupby('dt').k.nunique(); common = both[both == 2].index
    if len(common):
        tc = common.max(); px = df[df.dt == tc].set_index('k').c
        pf, pn = a.front_price or float(px[f]), a.next_price or float(px[n])
        if not (a.front_price or a.next_price):
            P(f"     prices at last common minute {tc:%d %b %H:%M} ET" + ('  !! STALE (>60 min before last bar)' if (last - tc).total_seconds() > 3600 else ''))
    else: pf, pn = a.front_price, a.next_price
    if pf and pn:
        dT = (en - ef).days; spread = pn - pf; ic = math.log(pn / pf) * 365 / dT * 100
        P(f"     {f} {pf:.2f}   {n} {pn:.2f}   spread {spread:+.2f} pts (${spread * PV:,.0f}/contract)   implied carry {ic:.2f}%/yr over {dT}d")
        log.update(front=pf, next=pn, spread=round(spread, 2), implied_carry=round(ic, 3))
        if a.sofr is not None:
            rq = (a.sofr - a.div) / 100; fair = pf * (math.exp(rq * dT / 365) - 1)
            P(f"     fair spread at SOFR {a.sofr}% - div {a.div}% = {fair:+.2f} pts  -> {'rich' if spread > fair else 'cheap'} by {spread - fair:+.2f} pts (${(spread - fair) * PV:,.0f})")
            P(f"     front basis decay ~ {pf * rq / 365:.2f} pts/day; to expiry ~ {pf * rq * max((ef - tdd).days, 0) / 365:.0f} pts")
            log.update(fair_spread=round(fair, 2), rich=round(spread - fair, 2))
        else: P(f"     add --sofr and --div for fair value; implied decay ~ {pf * ic / 100 / 365:.2f} pts/day")
        vf, vn = prev_vol(S, td, f), prev_vol(S, td, n)
        if vf is not None and vn is not None and vf + vn > 0:
            P(f"     prior-session volume share {n}: {100 * vn / (vf + vn):.0f}%"); log['next_vol_share'] = round(100 * vn / (vf + vn), 1)
    else:
        P(f"     need prices for both {f} and {n}: include both contracts' files or pass --front-price/--next-price")
    H6 = m['H6_carry']
    P(f"     backtest: roll window range x{H6['range_ratio_roll_vs_other']} (p {H6['range_p']}) - no intraday carry effect; dCarry->next-week range: {H6.get('dcarry_vs_next_week_range', 'n/a')}")
    txt = '\n'.join(L); print(txt)
    if a.out: open(a.out, 'w').write(txt + '\n')
    lp = a.log; old = pd.read_csv(lp) if os.path.exists(lp) else pd.DataFrame()
    old = old[~((old.get('date') == log['date']) & (old.get('contract') == k))] if len(old) else old
    pd.concat([old, pd.DataFrame([log])]).to_csv(lp, index=False); print(f'\nlogged -> {lp}')

def tick(x): return round(x * 4) / 4
def last_price(df, k):
    s = df[df.k == k]; return float(s.c.iloc[-1]) if len(s) else None
def prev_vol(S, td, k):
    s = S[(S.k == k) & (S.td < td)].sort_values('td'); return float(s.vol.iloc[-1]) if len(s) else None

# ---------------------------------------------------------------- score
def score(a):
    if not os.path.exists(a.log): sys.exit('no log yet')
    m = json.load(open(a.model)); df = load(a.data, m['tz_shift']); Lg = pd.read_csv(a.log)
    rth = df[(df.t >= RTH0) & (df.t <= RTH1)]
    for i, r in Lg.iterrows():
        if pd.isna(r.get('F_pts')): continue
        b = rth[(rth.td == pd.Timestamp(r.date)) & (rth.k == r.contract)]
        if len(b) < MIN_RTH: continue
        o, h, l, c = b.o.iloc[0], b.h.max(), b.l.min(), b.c.iloc[-1]
        Lg.loc[i, ['open', 'high', 'low', 'close', 'range']] = [o, h, l, c, h - l]
        Lg.loc[i, 'ratio'] = (h - l) / r.F_pts; Lg.loc[i, 'in_p10_p90'] = float(r.P10 <= h - l <= r.P90)
        for k in KS:
            Lg.loc[i, f'any_{k}'] = float(max(h - o, o - l) >= k * r.F_pts); Lg.loc[i, f'both_{k}'] = float(min(h - o, o - l) >= k * r.F_pts)
    Lg.to_csv(a.log, index=False); s = Lg.dropna(subset=['ratio']) if 'ratio' in Lg else Lg.iloc[:0]
    print(f'forward record: {len(s)} scored days')
    if len(s):
        H1 = m['H1_range']
        print(f"  realised/forecast median {s.ratio.median():.3f} (backtest {H1['ratio_median']});  P10-P90 cover {100 * s.in_p10_p90.mean():.0f}% (backtest {H1['cover_p10_p90']})")
        for k in KS: print(f"  k={k}: any {100 * s[f'any_{k}'].mean():5.1f}% (bt {H1['bands'][str(k)]['any']})  both {100 * s[f'both_{k}'].mean():5.1f}% (bt {H1['bands'][str(k)]['both']})")

# ---------------------------------------------------------------- cli
if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('mode', choices=['backtest', 'premarket', 'score'])
    ap.add_argument('--data', nargs='+', required=True, help='CSV paths or globs')
    ap.add_argument('--model', default='hydra_model.json'); ap.add_argument('--log', default='hydra_log.csv')
    ap.add_argument('--events', default='events.csv'); ap.add_argument('--tz-shift', type=float, default=1.0)
    ap.add_argument('--cutoff', default='09:25', help='backtest: ET time the pre-market features are frozen')
    ap.add_argument('--oos-start', default='2024-01'); ap.add_argument('--shuffles', type=int, default=200)
    ap.add_argument('--carry-hist', help='optional CSV date,front,next settlements')
    ap.add_argument('--contract', help='override traded contract, e.g. NQZ26')
    ap.add_argument('--front-price', type=float); ap.add_argument('--next-price', type=float)
    ap.add_argument('--sofr', type=float, help='SOFR %% for fair carry'); ap.add_argument('--div', type=float, default=0.7, help='NDX dividend yield %%')
    ap.add_argument('--asof', help='premarket: replay as of this ET time, e.g. "2026-06-12 09:20"')
    ap.add_argument('--out', help='also write the premarket report to this file')
    a = ap.parse_args()
    {'backtest': backtest, 'premarket': premarket, 'score': score}[a.mode](a)
