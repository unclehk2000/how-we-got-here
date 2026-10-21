"""Last three years only (Oct 2023 → Aug 2026, the end of the DXY futures file).
Part 1: rerun of what didn't hold (DXY 4-week / last week / DXY vol / 10Y → NQ range and direction; seasonality).
Part 2: DXY extremes and NQ moving the other way (contrarian), several honest definitions:
  T1 same day        DXY trading-day move ≥ k × its 20-day average move → NQ trading day closes the other way
  T2 rest of day     DXY move 18:00 → 10:00 ET ≥ k × its 20-day average (same window) → NQ 10:00 → close goes the other way
  T3 next day        yesterday's DXY move ≥ k × average → NQ today goes the other way to that DXY move
  T4 stretched level DXY ≥ 2 sd from its 20-day mean at yesterday's close → NQ today goes the other way to the stretch
  T5 weekly          last week's DXY change ≥ k × its 20-week average → NQ this week goes the other way
Discovery Oct 2023 → Sep 2025, confirmation Oct 2025 → Aug 2026, Benjamini–Hochberg over every variant tried.
Trading days 18:00 → 17:00 ET; DXY futures (Barchart 5-min, CT → ET), one contract per trading day (no roll jumps)."""
import pandas as pd, numpy as np, json
from scipy import stats
W0, C0, W1 = pd.Timestamp('2023-10-01'), pd.Timestamp('2025-10-01'), pd.Timestamp('2026-08-27')
def wilson(k, n, z=1.96):
    if n == 0: return np.nan, np.nan
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, h
# ── DXY futures by trading day
f = pd.read_csv('/mnt/user-data/uploads/DXY_2023_2026_5min_continuous.csv')
f['ts'] = pd.to_datetime(f.Date + ' ' + f.Time) + pd.Timedelta(hours=1); f = f.sort_values('ts')
f['tday'] = (f.ts + pd.Timedelta(hours=6)).dt.normalize(); f['m'] = f.ts.dt.hour * 60 + f.ts.dt.minute
rows = []
for td, g in f.groupby('tday'):
    if td.dayofweek >= 5: continue
    c = g.Contract.value_counts().index[0]; g = g[g.Contract == c]
    if len(g) < 150: continue
    at = lambda mm: g[g.m <= mm].Close.iloc[-1] if ((g.m <= mm) & (g.ts.dt.normalize() == td)).any() else np.nan
    gt = g[g.ts.dt.normalize() == td]
    p10 = gt[gt.m < 600].Close.iloc[-1] if (gt.m < 600).any() else np.nan
    rows.append(dict(tday=td, dO=g.Open.iloc[0], dC=g.Close.iloc[-1], d10=p10, con=c))
