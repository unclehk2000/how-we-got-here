import numpy as np, pandas as pd
import statsmodels.formula.api as smf
R = pd.read_pickle('/home/claude/rg/rg_rows2.pkl').rename(columns={'C': 'pc', 'O': 'op', 'G': 'gs'})
R['lr'] = np.log(R.ratio)
for y in ['fill_rth', 'ce_rth', 'c1_rth', 'o1_rth', 'fill_w5', 'ce_w5', 'c1_w5', 'o1_w5']:
    d = R.dropna(subset=[y]).copy(); d[y] = d[y].astype(float)
    d['did'] = d.tday.astype('int64')
    m = smf.logit(f'{y} ~ lr + I(lr**2) + news + C(sym)', d).fit(disp=0, cov_type='cluster', cov_kwds={'groups': pd.factorize(d.did)[0]})
    halves = {h: smf.logit(f'{y} ~ lr + I(lr**2) + news', d[d.half == h]).fit(disp=0).params['news[T.True]'] for h in ('18-24', '25-26')}
    syms = {s: smf.logit(f'{y} ~ lr + I(lr**2) + news', d[d.sym == s]).fit(disp=0).params['news[T.True]'] for s in ('NQ', 'ES', 'RTY')}
    print(f'{y:9s} news coef {m.params["news[T.True]"]:+.3f} p {m.pvalues["news[T.True]"]:.3f} | halves', {k: round(v, 2) for k, v in halves.items()}, 'syms', {k: round(v, 2) for k, v in syms.items()})
# CPI vs NFP separately on fill_rth
d = R.copy(); d['fill'] = d.fill_rth.astype(float)
m = smf.logit('fill ~ lr + I(lr**2) + C(regime, Treatment("normal")) + C(sym)', d).fit(disp=0, cov_type='cluster', cov_kwds={'groups': pd.factorize(d.tday)[0]})
print(m.params.filter(like='regime').round(3).to_dict(), m.pvalues.filter(like='regime').round(3).to_dict())
# size buckets: stability by half and symbol
for y in ['fill_rth', 'ce_rth', 'fill_w5', 'c1_rth', 'o1_rth']:
    print(y); print(R.groupby(['bk', 'half'], observed=True)[y].mean().unstack().mul(100).round(0).T.to_string())
    print(R.groupby(['bk', 'sym'], observed=True)[y].mean().unstack().mul(100).round(0).T.to_string())
