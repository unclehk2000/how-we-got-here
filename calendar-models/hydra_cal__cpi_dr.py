"""CPI-day structure for Gran Rey Cero: the 08:30–09:00 dealing range and its CE after 09:00, and NQ / ES / RTY against
their week open at 08:30 and 09:30. NQ + ES + RTY 1-minute, 2018–26. CPI days vs normal days (no CPI, NFP, FOMC, the
day after FOMC or the day after CPI). Clustered by date for pooled p-values."""
import re, json, numpy as np, pandas as pd
import statsmodels.api as sm
S = open('/home/claude/hm/Hollow.pine', encoding='utf-8').read()
def dates(name):
    blk = []
    for line in S[S.index(name + ' '):].split('\n'):
        if blk and not line.lstrip().startswith('+'):
            break
        blk.append(line)
    return set(pd.Timestamp(x) for x in re.findall(r'20\d{6}', '\n'.join(blk)))
FO, CP, NP = dates('S_FOMC'), dates('S_CPI'), dates('S_NFP')
rows = []
wk = {}
for sym in ('NQ', 'ES', 'RTY'):
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl')
    b['date'] = b.ts.dt.normalize()
    day = b.groupby('tday').agg(H=('High', 'max'), L=('Low', 'min'))
    adr = (day.H - day.L).rolling(20).mean().shift(1)
    tds = list(day.index)
    prev = {tds[i]: tds[i - 1] for i in range(1, len(tds))}
    # week open: the first bar of each CME week (Sunday 18:00 or the week's first session)
    b['wk'] = (b.ts + pd.Timedelta(hours=6)).dt.to_period('W-SAT')
    wo = b.groupby('wk').Open.first()
    b['wo'] = b.wk.map(wo)
    for td, g in b[b.date == b.tday].groupby('tday'):
        if td not in adr.index or not np.isfinite(adr.loc[td]):
            continue
        pt = prev.get(td)
        isC = td in CP
        norm = not (td in CP or td in NP or td in FO or pt in FO or pt in CP)
        if not (isC or norm):
            continue
        w = g[(g.hm >= 830) & (g.hm < 900)]
        a = g[(g.hm >= 900) & (g.hm < 1700)]
        if len(w) < 25 or len(a) < 300:
            continue
        H, L = w.High.max(), w.Low.min(); CE = (H + L) / 2; A = adr.loc[td]
        c859 = w.Close.iloc[-1]
        a14 = a[a.hm < 1615]
        def first(mask):
            ix = a.index[mask]
            return a.loc[ix[0], 'hm'] if len(ix) else np.nan
        ceHit = first((a.Low <= CE) & (a.High >= CE))
        hiBrk = first(a.High > H); loBrk = first(a.Low < L)
        rc = a14.Close.iloc[-1] if len(a14) else np.nan
        o830 = w.Open.iloc[0]
        r930 = g[g.hm == 930]
        rows.append(dict(sym=sym, tday=td, cpi=isC, A=A, rng=(H - L) / A, ceD=abs(c859 - CE) / A,
                         ce14=float(ceHit < 1615) if np.isfinite(ceHit) else 0.0, ce17=float(np.isfinite(ceHit)),
                         hi14=float(hiBrk < 1615) if np.isfinite(hiBrk) else 0.0, lo14=float(loBrk < 1615) if np.isfinite(loBrk) else 0.0,
                         both14=float((np.isfinite(hiBrk) and hiBrk < 1615) and (np.isfinite(loBrk) and loBrk < 1615)),
                         rcPos=np.nan if not np.isfinite(rc) else (1 if rc > H else -1 if rc < L else 0),
                         dir9=np.sign(c859 - o830), rthDir=np.nan if not np.isfinite(rc) or not len(r930) else np.sign(rc - r930.Open.iloc[0]),
                         wo830=o830 / g.wo.iloc[0] - 1 if g.wo.iloc[0] > 0 else np.nan,
                         wo930=(r930.Open.iloc[0] / g.wo.iloc[0] - 1) if len(r930) else np.nan,
                         woClose=(rc / g.wo.iloc[0] - 1) if np.isfinite(rc) else np.nan))
D = pd.DataFrame(rows)
D.to_pickle('/home/claude/hm/hydra_cal/cpi_dr.pkl')
print(D.groupby(['cpi', 'sym']).size().unstack())


