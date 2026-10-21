import json, numpy as np, pandas as pd, warnings
import statsmodels.formula.api as smf
warnings.filterwarnings('ignore')
R = pd.read_pickle('rg_rows2.pkl').rename(columns={'C': 'pc', 'O': 'op', 'G': 'gs'})
N2 = json.load(open('news_dates2.json'))
for k in ('ppi', 'gdp', 'pce', 'rs'):
    S = set(pd.to_datetime(N2[k]))
    R[k] = R.tday.isin(S)
R['cpiF'], R['nfpF'] = R.cpi, R.nfp
R['anyN'] = R[['cpiF', 'nfpF', 'ppi', 'gdp', 'pce', 'rs']].any(axis=1)
R['lr'] = np.log(R.ratio)
R['big'] = R.ratio >= 1.5
base = R[~R.anyN]
print('normal n', len(base), 'median ratio', round(base.ratio.median(), 2), 'big', round(100 * base.big.mean()), 'fill', round(100 * base.fill_rth.mean()), 'ce', round(100 * base.ce_rth.mean()))
rows = []
for k in ('cpiF', 'nfpF', 'ppi', 'gdp', 'pce', 'rs'):
    d = R[R[k] | ~R.anyN].copy()
    d['ev'] = d[k].astype(int)
    d['y'] = d.fill_rth.astype(float)
    g = pd.factorize(d.tday)[0]
    # size: is the event gap bigger? (log ratio, clustered OLS)
    ms = smf.ols('lr ~ ev + C(sym)', d).fit(cov_type='cluster', cov_kwds={'groups': g})
    # behaviour for its size: fill and CE
    mf = smf.logit('y ~ lr + I(lr**2) + ev + C(sym)', d).fit(disp=0, cov_type='cluster', cov_kwds={'groups': g})
    d['yc'] = d.ce_rth.astype(float)
    mc = smf.logit('yc ~ lr + I(lr**2) + ev + C(sym)', d).fit(disp=0, cov_type='cluster', cov_kwds={'groups': g})
    e = d[d.ev == 1]
    hz = {h: round(e[e.half == h].ratio.median() / base[base.half == h].ratio.median(), 2) for h in ('18-24', '25-26')}
    sz = {s: round(e[e.sym == s].ratio.median() / base[base.sym == s].ratio.median(), 2) for s in ('NQ', 'ES', 'RTY')}
    rows.append(dict(ev=k, n=len(e), days=e.tday.nunique(), med_ratio=round(e.ratio.median(), 2), big=round(100 * e.big.mean()),
                     size_x=round(np.exp(ms.params['ev']), 2), size_p=round(ms.pvalues['ev'], 4), halves=hz, syms=sz,
                     fill=round(100 * e.fill_rth.mean()), fill_p=round(mf.pvalues['ev'], 3), fill_coef=round(mf.params['ev'], 2),
                     ce=round(100 * e.ce_rth.mean()), ce_p=round(mc.pvalues['ev'], 3)))
pd.set_option('display.width', 250)
print(pd.DataFrame(rows).to_string())
# all six pooled
d = R.copy(); d['ev'] = d.anyN.astype(int); g = pd.factorize(d.tday)[0]
ms = smf.ols('lr ~ ev + C(sym)', d).fit(cov_type='cluster', cov_kwds={'groups': g})
d['y'] = d.fill_rth.astype(float)
mf = smf.logit('y ~ lr + I(lr**2) + ev + C(sym)', d).fit(disp=0, cov_type='cluster', cov_kwds={'groups': g})
e = d[d.ev == 1]
print('ANY news n', len(e), 'days', e.tday.nunique(), 'share of days', round(100 * e.tday.nunique() / R.tday.nunique()), 'median ratio', round(e.ratio.median(), 2), 'big', round(100 * e.big.mean()),
      'size x', round(np.exp(ms.params['ev']), 2), 'p', ms.pvalues['ev'], 'fill', round(100 * e.fill_rth.mean()), 'fill_p (size-controlled)', round(mf.pvalues['ev'], 3))
R.to_pickle('rg_rows3.pkl')