DX = pd.DataFrame(rows).set_index('tday')
DX['chg'] = np.log(DX.dC / DX.dO); DX['chg10'] = np.log(DX.d10 / DX.dO)
DX['avg'] = DX.chg.abs().shift(1).rolling(20).mean(); DX['avg10'] = DX.chg10.abs().shift(1).rolling(20).mean()
DX['z'] = DX.chg / DX.avg; DX['z10'] = DX.chg10 / DX.avg10
# stretch: close vs its 20-day mean in sd (known at that close)
DX['str'] = (DX.dC - DX.dC.rolling(20).mean()) / DX.dC.rolling(20).std()
# ── NQ by trading day: open 18:00, price at 10:00, close
b = pd.read_pickle('/home/claude/t3/bars_NQ_all.pkl'); b = b[b.tday >= '2023-01-01']
b['m'] = b.ts.dt.hour * 60 + b.ts.dt.minute
g = b.groupby('tday')
NQ = pd.DataFrame(dict(O=g.Open.first(), C=g.Close.last()))
NQ['p10'] = b[(b.m < 600) & (b.ts.dt.normalize() == b.tday)].groupby('tday').Close.last()
D = pd.read_pickle('/home/claude/hm/days_NQ.pkl'); TD = D[D.anchor == 'TD'].set_index('tday')
NQ = NQ.join(TD[['R', 'type']], how='left')
NQ['dir'] = np.sign(NQ.C - NQ.O); NQ['dir10'] = np.sign(NQ.C - NQ.p10)
J = NQ.join(DX, how='inner'); J = J[(J.index >= W0) & (J.index <= W1)]
J['prev_z'] = DX.z.shift(1).reindex(J.index); J['prev_dir'] = np.sign(DX.chg.shift(1)).reindex(J.index); J['prev_str'] = DX.str.shift(1).reindex(J.index)
disc = J.index < C0; conf = ~disc
print(f'window {J.index.min():%d %b %Y} → {J.index.max():%d %b %Y}: {len(J)} trading days (discovery {disc.sum()}, confirmation {conf.sum()})')
TESTS = []
def test(name, sel, hit, base_sel):
    """hit: 1 if NQ went the other way, on the selected days; base: same outcome on the comparison days"""
    out = dict(name=name)
    for nm, m in (('disc', disc), ('conf', conf), ('all', disc | conf)):
        s = sel & m & hit.notna(); bsel = base_sel & m & hit.notna()
        k, n = int(hit[s].sum()), int(s.sum()); kb, nb = int(hit[bsel].sum()), int(bsel.sum())
        p, h = wilson(k, n); pb, hb = wilson(kb, nb)
        pv = stats.binomtest(k, n, 0.5, alternative='greater').pvalue if n else 1.0
        if n and nb:
            pp = (k + kb) / (n + nb); se = np.sqrt(pp * (1 - pp) * (1 / n + 1 / nb)); z = (k / n - kb / nb) / se if se > 0 else 0
            pvb = 1 - stats.norm.cdf(z)
        else: pvb = 1.0
        out[nm] = dict(k=k, n=n, p=p, moe=h, base=pb, base_moe=hb, nb=nb, p_vs50=pv, p_vsbase=pvb)
    TESTS.append(out); return out
for k in (1.0, 1.5, 2.0):
    ext = J.z.abs() >= k; opp = (J.dir == -np.sign(J.chg)).astype(float).where((J.dir != 0) & (J.chg != 0))
    test(f'T1 same day · DXY ≥ {k:.1f}× avg', ext, opp, ~ext)
    ext = J.z10.abs() >= k; opp = (J.dir10 == -np.sign(J.chg10)).astype(float).where((J.dir10 != 0) & (J.chg10 != 0))
    test(f'T2 10:00 → close · DXY by 10:00 ≥ {k:.1f}× avg', ext, opp, ~ext)
    ext = J.prev_z.abs() >= k; opp = (J.dir == -J.prev_dir).astype(float).where((J.dir != 0) & (J.prev_dir != 0))
    test(f'T3 next day · yesterday DXY ≥ {k:.1f}× avg', ext, opp, ~ext)
for k in (1.5, 2.0):
    ext = J.prev_str.abs() >= k; opp = (J.dir == -np.sign(J.prev_str)).astype(float).where(J.dir != 0)
    test(f'T4 stretched · DXY ≥ {k:.1f} sd from 20-day mean', ext, opp, ~ext)
# weekly (rebuilt DXY, Friday noon; NQ Friday close to Friday close)
dxy = pd.read_pickle('dxy_rec.pkl').dxy; wk = np.log(dxy.resample('W-FRI').last()).diff()
nqw = np.log(NQ.C.resample('W-FRI').last()).diff()
WW = pd.DataFrame(dict(dx=wk.shift(1), avg=wk.abs().shift(1).rolling(20).mean(), nq=nqw)).dropna()
WW = WW[(WW.index >= W0) & (WW.index <= W1 + pd.Timedelta(days=7))]
for k in (1.0, 1.5):
    sel = (WW.dx.abs() >= k * WW.avg); opp = (np.sign(WW.nq) == -np.sign(WW.dx)).astype(float)
    dsc = WW.index < C0
    o = dict(name=f'T5 week · last week DXY ≥ {k:.1f}× avg')
    for nm, m in (('disc', dsc), ('conf', ~dsc), ('all', dsc | ~dsc)):
        s = sel & m; kk, n = int(opp[s].sum()), int(s.sum()); kb, nb = int(opp[~sel & m].sum()), int((~sel & m).sum())
        p, h = wilson(kk, n); pb, hb = wilson(kb, nb)
        o[nm] = dict(k=kk, n=n, p=p, moe=h, base=pb, base_moe=hb, nb=nb, p_vs50=stats.binomtest(kk, n, 0.5, alternative='greater').pvalue if n else 1, p_vsbase=np.nan)
    TESTS.append(o)
