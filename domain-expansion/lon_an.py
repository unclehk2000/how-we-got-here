import json, numpy as np, pandas as pd
import statsmodels.api as sm
R = pd.read_pickle('lon_rows.pkl'); C = pd.read_pickle('lon_ck.pkl')
R = R[(R.rD > 0) & (R.atr > 0) & (R.lr > 0)].copy()
R['tr'] = R.tday < '2025'
out = {}
# (a) expected London range
for name, cols in (('rD+atr', ['lrD', 'latr']), ('atr', ['latr']), ('rD', ['lrD'])):
    R['lrD'], R['latr'], R['llr'] = np.log(R.rD), np.log(R.atr), np.log(R.lr)
    tr, te = R[R.tr], R[~R.tr]
    m = sm.OLS(tr.llr, sm.add_constant(tr[cols])).fit()
    res = tr.llr - m.predict(sm.add_constant(tr[cols]))
    q25, q50, q75 = np.quantile(res, [0.25, 0.5, 0.75])
    pe = m.predict(sm.add_constant(te[cols]))
    rte = te.llr - pe
    cov = ((rte >= q25) & (rte <= q75)).mean()
    r2 = 1 - ((te.llr - pe - q50) ** 2).sum() / ((te.llr - te.llr.mean()) ** 2).sum()
    bys = {s: (((te[te.sym == s].llr - pe[te.sym == s]) >= q25) & ((te[te.sym == s].llr - pe[te.sym == s]) <= q75)).mean() for s in ('NQ', 'ES', 'RTY')}
    print(f'{name:7s} coef {dict(m.params.round(3))} | train R2 {m.rsquared:.3f} | test R2 {r2:.3f} | test median ratio {np.exp(np.median(rte) - q50):.3f} | middle-half coverage {cov:.2f} by sym ' + ' '.join(f'{k} {v:.2f}' for k, v in bys.items()) + f' | band x{np.exp(q25 - q50):.2f}–x{np.exp(q75 - q50):.2f}')
    out['exp_' + name] = dict(params=m.params.to_dict(), q25=q25, q50=q50, q75=q75, test_r2=r2, cov=cov)
# (e) tier odds: 2 SD at the London extreme
R['coiled'] = R.coil <= 0.20
R['cbw'] = R.cbR >= 5.0
R['tier'] = np.where(R.coiled & R.cbw, 3, np.where(R.coiled, 2, np.where(R.cbw, 1, 0)))
R['x2'] = (R.mx >= 2.0).astype(float)
print('\n2 SD at the London extreme by tier (pooled, 2018–24 / 2025–26, NQ ES RTY):')
for t in (3, 2, 1, 0):
    s = R[R.tier == t]
    print(f'  tier {t}: {s.x2.mean():.2f} n {len(s)} | halves {s[s.tr].x2.mean():.2f} / {s[~s.tr].x2.mean():.2f} | ' + ' '.join(f'{k} {s[s.sym == k].x2.mean():.2f}' for k in ('NQ', 'ES', 'RTY')))
out['tier'] = {int(t): dict(p=R[R.tier == t].x2.mean(), n=int((R.tier == t).sum()), h1=R[(R.tier == t) & R.tr].x2.mean(), h2=R[(R.tier == t) & ~R.tr].x2.mean()) for t in (3, 2, 1, 0)}
print('  all', R.x2.mean().round(3))
# (d) NY carry
for col in ('ny_hi', 'ny_lo', 't11_hi', 't11_lo'):
    s = R.dropna(subset=[col])
    print(f'{col}: {s[col].mean():.2f} | halves {s[s.tr][col].mean():.2f} / {s[~s.tr][col].mean():.2f} | ' + ' '.join(f'{k} {s[s.sym == k][col].mean():.2f}' for k in ('NQ', 'ES', 'RTY')))
    out[col] = s[col].mean()
s = R.dropna(subset=['t11_hi', 't11_lo'])
print('either by 11:00', ((s.t11_hi + s.t11_lo) > 0).mean().round(3), 'both', ((s.t11_hi + s.t11_lo) > 1).mean().round(3))
# London range vs ADR
s = R.dropna(subset=['adr'])
print('London range / ADR20: median', (s.lr / s.adr).median().round(3), 'P25', (s.lr / s.adr).quantile(.25).round(3), 'P75', (s.lr / s.adr).quantile(.75).round(3))
out['lr_adr'] = dict(p25=(s.lr / s.adr).quantile(.25), p50=(s.lr / s.adr).median(), p75=(s.lr / s.adr).quantile(.75))
# time of the London high / low
for col in ('t_hi', 't_lo'):
    tt = R[col]
    print(col, 'share printed by', ' '.join(f'{h // 60:02d}:{h % 60:02d} {(tt < h).mean():.2f}' for h in (150, 180, 210, 240, 270)))
json.dump(out, open('lon_stats.json', 'w'), default=float, indent=1)
