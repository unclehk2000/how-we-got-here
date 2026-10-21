import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
from common import *
from scipy.stats import norm
import statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg
NQ=prep('NQ'); ES=prep('ES'); A={'NQ':NQ,'ES':ES}
H30={s:pd.read_pickle(f'slots30_{s}.pkl').join(A[s][['har']+[f'sh{i}' for i in range(23)]],how='inner') for s in A}
# hourly projection median weights (pooled train) to get the live projection at each half-hour checkpoint
def xy(S,i):
    lrun=np.log(S[f'r{i}'].clip(lower=1e-4)); proj=lrun-S[f'sh{i}']; return pd.DataFrame({'c':1.0,'gap':S.har-proj}),S.lf-proj
W=[]
for i in range(23):
    X=[];Y=[]
    for S in A.values():
        T=S[S.index.year<=2024]; x,y=xy(T,i); X.append(x); Y.append(y)
    W.append(QuantReg(pd.concat(Y),pd.concat(X)).fit(q=0.5,max_iter=5000).params.values)
W=np.array(W)
def vprof(S):
    lc=np.log(S[[f'c{k}' for k in range(46)]].values); r=np.diff(np.c_[np.zeros(len(S)),lc],axis=1); return np.nanmean(r**2,axis=0)
v=np.mean([vprof(H30[s][H30[s].index.year<=2024]) for s in H30],axis=0); rem30=1-np.cumsum(v)/v.sum()
remH=rem30[1::2]                                     # end of each hour slot
def remAt(k,hourly):
    if not hourly: return rem30[k]
    j=k//2
    if k%2==1: return remH[j]
    return 1-0.5*(1-remH[0]) if j==0 else 0.5*(remH[j-1]+remH[j])
rows=[]
for s,S in H30.items():
    for k in range(44):
        j=k//2; f=1.0 if k%2==1 else 0.5
        sh=np.exp(S[f'sh{j}']) if (k%2==1 or j==0) else np.exp(S[f'sh{j-1}'])+(np.exp(S[f'sh{j}'])-np.exp(S[f'sh{j-1}']))*0.5
        lrun=np.log(S[f'r{k}'].clip(lower=1e-4)); pj=lrun-np.log(sh.clip(lower=1e-3))
        w=W[j] if (k%2==1 or j==0) else 0.5*(W[j-1]+W[j])
        prj=np.maximum(lrun,pj+w[0]+w[1]*(S.har-pj))
        p=S[f'p{k}']
        for side,pp,y in [('hi',p,S[f'hi{k}']),('lo',1-p,S[f'lo{k}'])]:
            rows.append(pd.DataFrame({'sym':s,'k':k,'y':y,'d':S[f'r{k}']*(1-pp),'har':S.har,'prj':prj,'remH':remAt(k,True),'rem30':remAt(k,False),'yr':S.index.year}))
R=pd.concat(rows); tr=R[R.yr<=2024]; te=R[R.yr>=2025].copy()
te['B']=te.k.map(tr.groupby('k').y.mean())
def P(d,kap,lev,remc): return np.clip(2*norm.cdf(d.d/(kap*np.exp(d[lev])*np.sqrt(np.maximum(d[remc],1e-6))))-1,0,1)
res={}
for lev in ['har','prj']:
    for remc in ['remH','rem30']:
        kap=min(np.arange(0.3,1.2,0.01),key=lambda kp:((tr.y-P(tr,kp,lev,remc))**2).mean())
        res[(lev,remc)]=kap; te[f'{lev}_{remc}']=P(te,kap,lev,remc)
sk=lambda d,c:100*(1-((d.y-d[c])**2).mean()/((d.y-d.B)**2).mean())
print('Random-walk extremes probability · Brier skill vs base rate by half-hour, test 2025–26')
for (lev,remc),kap in res.items():
    c=f'{lev}_{remc}'
    print(f"  sigma from {'expected (pre-open)' if lev=='har' else 'live projection    '} · variance profile {'hourly, interpolated' if remc=='remH' else 'half-hourly         '} · kappa {kap:.2f} | NQ {sk(te[te.sym=='NQ'],c):5.1f}%  ES {sk(te[te.sym=='ES'],c):5.1f}% | 09:30–16:00 NQ {sk(te[(te.sym=='NQ')&(te.k>=31)],c):5.1f}% ES {sk(te[(te.sym=='ES')&(te.k>=31)],c):5.1f}%")
for yy in range(2018,2027):
    d=R[R.yr==yy]
print('\nremaining variance share at the end of each hour slot (NQ+ES 2018–24):'); print(' '.join(f'{(18+j)%24:02d}:{x:.3f}' for j,x in enumerate(remH)))
# variance profile stability by period
for a,b in [(2018,2020),(2021,2022),(2023,2024),(2025,2026)]:
    vv=np.mean([vprof(H30[s][(H30[s].index.year>=a)&(H30[s].index.year<=b)]) for s in H30],axis=0); rr=(1-np.cumsum(vv)/vv.sum())[1::2]
    print(f'  {a}-{b}:',' '.join(f'{x:.2f}' for x in rr[[0,6,12,14,15,16,18,20,21]]),' (19:00 01:00 07:00 09:00 10:00 11:00 13:00 15:00 16:00)')
np.save('remH.npy',remH); te.to_pickle('rw_test.pkl'); pd.to_pickle(res,'rw_kappa.pkl')
