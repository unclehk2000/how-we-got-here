import json, numpy as np, pandas as pd, warnings
import statsmodels.formula.api as smf
warnings.filterwarnings('ignore')
R = pd.read_pickle('rg_rows3.pkl')
rows = []
for sym in ('NQ', 'ES', 'RTY'):
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl')[['High', 'Low', 'tday', 'hm']]
    day = b.groupby('tday').agg(H=('High', 'max'), L=('Low', 'min'))
    adr = (day.H - day.L).rolling(20).mean().shift(1)
    w = b[(b.hm >= 830) & (b.hm < 835)].groupby('tday').agg(h=('High', 'max'), l=('Low', 'min'))
    p = b[(b.hm >= 825) & (b.hm < 830)].groupby('tday').agg(h=('High', 'max'), l=('Low', 'min'))
    x = pd.DataFrame({'r830': (w.h - w.l) / adr, 'r825': (p.h - p.l) / adr}).dropna()
    x['sym'] = sym
    rows.append(x.reset_index())
X = pd.concat(rows).merge(R[['sym', 'tday', 'cpiF', 'nfpF', 'ppi', 'gdp', 'pce', 'rs', 'anyN', 'half']], on=['sym', 'tday'])
X['lr'] = np.log(X.r830 / X.r825.replace(0, np.nan))
base = X[~X.anyN]
print('normal 08:30-08:34 range / ADR median', round(base.r830.median(), 3))
for k in ('cpiF', 'nfpF', 'ppi', 'gdp', 'pce', 'rs'):
    d = X[X[k] | ~X.anyN].copy(); d['ev'] = d[k].astype(int); d['y'] = np.log(d.r830)
    m = smf.ols('y ~ ev + C(sym)', d).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(d.tday)[0]})
    e = d[d.ev == 1]
    hz = {h: round(e[e.half == h].r830.median() / base[base.half == h].r830.median(), 2) for h in ('18-24', '25-26')}
    sz = {s: round(e[e.sym == s].r830.median() / base[base.sym == s].r830.median(), 2) for s in ('NQ', 'ES', 'RTY')}
    print(k, 'n', len(e), '08:30 range x normal', round(np.exp(m.params['ev']), 2), 'p', f"{m.pvalues['ev']:.1e}", hz, sz)
