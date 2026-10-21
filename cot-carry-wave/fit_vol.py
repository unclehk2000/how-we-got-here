import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
import statsmodels.api as sm
from model import FEAT, predict, predict_cache, evaluate
X=pd.read_pickle('design.pkl')
D=X.dropna(subset=['y']).copy()
Z=D[FEAT].fillna(D[FEAT].median()); Zs=(Z-Z.mean())/Z.std()
# 1. In-sample OLS, HAC t
o=sm.OLS(D.y,sm.add_constant(Zs)).fit(cov_type='HAC',cov_kwds={'maxlags':4})
print('IN-SAMPLE OLS on r_spot (%%/wk), n=%d  R2=%.3f adjR2=%.3f  F-test p=%.3f'%(o.nobs,o.rsquared,o.rsquared_adj,o.f_pvalue))
print(pd.DataFrame({'beta_per_sd':o.params,'HAC_t':o.tvalues}).round(3).to_string())
# 2. Weekly Markov-switching regression (switching intercept + variance, exog COT/price betas switching)
ex=Zs[['am_d1','lev_d1','am_z52','r1','rv4']]
best=None
for rep in range(3):
    try:
        r=sm.tsa.MarkovRegression(D.y,k_regimes=2,exog=ex,switching_variance=True).fit(search_reps=30,disp=False)
        if best is None or r.llf>best.llf: best=r
    except Exception as e: print(e)
lin=sm.OLS(D.y,sm.add_constant(ex)).fit()
print('\nWEEKLY MARKOV-SWITCHING REGRESSION: llf %.1f vs linear %.1f, LR=%.1f on %d extra params'%(best.llf,lin.llf,2*(best.llf-lin.llf),len(best.params)-len(lin.params)-1))
print(best.params.round(3).to_string())
# 3. Volatility target
for m in ['vdrift','vols','vmark']:
    pass
def vpred(kind):
    out=pd.Series(np.nan,index=X.index)
    for t in X.index[X.index.start_time>=pd.Timestamp('2024-01-01')]:
        tr=X[(X.index<t)&X.rv.notna()&X.rv4.notna()]
        if len(tr)<52 or pd.isna(X.rv[t]): continue
        if kind=='vdrift': out[t]=tr.rv.mean(); continue
        cols=['rv4','p_hv'] if kind=='vmark' else ['rv4']
        cols=cols+['am_z52','lev_z52'] if kind=='vmark' else cols
        Zt=tr[cols].fillna(tr[cols].median()); m=sm.OLS(np.log(tr.rv),sm.add_constant(Zt)).fit()
        xt=X.loc[[t],cols].fillna(tr[cols].median())
        out[t]=np.exp(m.predict(sm.add_constant(xt,has_constant="add")).iloc[0]+m.mse_resid/2)
    return out
for k in ['vdrift','vols','vmark']: predict_cache[k]=vpred(k)
print('\nNEXT-WEEK REALISED VOL (sqrt of summed daily r^2), OOS 2024-26')
for k,lab in [('vols','past 4w vol only'),('vmark','past vol + Markov P(high-vol) + COT z')]:
    print(lab,evaluate(X,predict_cache[k],lab,target='rv'))
# 4. Use the regime layer the way a carry market allows: stay long, size by forecast vol
s=predict_cache['vmark']; m=s.notna()&X.y_fut.notna()
w=(s[m].median()/s[m]).clip(0,2); yf=X.y_fut[m]
sh=lambda r: r.mean()/r.std()*np.sqrt(52)
mdd=lambda r: ((1+r/100).cumprod()/(1+r/100).cumprod().cummax()-1).min()*100
print('\nAlways long: ret %.1f%% sharpe %.2f maxDD %.1f%% | Markov vol-sized long: ret %.1f%% sharpe %.2f maxDD %.1f%% avg size %.2f'%(
      yf.sum(),sh(yf),mdd(yf),(w*yf).sum(),sh(w*yf),mdd(w*yf),w.mean()))
flat=(X.p_hv[m]>0.8)
print('Long except when P(high-vol)>0.8 at Friday close: ret %.1f%% sharpe %.2f maxDD %.1f%% weeks flat %d'%(
      (yf*(~flat)).sum(),sh(yf*(~flat)),mdd(yf*(~flat)),flat.sum()))
# 5. carry sensitivity
import model as M
X2=X.copy(); X2['bleed']=X.bleed*4.0/X.carry_pct; X2['carry_pct']=4.0; X2['y']=X2.y_fut+X2.bleed
pe=predict(X2,'enet'); pd_=predict(X2,'drift'); M.predict_cache['drift']=pd_
print('\nCarry fixed at 4%%: enet', evaluate(X2,pe,'enet'))
