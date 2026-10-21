"""Causal Markov regime probabilities from DAILY NQ returns.
2-state Markov-switching model: r_d = mu_s + sigma_s * e_d, P(s_d | s_{d-1}) = transition matrix.
Parameters refitted every quarter on all data to date; probabilities are FILTERED (data to that day only)."""
import pandas as pd, numpy as np, warnings
import statsmodels.api as sm
warnings.filterwarnings('ignore')
def fit(r):
    m=sm.tsa.MarkovRegression(r*100,k_regimes=2,trend='c',switching_variance=True)
    v=float((r*100).var())
    starts=[[0.97,0.10,0.1,-0.1,0.6*v,2.5*v],[0.95,0.05,0.1,0.0,0.5*v,3.0*v],[0.98,0.15,0.15,-0.2,0.7*v,2.0*v]]
    best=None
    for sp in starts:
        try: res=m.fit(start_params=sp,disp=False)
        except Exception: continue
        sd=np.sqrt([res.params['sigma2[0]'],res.params['sigma2[1]']])
        if sd.min()<0.45: continue                      # reject degenerate near-zero-variance states
        if best is None or res.llf>best.llf: best=res
    return best
def hv_index(res):
    s2=[res.params[f'sigma2[{k}]'] for k in range(2)]; return int(np.argmax(s2))
def filtered_hv(r,refit_from='2024-01-01',freq='QS'):
    r=r.dropna(); out=pd.Series(np.nan,index=r.index); fits=[]
    starts=pd.date_range(refit_from,r.index.max(),freq=freq)
    # in-sample (training) period: probabilities from a fit on the training data itself
    edges=[r.index.min()]+list(starts)+[r.index.max()+pd.Timedelta(days=1)]
    for i in range(1,len(edges)):
        lo,hi=edges[i-1],edges[i]
        train=r[r.index<max(hi if i==1 else lo, r.index.min()+pd.Timedelta(days=200))]
        res=fit(train); k=hv_index(res)
        mod=sm.tsa.MarkovRegression(r[r.index<hi]*100,k_regimes=2,trend='c',switching_variance=True)
        fr=mod.filter(res.params)
        p=fr.filtered_marginal_probabilities[k] if hasattr(fr.filtered_marginal_probabilities,'columns') else fr.filtered_marginal_probabilities[:,k]
        p=pd.Series(np.asarray(p),index=r[r.index<hi].index)
        m=(r.index>=lo)&(r.index<hi); out[m]=p[m[r.index<hi] if False else p.index>=lo].values
        P=res.params
        fits.append(dict(fit_to=train.index.max().date(),mu_calm=P[f'const[{1-k}]'],mu_hv=P[f'const[{k}]'],
                         sd_calm=np.sqrt(P[f'sigma2[{1-k}]']),sd_hv=np.sqrt(P[f'sigma2[{k}]']),
                         p_stay_calm=(P['p[0->0]'] if k==1 else 1-P['p[1->0]']),
                         p_stay_hv=(1-P['p[1->0]']) if k==1 else P['p[0->0]']))
    return out,pd.DataFrame(fits)
if __name__=='__main__':
    d=pd.read_pickle('daily.pkl')
    full=fit(d.r.dropna()); print(full.summary().tables[1]); print(full.params.round(4))
    p,F=filtered_hv(d.r); d['p_hv']=p
    print(F.round(3).to_string(index=False))
    print('share of days hv>0.5: %.2f'%(d.p_hv>0.5).mean())
    d.to_pickle('daily_regime.pkl')
