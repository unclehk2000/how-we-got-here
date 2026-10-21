import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
from common import *
from statsmodels.regression.quantile_regression import QuantReg
# Which "days in profile" N gives the best live projection? (typical share of the day done by each hour = median of last N days)
res={}
for N in [10,20,30,45,60,90]:
    A=[prep(s,N) for s in ['NQ','ES']]
    A=[S[S.index>=pd.Timestamp('2018-06-01')] for S in A]     # same start for every N (90-day warm-up)
    out=[]
    for i in range(22):
        X=[];Y=[];XT=[];YT=[];L=[]
        for S in A:
            lrun=np.log(S[f'r{i}'].clip(lower=1e-4)); proj=lrun-S[f'sh{i}']
            x=pd.DataFrame({'c':1.0,'gap':S.har-proj}); y=S.lf-proj; tr=S.index.year<=2024
            X.append(x[tr]);Y.append(y[tr]);XT.append(x[~tr]);YT.append(y[~tr]);L.append((proj[~tr],lrun[~tr],S.lf[~tr]))
        par=QuantReg(pd.concat(Y),pd.concat(X)).fit(q=0.5,max_iter=5000).params.values
        e=np.concatenate([np.abs(lf-np.maximum(pj+xt.values@par,lr)) for xt,(pj,lr,lf) in zip(XT,L)])
        out.append(e.mean())
    res[N]=out
R=pd.DataFrame(res,index=[f'{(18+i)%24:02d}:59' for i in range(22)])
print('MAE of log final range, test 2025–26 NQ+ES, by days in profile N'); print(R.iloc[[0,3,6,9,12,14,15,16,17,18,20]].round(4).to_string()); print('mean',R.mean().round(4).to_dict())
