"""Month-of-year seasonality: does it persist? DXY (rebuilt daily from Fed H.10, 1999–2026), VIX (CBOE daily, 1990–2026),
US 10Y (monthly average yield, FRED GS10, 1953–2026), NQ (continuous daily, 2009–2026).
For each series: monthly change by calendar month, split into two halves, sign agreement and correlation of the 12
monthly means between halves, and a walk-forward test: predict each month's sign from the mean of all earlier years
(expanding window, at least 8 years), hit rate vs 50% and vs 'always the more common sign'. Writes seasonal.json."""
import pandas as pd, numpy as np, json
from scipy import stats
dxy = pd.read_pickle('dxy_rec.pkl').dxy
vix = pd.read_csv('vix_daily.csv', parse_dates=['DATE']).set_index('DATE').CLOSE
y10 = pd.read_csv('bond-yields-us-10y/data/monthly.csv', parse_dates=['Date']).set_index('Date').Rate
nq = pd.read_csv('/mnt/user-data/uploads/nq_es_rty_daily_task2_1/continuous/NQ_continuous.csv', parse_dates=['Date']).set_index('Date').AdjClose
def monthly(series, kind):
    if kind == 'yield': m = series.diff()                                  # change in % points of the monthly average
    else:
        e = series.resample('ME').last(); m = (e / e.shift(1) - 1) * 100       # month-end to month-end %
    m = m.dropna(); return pd.DataFrame(dict(v=m.values, y=m.index.year, mo=m.index.month), index=m.index)
OUT = {}
NAMES = dict(DXY=(dxy, 'pct'), VIX=(vix, 'pct'), US10Y=(y10, 'yield'), NQ=(nq, 'pct'))
for nm, (s, kind) in NAMES.items():
    M = monthly(s, kind); M = M[M.y <= 2026]
    yrs = sorted(M.y.unique()); half = yrs[len(yrs) // 2]
    A, B = M[M.y < half], M[M.y >= half]
    ma = A.groupby('mo').v.mean(); mb = B.groupby('mo').v.mean()
    agree = int((np.sign(ma) == np.sign(mb)).sum()); r = np.corrcoef(ma, mb)[0, 1]
    rs = stats.spearmanr(ma, mb)[0]
    full = M.groupby('mo').v.agg(['mean', 'median', 'count']); full['pos'] = M.groupby('mo').v.apply(lambda x: (x > 0).mean())
    t = M.groupby('mo').v.apply(lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x))))
    # walk-forward sign prediction
    hits = []; base = []
    for (y, mo), v in M.set_index(['y', 'mo']).v.items():
        prior = M[(M.mo == mo) & (M.y < y)]
        if len(prior) < 8 or v == 0: continue
        pred = np.sign(prior.v.mean()); hits.append(np.sign(v) == pred)
        base.append(np.sign(v) == np.sign(M[M.y < y].v.mean()))          # 'always the long-run sign of all months'
    hits = np.array(hits); base = np.array(base)
    k, n = hits.sum(), len(hits); pb = stats.binomtest(int(k), n, 0.5).pvalue
    print(f'\n{nm}: {M.index.min():%Y-%m} → {M.index.max():%Y-%m} ({len(yrs)} years) · halves split at {half}')
    print(f'   12 monthly means, first half vs second half: same sign in {agree}/12 months · correlation {r:+.2f} (Spearman {rs:+.2f})')
    print(f'   walk-forward: seasonal sign called the month right {k}/{n} = {k / n * 100:.1f}% (p vs 50% {pb:.2f}) · always-the-usual-sign {base.mean() * 100:.1f}%')
    sig = [f'{mo}:{t[mo]:+.1f}' for mo in range(1, 13) if abs(t[mo]) >= 2]
    print('   months with |t| ≥ 2 over the full sample: ' + (', '.join(sig) if sig else 'none'))
    row = full.loc[10]
    print(f'   October: mean {row["mean"]:+.2f}{"pp" if kind == "yield" else "%"} · median {row["median"]:+.2f} · up {row["pos"] * 100:.0f}% of {int(row["count"])} · t {t[10]:+.2f} · halves {ma[10]:+.2f} | {mb[10]:+.2f}')
    o = M[(M.mo == 10) & (M.y >= 2010)]
    print(f'   October 2010–{o.y.max()}: mean {o.v.mean():+.2f} · up {(o.v > 0).mean() * 100:.0f}% of {len(o)}')
    OUT[nm] = dict(span=f'{M.index.min():%Y}–{M.index.max():%Y}', years=len(yrs), agree=agree, r=r, rs=rs, wf_hit=k / n, wf_n=n, wf_p=pb, wf_base=float(base.mean()),
                   bymonth={int(mo): dict(mean=float(full.loc[mo, 'mean']), median=float(full.loc[mo, 'median']), pos=float(full.loc[mo, 'pos']), n=int(full.loc[mo, 'count']), t=float(t[mo]), h1=float(ma[mo]), h2=float(mb[mo])) for mo in range(1, 13)})