# BH over the discovery p-values (vs 50%)
pv = np.array([t['disc']['p_vs50'] for t in TESTS]); m = len(pv); order = np.argsort(pv)
thr = np.zeros(m, bool); maxi = -1
for i, j in enumerate(order):
    if pv[j] <= 0.10 * (i + 1) / m: maxi = i
for i, j in enumerate(order):
    if i <= maxi: thr[j] = True
print(f'\n{m} variants tried · BH at 10% on discovery p-values\n')
print(f'{"variant":44s} {"discovery Oct23–Sep25":>30s} {"confirmation Oct25–Aug26":>30s}   {"all 3 years":>22s}  other days')
for t, ok in zip(TESTS, thr):
    d, c, a = t['disc'], t['conf'], t['all']
    held = ok and c['n'] > 0 and c['p'] > 0.5 and (np.isnan(c['p_vsbase']) or c['p'] > c['base'])
    t['bh'] = bool(ok); t['held'] = bool(held)
    print(f'{t["name"]:44s} {d["p"]*100:5.1f}% ±{d["moe"]*100:2.0f} n{d["n"]:3d} p{d["p_vs50"]:.3f} {"BH✓" if ok else "   "}  {c["p"]*100:5.1f}% ±{c["moe"]*100:2.0f} n{c["n"]:3d} p{c["p_vs50"]:.3f}   {a["p"]*100:5.1f}% ±{a["moe"]*100:2.0f} n{a["n"]:3d}  {a["base"]*100:4.1f}%  {"HELD" if held else ""}')
# ── Part 1: rerun of what didn't hold, last three years
M = pd.read_pickle('macro_NQ.pkl'); M = M[(M.index >= W0)]
dm = M.index < C0
print('\nPart 1 · last three years (Oct 2023 → Oct 2026), NQ day range ÷ ADR20 and up-close')
P1 = {}
for f_, lab in (('dx4', 'DXY 4-week change'), ('dx1', 'DXY last-week change'), ('dvol', 'DXY 20-day vol vs its year'), ('y10m', '10Y last-month change'), ('vspike', 'VIX vs 20-day mean (for scale)')):
    ok = M[[f_, 'R', 'up']].dropna()
    r_all, p_all = stats.spearmanr(ok[f_], ok.R); r_d = stats.spearmanr(ok[f_][ok.index < C0], ok.R[ok.index < C0])[0]; r_c = stats.spearmanr(ok[f_][ok.index >= C0], ok.R[ok.index >= C0])[0]
    up_r = ok[ok[f_] > 0].up.mean(); up_f = ok[ok[f_] <= 0].up.mean()
    z = stats.chi2_contingency(pd.crosstab(ok[f_] > 0, ok.up))[1]
    print(f'   {lab:34s} range Spearman {r_all:+.2f} (p {p_all:.3f}; {r_d:+.2f} then {r_c:+.2f}) · NQ up {up_r * 100:.0f}% after a rise vs {up_f * 100:.0f}% after a fall (p {z:.2f}) · n{len(ok)}')
    P1[f_] = dict(rho=r_all, p=p_all, rd=r_d, rc=r_c, up_r=up_r, up_f=up_f, p_dir=z, n=len(ok))
# seasonality inside three years: each month has three observations at most
vix = pd.read_csv('vix_daily.csv', parse_dates=['DATE']).set_index('DATE').CLOSE
y10 = pd.read_csv('bond-yields-us-10y/data/monthly.csv', parse_dates=['Date']).set_index('Date').Rate
me = lambda s: (s.resample('ME').last().pct_change() * 100)
octs = {'DXY': me(dxy), 'VIX': me(vix), 'NQ': me(NQ.C), '10Y (pp)': y10.diff()}
print('\n   Octobers 2023 · 2024 · 2025: ' + ' | '.join(f'{k} ' + ' '.join(f'{v[(v.index.month == 10) & (v.index.year == y)].iloc[0]:+.2f}' if ((v.index.month == 10) & (v.index.year == y)).any() else '—' for y in (2023, 2024, 2025)) for k, v in octs.items()))
json.dump(dict(tests=TESTS, part1=P1), open('dxy3y.json', 'w'), indent=1, default=float)
J.to_pickle('dxy3y_days.pkl')
