"""CPI dealing range ±0.25 extensions for Gran Rey Cero: after 09:00, how often RTH (to 16:14) trades beyond the
08:30–09:00 high + 0.25 × range and below the low − 0.25 × range. NQ + ES + RTY 1-minute 2018–26, CPI days vs normal
days (no CPI, NFP, FOMC, day after FOMC or CPI). Pooled p clustered by date; the ✓ rule: p < 0.05, same side in
2018–24 and 2025–26, same side on NQ, ES and RTY."""
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
for sym in ('NQ', 'ES', 'RTY'):
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl')
    b['date'] = b.ts.dt.normalize()
    tds = sorted(b.tday.unique())
    prev = {tds[i]: tds[i - 1] for i in range(1, len(tds))}
    for td, g in b[b.date == b.tday].groupby('tday'):
        pt = prev.get(td)
        isC = td in CP
        norm = not (td in CP or td in NP or td in FO or pt in FO or pt in CP)
        if not (isC or norm):
            continue
        w = g[(g.hm >= 830) & (g.hm < 900)]
        a = g[(g.hm >= 900) & (g.hm < 1615)]
        if len(w) < 25 or len(a) < 300:
            continue
        H, L = w.High.max(), w.Low.min(); R = H - L
        if R <= 0:
            continue
        up = float(a.High.max() >= H + 0.25 * R); dn = float(a.Low.min() <= L - 0.25 * R)
        up0 = float(a.High.max() > H); dn0 = float(a.Low.min() < L)
        # given the side broke, did it reach the 0.25 extension
        rows.append(dict(sym=sym, tday=td, cpi=isC, up25=up, dn25=dn, any25=max(up, dn), both25=up * dn,
                         up_given=up if up0 else np.nan, dn_given=dn if dn0 else np.nan))
D = pd.DataFrame(rows)
def test(col):
    X = D.dropna(subset=[col])
    m = sm.OLS(X[col], sm.add_constant(X.cpi.astype(float))).fit(cov_type='cluster', cov_kwds={'groups': X.tday.astype('int64')})
    c, n_ = X[X.cpi], X[~X.cpi]
    hv = [(c[c.tday < '2025'][col].mean(), n_[n_.tday < '2025'][col].mean()), (c[c.tday >= '2025'][col].mean(), n_[n_.tday >= '2025'][col].mean())]
    bs = [(c[c.sym == s][col].mean(), n_[n_.sym == s][col].mean()) for s in ('NQ', 'ES', 'RTY')]
    sg = np.sign(c[col].mean() - n_[col].mean())
    held = m.pvalues.iloc[1] < 0.05 and all(np.sign(x - y) == sg for x, y in hv + bs)
    print(f'{col:9s} CPI {c[col].mean():.2f} (n {len(c)}, {c.tday.nunique()} days) vs normal {n_[col].mean():.2f} | p {m.pvalues.iloc[1]:.4f} | halves ' +
          ' '.join(f'{x:.2f}/{y:.2f}' for x, y in hv) + ' | NQ ES RTY ' + ' '.join(f'{x:.2f}/{y:.2f}' for x, y in bs) + (' HELD' if held else ''))
    return dict(cpi=c[col].mean(), norm=n_[col].mean(), p=m.pvalues.iloc[1], held=bool(held), halves=hv, bys=bs, n=len(c), nd=int(c.tday.nunique()))
out = {k: test(k) for k in ('up25', 'dn25', 'any25', 'both25', 'up_given', 'dn_given')}
json.dump(out, open('/home/claude/hm/hydra_cal/cpi_dr_ext.json', 'w'), default=float, indent=1)
