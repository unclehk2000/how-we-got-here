import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np
from scipy import stats
import statsmodels.api as sm

def design(D):
    X=pd.DataFrame(index=D.index)
    lr=D.lr
    X['l1']=lr.shift(1)
    X['l5']=lr.shift(1).rolling(5).mean()
    X['l22']=lr.shift(1).rolling(22).mean()
    X['neg1']=np.minimum(D.ret.shift(1),0)          # yesterday's down move (leverage effect)
    X['absr1']=D.ret.shift(1).abs()
    for i,n in enumerate(['tue','wed','thu','fri']): X[n]=(D.dow==i+1).astype(int)
    for f in ['opex_day','qopex_day','roll_week','tom','pre_hol','post_hol']: X[f]=D[f]
    X['rvol1']=np.log(D.rvol.shift(1))
    return X

def fit_eval(D, cols, tr, te, label):
    X=design(D)[cols]; y=D.lr
    ok=X.notna().all(axis=1)&y.notna()&((D.rvol>0.4)|D.rvol.isna())
    Xtr=sm.add_constant(X[ok&tr]); m=sm.OLS(y[ok&tr],Xtr).fit(cov_type='HAC',cov_kwds={'maxlags':5})
    Xte=sm.add_constant(X[ok&te],has_constant='add'); p=m.predict(Xte)
    e=y[ok&te]-p
    res_tr=m.resid
    q25,q75,q10,q90=np.percentile(res_tr,[25,75,10,90])
    cov50=((e>=q25)&(e<=q75)).mean(); cov80=((e>=q10)&(e<=q90)).mean()
    r2=1-(e**2).sum()/((y[ok&te]-y[ok&te].mean())**2).sum()
    return dict(model=label,MAE=e.abs().mean(),R2=r2,cov50=cov50,cov80=cov80,n=len(e)),m,e

if __name__=="__main__":
 for s in ["NQ","ES","RTY"]:
     D=pd.read_pickle(f'F_{s}.pkl')
     D['base30']=np.log(D.rng.rolling(30).median().shift(1))
     D['atrl']=np.log(D.atr14)
     for split,(tr,te) in {'train 2010-20 / test 2021-26':(D.year<=2020,D.year>=2021),
                           'train 2018-24 / test 2025-26':((D.year>=2018)&(D.year<=2024),D.year>=2025)}.items():
         rows=[]
         # baselines: Kyōka's typical day = median of last 30 ranges (bias-corrected on train)
         for b,lab in [('base30','Kyōka: median of last 30 days'),('atrl','ATR14')]:
             ok=D[b].notna()&((D.rvol>0.4)|D.rvol.isna())
             c=(D.lr-D[b])[ok&tr].median()      # median-unbiased shift so the baseline is fair
             e=(D.lr-D[b]-c)[ok&te]
             q25,q75,q10,q90=np.percentile((D.lr-D[b]-c)[ok&tr],[25,75,10,90])
             r2=1-(e**2).sum()/((D.lr[ok&te]-D.lr[ok&te].mean())**2).sum()
             rows.append(dict(model=lab,MAE=e.abs().mean(),R2=r2,cov50=((e>=q25)&(e<=q75)).mean(),cov80=((e>=q10)&(e<=q90)).mean(),n=len(e)))
         r,m1,e1=fit_eval(D,['l1','l5','l22'],tr,te,'HAR (1,5,22-day log range)'); rows.append(r)
         r,m2,e2=fit_eval(D,['l1','l5','l22','neg1','absr1'],tr,te,'HAR + yesterday move'); rows.append(r)
         r,m3,e3=fit_eval(D,['l1','l5','l22','neg1','absr1','tue','wed','thu','fri','opex_day','qopex_day','roll_week','tom','pre_hol','post_hol'],tr,te,'HAR + move + calendar'); rows.append(r)
         cols4=['l1','l5','l22','neg1','absr1','tue','wed','thu','fri','opex_day','qopex_day','roll_week','tom','pre_hol','post_hol','rvol1']
         if s!='RTY' or True:
             r,m4,e4=fit_eval(D,cols4,tr,te,'… + relative volume'); rows.append(r)
         T=pd.DataFrame(rows).set_index('model')
         print(f'\n== {s} · {split} · forecasting today\'s log range ==')
         print(T.round(4).to_string())
         if split.startswith('train 2010'):
             print('coefficients (HAC t) of the full model:')
             print(pd.DataFrame({'coef':m4.params,'t':m4.tvalues}).round(3).T.to_string())
