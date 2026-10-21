import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np, statsmodels.api as sm, json, warnings; warnings.filterwarnings('ignore')
import har2
from har2 import fit, predict, CAL
_orig=har2.design2
def design3(D):
    X=_orig(D); X['inside']=((D.h.shift(1)<=D.h.shift(2))&(D.l.shift(1)>=D.l.shift(2))).astype(int); return X
har2.design2=design3
COLS=['d1','d5','d22','dn1','up1','inside','tue','wed','thu','fri','opex_day','tom','pre_hol','post_hol']
if __name__=='__main__':
    out={}
    for s in ['NQ','ES','RTY']:
        D=pd.read_pickle(f'F_{s}.pkl')
        m,ok=fit(D,COLS,D.year>=2010)
        q=np.percentile(m.resid,[10,25,50,75,90])
        out[s]=dict(coef={k:round(float(v),4) for k,v in m.params.items()},t={k:round(float(v),2) for k,v in m.tvalues.items()},q={p:round(float(v),4) for p,v in zip([10,25,50,75,90],q)},n=int(m.nobs))
        print(s, 'n',int(m.nobs), 'inside days %', round(100*design3(D)['inside'].mean(),1))
        print(pd.DataFrame({'coef':m.params,'t':m.tvalues,'×range':np.exp(m.params)}).round(3).T.to_string())
        print('  residual quantiles', dict(zip([10,25,50,75,90],q.round(3))))
    json.dump(out,open('har_coef.json','w'),indent=1)

    # pooled fit across the three markets (used for any other symbol)
    import statsmodels.api as sm
    Ys=[];Xs=[]
    for s in ['NQ','ES','RTY']:
        D=pd.read_pickle(f'F_{s}.pkl'); X=har2.design2(D)[COLS]; y=D.lr-har2.design2(D)['L']
        ok=X.notna().all(axis=1)&y.notna()&((D.rvol>0.4)|D.rvol.isna()); Xs.append(X[ok]); Ys.append(y[ok])
    X=pd.concat(Xs); y=pd.concat(Ys)
    m=sm.OLS(y,sm.add_constant(X)).fit()
    q=np.percentile(m.resid,[10,25,50,75,90])
    out['POOLED']=dict(coef={k:round(float(v),4) for k,v in m.params.items()},q={p:round(float(v),4) for p,v in zip([10,25,50,75,90],q)},n=int(m.nobs))
    print('POOLED',{k:round(float(v),3) for k,v in m.params.items()}, q.round(3))
    json.dump(out,open('har_coef.json','w'),indent=1)
