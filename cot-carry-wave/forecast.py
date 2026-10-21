"""This week's NQ carry-Markov forecast. Run after carry_data.py and markov.py.
Mean: carry-adjusted drift (expanding average) minus this week's carry bleed.
Risk: weekly sigma from the Markov high-vol probability; bands use empirical multipliers from past forecast errors."""
import pandas as pd, numpy as np, statsmodels.api as sm
from scipy.stats import norm
from carry_data import carry_path
X=pd.read_pickle('design.pkl'); d=pd.read_pickle('daily_regime.pkl')
D=X.dropna(subset=['rv','p_hv'])
v=sm.OLS(np.log(D.rv),sm.add_constant(D[['p_hv']])).fit()
a,b=v.params; s2=v.mse_resid
# one-week-ahead regime probability through the transition matrix (latest quarterly fit, full sample here)
from markov import fit, hv_index
res=fit(d.r.dropna()); k=hv_index(res); P=res.params
p_hh=(1-P['p[1->0]']) if k==1 else P['p[0->0]']; p_cc=P['p[0->0]'] if k==1 else 1-P['p[1->0]']
p_now=float(d.p_hv.iloc[-1]); p5=p_now
for _ in range(5): p5=p5*p_hh+(1-p5)*(1-p_cc)             # five trading days ahead
p_wk=np.mean([p_now]+[p5])
sig=np.exp(a+b*p_wk+s2/2)
last=d.index[-1]; nxt=last+pd.Timedelta(days=3)
c=float(carry_path(pd.DatetimeIndex([nxt])).iloc[0]); bleed=100*c*7/365
mu_spot=X.y.mean(); mu=mu_spot-bleed
# empirical band multipliers from in-sample standardised errors
e=((X.y_fut-(X.y.expanding().mean().shift()-X.bleed))/np.exp(a+b*X.p_hv+s2/2)).abs().dropna()
q68,q95=e.quantile(.68),e.quantile(.95)
px=float(d.close.iloc[-1])
print(f'NQ carry-Markov forecast for the week after {last.date()}  (last close {px:,.2f}, contract {d.ctr.iloc[-1]})')
print(f'  carry c = {100*c:.2f}%/yr  -> futures bleed this week {bleed:.3f}%')
print(f'  drift (carry-adjusted, 2023-26 mean) {mu_spot:+.3f}%  -> expected futures return {mu:+.3f}%')
print(f'  P(high-vol regime): now {p_now:.2f}, 5 days ahead {p5:.2f}   (stay probs: calm {p_cc:.3f}, high-vol {p_hh:.3f})')
print(f'  weekly sigma {sig:.2f}%   P(up week) {norm.cdf(mu/sig):.2f}')
for lab,q in [('68%',q68),('95%',q95)]:
    lo,hi=mu-q*sig,mu+q*sig
    print(f'  {lab} band: {lo:+.2f}% to {hi:+.2f}%   = {px*(1+lo/100):,.0f} – {px*(1+hi/100):,.0f}')
