import pandas as pd, numpy as np, statsmodels.api as sm, warnings; warnings.filterwarnings('ignore')
from model import predict
X=pd.read_pickle('design.pkl')
def vpred(cols):
    out=pd.Series(np.nan,index=X.index)
    for t in X.index[X.index.start_time>=pd.Timestamp('2024-01-01')]:
        tr=X[(X.index<t)&X.rv.notna()&X.rv4.notna()]
        if len(tr)<52 or pd.isna(X.rv[t]): continue
        Zt=tr[cols].fillna(tr[cols].median()); m=sm.OLS(np.log(tr.rv),sm.add_constant(Zt)).fit()
        xt=X.loc[[t],cols].fillna(tr[cols].median())
        out[t]=np.exp(m.predict(sm.add_constant(xt,has_constant='add')).iloc[0]+m.mse_resid/2)
    return out
dr=pd.Series(np.nan,index=X.index)
for t in X.index[X.index.start_time>=pd.Timestamp('2024-01-01')]:
    tr=X[(X.index<t)&X.rv.notna()]
    if len(tr)>=52 and pd.notna(X.rv[t]): dr[t]=tr.rv.mean()
mu=predict(X,'drift')-X.bleed
for cols in [['rv4'],['rv4','p_hv'],['rv4','p_hv','am_z52','lev_z52'],['p_hv']]:
    s=vpred(cols); m=s.notna()
    r2=1-((X.rv[m]-s[m])**2).sum()/((X.rv[m]-dr[m])**2).sum()
    e=(X.y_fut[m]-mu[m]).abs()
    print(cols,'OOS R2 %.1f%%'%(100*r2),'| within ±1σ %.0f%%  ±2σ %.0f%%'%(100*(e<=s[m]).mean(),100*(e<=2*s[m]).mean()),
          '| corr(σ̂,|r|) %.2f'%np.corrcoef(s[m],X.y_fut[m].abs())[0,1])
s=vpred(['rv4','p_hv']); s.to_pickle('vol_pred.pkl'); mu.to_pickle('mu_pred.pkl')
from scipy.stats import norm
m=s.notna()
pu=norm.cdf(mu[m]/s[m]); print('P(up) model range %.2f–%.2f, mean %.2f; realised up-rate %.2f'%(pu.min(),pu.max(),pu.mean(),(X.y_fut[m]>0).mean()))
# reliability of P(up) in two bins
b=pd.qcut(pu,2,labels=['lower','higher']); print(pd.DataFrame({'b':b,'up':(X.y_fut[m]>0).values}).groupby('b').up.agg(['count','mean']).round(3))
