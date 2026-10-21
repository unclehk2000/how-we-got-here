import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
from common import *
from statsmodels.regression.quantile_regression import QuantReg
from scipy.stats import norm
Q=(0.10,0.25,0.5,0.75,0.90)
NQ=prep('NQ'); ES=prep('ES'); P=pd.concat([NQ,ES])
def xy(S,i):
    lrun=np.log(S[f'r{i}'].clip(lower=1e-4)); proj=lrun-S[f'sh{i}']
    return pd.DataFrame({'c':1.0,'gap':S.har-proj}),S.lf-proj,proj,lrun
def fitq(S,i):
    X,y,_,_=xy(S,i); out={}; fb={}
    for q in Q:
        try: par=QuantReg(y,X).fit(q=q,max_iter=5000).params.values
        except Exception: par=None
        ok=par is not None and abs((y<=X.values@par).mean()-q)<=0.03 and (par[1]>=-0.05)
        if not ok: par=np.array([np.quantile(y,q),0.0])
        out[q]=par; fb[q]=not ok
    return out,fb
def pred(S,i,par):
    X,_,proj,lrun=xy(S,i); return {q:np.maximum(proj+X.values@par[q],lrun) for q in Q}
print('Pooled NQ+ES weights, train 2018–24 → test 2025–26: share of days below each projected quantile (target 10/25/50/75/90)')
tr=P[P.index.year<=2024]; te=P[P.index.year>=2025]
cov=[]
for i in range(23):
    par,fb=fitq(tr,i); p=pred(te,i,par)
    below=[(te.lf<=p[q]+1e-12).mean()*100 for q in Q]; mae=(te.lf-p[0.5]).abs().mean()
    c50=((te.lf>=p[0.25]-1e-12)&(te.lf<=p[0.75]+1e-12)).mean()*100; c80=((te.lf>=p[0.10]-1e-12)&(te.lf<=p[0.90]+1e-12)).mean()*100
    cov.append(c50)
    print(f"{(18+i)%24:02d}:59 MAE {mae:.3f} | below " + ' '.join(f'{b:4.0f}' for b in below) + f" | P25–75 {c50:4.0f}%  P10–90 {c80:4.0f}% | fallback " + ''.join('x' if fb[q] else '.' for q in Q))
# production: all years
rows=[]
for i in range(23):
    par,fb=fitq(P,i); rows.append({**{f'w{int(q*100)}':par[q][1] for q in Q},**{f'c{int(q*100)}':par[q][0] for q in Q}})
W=pd.DataFrame(rows); W.to_pickle('proj_weights_pooled.pkl')
# random-walk extremes: kappa and variance profile on all years
H30={s:pd.read_pickle(f'slots30_{s}.pkl') for s in ['NQ','ES']}
def vprof(S):
    lc=np.log(S[[f'c{k}' for k in range(46)]].values); r=np.diff(np.c_[np.zeros(len(S)),lc],axis=1); return np.nanmean(r**2,axis=0)
v=np.mean([vprof(H30[s]) for s in H30],axis=0); remH=(1-np.cumsum(v)/v.sum())[1::2]; remH[-1]=0.0
rows=[]
for s,S in [('NQ',NQ),('ES',ES)]:
    for j in range(22):
        for side,pp,y in [('hi',S[f'p{j}'],S[f'hi{j}']),('lo',1-S[f'p{j}'],S[f'lo{j}'])]:
            rows.append(pd.DataFrame({'y':y,'d':S[f'r{j}']*(1-pp),'har':S.har,'rem':remH[j]}))
R=pd.concat(rows)
kap=min(np.arange(0.4,1.0,0.005),key=lambda kp:((R.y-np.clip(2*norm.cdf(R.d/(kp*np.exp(R.har)*np.sqrt(np.maximum(R.rem,1e-6))))-1,0,1))**2).mean())
print(f'\nproduction kappa (2018–2026) {kap:.3f}')
f=lambda a,n=3:', '.join(f'{x:.{n}f}' for x in a)
print('\n// Pine arrays (pooled NQ+ES 2018–2026)')
for q in ['10','25','50','75','90']:
    print(f'var array<float> PW{q} = array.from({f(W["w"+q])})'); print(f'var array<float> PC{q} = array.from({f(W["c"+q])})')
print(f'var array<float> VREM = array.from({f(remH)})'); print(f'KAPPA = {kap:.3f}')