# VIX LEVEL seasonality (average VIX in the month ÷ that year's average): does the "autumn is volatile" shape persist?
v = vix.resample('ME').mean(); L = pd.DataFrame(dict(v=np.log(v / v.groupby(v.index.year).transform('mean')), y=v.index.year, mo=v.index.month)).dropna()
L = L[(L.y >= 1990) & (L.y <= 2025)]
ha = L[L.y < 2008].groupby('mo').v.mean(); hb = L[L.y >= 2008].groupby('mo').v.mean()
print(f'\nVIX level by month (÷ its year): halves 1990–2007 vs 2008–2025 correlation {np.corrcoef(ha, hb)[0, 1]:+.2f}, same sign {(np.sign(ha) == np.sign(hb)).sum()}/12')
print('   ' + ' '.join(f'{mo}:{np.exp(ha[mo]):.2f}/{np.exp(hb[mo]):.2f}' for mo in range(1, 13)))
OUT['VIXlevel'] = dict(r=float(np.corrcoef(ha, hb)[0, 1]), agree=int((np.sign(ha) == np.sign(hb)).sum()), h1={int(m): float(np.exp(ha[m])) for m in ha.index}, h2={int(m): float(np.exp(hb[m])) for m in hb.index})
# does the dollar's seasonal month sign line up with NQ's month? (contemporaneous link via the seasonal mean, walk-forward)
D = monthly(dxy, 'pct'); N = monthly(nq, 'pct'); J = D.join(N, rsuffix='_nq', how='inner')
calls = []
for (y, mo), row in J.set_index(['y', 'mo']).iterrows():
    prior = D[(D.mo == mo) & (D.y < y)]
    if len(prior) < 8: continue
    calls.append(dict(y=y, mo=mo, dxSeason=np.sign(prior.v.mean()), nq=row.v_nq, dx=row.v))
C = pd.DataFrame(calls)
up_if_dxdn = (C[C.dxSeason < 0].nq > 0).mean(); up_if_dxup = (C[C.dxSeason > 0].nq > 0).mean()
print(f'\nNQ month up when the dollar seasonal (from earlier years) said down: {up_if_dxdn * 100:.0f}% (n{(C.dxSeason < 0).sum()}) vs said up: {up_if_dxup * 100:.0f}% (n{(C.dxSeason > 0).sum()})')
same = (np.sign(J.v) != np.sign(J.v_nq)).mean()
print(f'NQ and DXY moved opposite ways in {same * 100:.0f}% of months 2009–2026 (same month, not a forecast)')
OUT['link'] = dict(up_if_dxdn=up_if_dxdn, up_if_dxup=up_if_dxup, n_dn=int((C.dxSeason < 0).sum()), n_up=int((C.dxSeason > 0).sum()), opposite_same_month=same)
json.dump(OUT, open('seasonal.json', 'w'), indent=1, default=float)