def test(col, sub=None):
    X = D if sub is None else D[sub]
    X = X.dropna(subset=[col])
    m = sm.OLS(X[col].astype(float), sm.add_constant(X.cpi.astype(float))).fit(cov_type='cluster', cov_kwds={'groups': X.tday.astype('int64')})
    c, n_ = X[X.cpi], X[~X.cpi]
    halves = [(c[c.tday < '2025'][col].mean(), n_[n_.tday < '2025'][col].mean()), (c[c.tday >= '2025'][col].mean(), n_[n_.tday >= '2025'][col].mean())]
    bys = [(c[c.sym == s][col].mean(), n_[n_.sym == s][col].mean()) for s in ('NQ', 'ES', 'RTY')]
    sgn = np.sign(c[col].mean() - n_[col].mean())
    held = m.pvalues.iloc[1] < 0.05 and all(np.sign(x - y) == sgn for x, y in halves + bys)
    print(f'{col:7s} CPI {c[col].mean():.3f} (n {len(c)}) vs normal {n_[col].mean():.3f} | p {m.pvalues.iloc[1]:.4f} | halves ' +
          ' '.join(f'{x:.2f}/{y:.2f}' for x, y in halves) + ' | NQ ES RTY ' + ' '.join(f'{x:.2f}/{y:.2f}' for x, y in bys) + (' HELD' if held else ''))
    return dict(cpi=c[col].mean(), norm=n_[col].mean(), p=m.pvalues.iloc[1], held=bool(held), halves=halves, bys=bys, n=len(c), nd=c.tday.nunique())


out = {}
for col in ('rng', 'ce14', 'ce17', 'hi14', 'lo14', 'both14'):
    out[col] = test(col)
# CE touch by distance at 08:59 (CPI days)
C = D[D.cpi]
for lo, hi in ((0, 0.1), (0.1, 0.2), (0.2, 0.4), (0.4, 9)):
    s = C[(C.ceD >= lo) & (C.ceD < hi)]
    print(f'CE dist {lo}-{hi} ADR: n {len(s)} touched by 16:14 {s.ce14.mean():.2f} by 17:00 {s.ce17.mean():.2f}')
# RTH close against the 08:30–09:00 range
print('CPI RTH close vs DR: above', (C.rcPos == 1).mean().round(2), 'inside', (C.rcPos == 0).mean().round(2), 'below', (C.rcPos == -1).mean().round(2))
N = D[~D.cpi]
print('normal RTH close vs DR: above', (N.rcPos == 1).mean().round(2), 'inside', (N.rcPos == 0).mean().round(2), 'below', (N.rcPos == -1).mean().round(2))
# the window's direction and the RTH close direction
C2 = C.dropna(subset=['rthDir'])
print('CPI: RTH closed the 08:30–09:00 way', (C2.dir9 == C2.rthDir).mean().round(3), 'n', len(C2))
# week open: split at 08:30 (one index on the other side of its week open), per date
P = D[D.cpi].pivot_table(index='tday', columns='sym', values=['wo830', 'wo930', 'woClose'])
P = P.dropna()
sg = np.sign(P['wo830'])
split = (sg.nunique(axis=1) > 1)
print('CPI days with all three:', len(P), 'split at 08:30', split.mean().round(2), 'split at 09:30', (np.sign(P['wo930']).nunique(axis=1) > 1).mean().round(2))
# does the weakest at 08:30 (vs week open) stay the weakest by the RTH close?
weak830 = P['wo830'].idxmin(axis=1); weakC = P['woClose'].idxmin(axis=1)
strong830 = P['wo830'].idxmax(axis=1); strongC = P['woClose'].idxmax(axis=1)
print('weakest at 08:30 still weakest at 16:14', (weak830 == weakC).mean().round(2), '(chance 0.33); strongest stays', (strong830 == strongC).mean().round(2))
weak930 = P['wo930'].idxmin(axis=1)
print('weakest at 09:30 still weakest at 16:14', (weak930 == weakC).mean().round(2))
# split resolution: on split days, does the odd one out join the majority by the close?
res = []
for td, r in P[split].iterrows():
    s8 = np.sign(r['wo830']); maj = np.sign(s8.sum()); odd = s8[s8 != maj].index
    sc = np.sign(r['woClose'])
    res.append(all(sc[o] == maj for o in odd))
print('split days: the odd one joined the others by 16:14', np.mean(res).round(2), 'n', len(res))
json.dump({k: v for k, v in out.items()}, open('/home/claude/hm/hydra_cal/cpi_dr.json', 'w'), default=float, indent=1)
