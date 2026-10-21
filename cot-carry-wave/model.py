"""Carry-aware weekly NQ regression with COT and a Markov regime layer.
Target:  r_spot(t) = r_fut(t) + c(t)*dt(t)            (carry-adjusted weekly return, %)
Model:   r_spot(t) = sum_s P(s_t | info_{t-1}) * (a_s + b_s' X_{t-1}) + e_t
Futures forecast = forecast of r_spot - c(t)*dt(t).   Benchmark = always-long futures (the carry-charge market)."""
import pandas as pd, numpy as np, warnings
from sklearn.linear_model import ElasticNetCV, LinearRegression, Ridge
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings('ignore')
FEAT=['p_hv','am','am_d1','lev','lev_d1','am_z52','lev_z52','oi_chg','carry_pct','roll_wk','r1','r4','rv4']

def design():
    w=pd.read_pickle('weekly.pkl'); f=pd.read_pickle('cotf.pkl'); d=pd.read_pickle('daily_regime.pkl')
    reg=d.groupby(d.index.to_period('W-FRI')).p_hv.last().reindex(w.index)
    X=pd.DataFrame(index=w.index)
    X['y']=100*w.r_spot; X['y_fut']=100*w.r_fut; X['bleed']=100*w.bleed
    X['p_hv']=reg.shift()                                     # regime as of last Friday close
    cf=f.reindex(f.index.union(w.index)).ffill().reindex(w.index)   # latest released report
    for c in ['am','am_d1','lev','lev_d1','am_z52','lev_z52','oi_chg']: X[c]=cf[c]
    X['carry_pct']=100*w.carry; X['roll_wk']=w.roll_wk
    X['r1']=100*w.r_fut.shift(); X['r4']=100*w.r_fut.shift().rolling(4,min_periods=3).sum()
    X['rv4']=100*np.sqrt((w.rv**2).shift().rolling(4,min_periods=3).mean())
    X['absy']=100*w.r_fut.abs(); X['rv']=100*w.rv
    return X

def _prep(tr,te,cols):
    med=tr[cols].median(); sc=StandardScaler().fit(tr[cols].fillna(med))
    return sc.transform(tr[cols].fillna(med)),sc.transform(te[cols].fillna(med)),sc

def predict(X,model,cols=FEAT,start='2024-01-01',min_train=52,target='y'):
    """expanding window, refit every week; returns OOS forecast of target"""
    out=pd.Series(np.nan,index=X.index)
    ok=X[target].notna()
    for t in X.index[X.index.start_time>=pd.Timestamp(start)]:
        if not ok[t]: continue
        tr=X[(X.index<t)&ok]
        if len(tr)<min_train: continue
        te=X.loc[[t]]
        if model=='drift': out[t]=tr[target].mean(); continue
        a,b,_=_prep(tr,te,cols)
        if model=='ols': out[t]=LinearRegression().fit(a,tr[target]).predict(b)[0]
        elif model=='enet':
            m=ElasticNetCV(l1_ratio=[.1,.5,.9,1],cv=TimeSeriesSplit(4),alphas=30,max_iter=5000).fit(a,tr[target])
            out[t]=m.predict(b)[0]
        elif model=='markov':
            # regime-weighted ridge: one regression per regime, weights = regime probabilities
            ph=tr.p_hv.fillna(tr.p_hv.mean()).clip(0.01,0.99).values
            pn=float(np.clip(te.p_hv.fillna(tr.p_hv.mean()).iloc[0],0.01,0.99))
            cols2=[c for c in cols if c!='p_hv']; a2,b2,_=_prep(tr,te,cols2)
            mh=Ridge(alpha=10).fit(a2,tr[target],sample_weight=ph); mc=Ridge(alpha=10).fit(a2,tr[target],sample_weight=1-ph)
            out[t]=pn*mh.predict(b2)[0]+(1-pn)*mc.predict(b2)[0]
    return out

def evaluate(X,p,name,target='y'):
    m=p.notna()&X[target].notna()
    y=X[target][m]; f=p[m]; drift=predict_cache['drift'][m] if target=='y' else predict_cache['vdrift'][m]
    r2=1-((y-f)**2).sum()/((y-drift)**2).sum()
    # Clark-West (nested vs drift)
    cw=(y-drift)**2-((y-f)**2-(drift-f)**2); t_cw=cw.mean()/(cw.std(ddof=1)/np.sqrt(len(cw)))
    res=dict(model=name,n=int(m.sum()),oos_r2_vs_drift=round(100*r2,2),clark_west_t=round(t_cw,2))
    if target=='y':
        ff=f-X.bleed[m]; yf=X.y_fut[m]                     # futures forecast vs futures outcome
        pos=np.sign(ff); hit=(np.sign(yf)==pos).mean()
        lf=(ff>0).astype(float)
        sh=lambda r: r.mean()/r.std()*np.sqrt(52)
        res.update(hit=round(100*hit,1),always_long_hit=round(100*(yf>0).mean(),1),
                   ls_ret=round((pos*yf).sum(),1),lf_ret=round((lf*yf).sum(),1),long_ret=round(yf.sum(),1),
                   ls_sharpe=round(sh(pos*yf),2),lf_sharpe=round(sh(lf*yf),2),long_sharpe=round(sh(yf),2),weeks_long=int((ff>0).sum()))
    return res
predict_cache={}
if __name__=='__main__':
    X=design(); X.to_pickle('design.pkl')
    print('weeks with target',X.y.notna().sum(),'| OOS from 2024-01')
    for mdl in ['drift','ols','enet','markov']:
        predict_cache[mdl]=predict(X,mdl)
    rows=[evaluate(X,predict_cache[m],m) for m in ['drift','ols','enet','markov']]
    pd.set_option('display.width',250); print(pd.DataFrame(rows).to_string(index=False))
    pd.DataFrame(predict_cache).to_pickle('preds_dir.pkl')
