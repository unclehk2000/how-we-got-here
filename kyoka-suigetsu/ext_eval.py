from common import *
import statsmodels.api as sm
from scipy.stats import norm
NQ=prep('NQ'); ES=prep('ES')
H30={s:pd.read_pickle(f'slots30_{s}.pkl') for s in ['NQ','ES']}
def stack_h(S,i):
    u=np.log(S[f'r{i}'].clip(lower=1e-4))-S.har; p=S[f'p{i}']
    return pd.concat([pd.DataFrame({'u':u,'pos':p,'y':S[f'hi{i}']}),pd.DataFrame({'u':u,'pos':1-p,'y':S[f'lo{i}']})])
A={s:S for s,S in [('NQ',NQ),('ES',ES)]}
coef=[]
for i in range(22):
    T=pd.concat([stack_h(S[S.index.year<=2024],i) for S in A.values()])
    m=sm.GLM(T.y,sm.add_constant(T[['u','pos']]),family=sm.families.Binomial()).fit(); coef.append(m.params.values)
coef=np.array(coef)   # 22 x 3 (const,u,pos)
def cAt(k):           # half-hour checkpoint k -> coefficients as Pine would use them
    j=k//2
    if k%2==1: return coef[j] if j<22 else None
    return coef[0] if j==0 else 0.5*(coef[j-1]+coef[j])
# test rows at every half-hour checkpoint 0..43
rows=[]
for s in ['NQ','ES']:
    S=H30[s].join(A[s][['har']],how='inner')
    for k in range(44):
        c=cAt(k)
        u=np.log(S[f'r{k}'].clip(lower=1e-4))-S.har; p=S[f'p{k}']
        for side,pp,y in [('hi',p,S[f'hi{k}']),('lo',1-p,S[f'lo{k}'])]:
            z=c[0]+c[1]*u+c[2]*pp
            rows.append(pd.DataFrame({'sym':s,'k':k,'side':side,'u':u,'pos':pp,'y':y,'P':1/(1+np.exp(-z)),'r':S[f'r{k}'],'har':S.har,'yr':S.index.year}))
R=pd.concat(rows)
tr=R[R.yr<=2024]; te=R[R.yr>=2025].copy()
br=tr.groupby('k').y.mean(); te['B']=te.k.map(br)
# Brownian benchmark: remaining variance share by half-hour (train), daily sigma = kappa * expected range
def vprof(S):
    lc=np.log(S[[f'c{k}' for k in range(46)]].values); r=np.diff(np.c_[np.zeros(len(S)),lc],axis=1); return np.nanmean(r**2,axis=0)
v=np.mean([vprof(H30[s][H30[s].index.year<=2024]) for s in H30],axis=0); rem=1-np.cumsum(v)/v.sum()
def bm(d,kap):
    sig=kap*np.exp(d.har)*np.sqrt(np.maximum(rem[d.k.values],1e-6)); dist=d.r*(1-d.pos)
    return np.clip(2*norm.cdf(dist/sig)-1,0,1)
best=min(np.arange(0.2,1.2,0.02),key=lambda kp:((tr.y-bm(tr,kp))**2).mean())
te['W']=bm(te,best)
print(f'Brownian benchmark: daily sigma = {best:.2f} × expected range (fitted on 2018–24)\n')
print('Test 2025–26, every half-hour checkpoint 18:29–15:59 ET (in-hour points use interpolated coefficients)')
for s in ['NQ','ES']:
    t=te[te.sym==s]
    bB=((t.y-t.B)**2).mean(); bW=((t.y-t.W)**2).mean(); bP=((t.y-t.P)**2).mean()
    ev=t[t.k%2==1]; od=t[t.k%2==0]
    sk=lambda d,c:100*(1-((d.y-d[c])**2).mean()/((d.y-d.B)**2).mean())
    print(f'  {s}: Brier base-rate {bB:.4f} · random walk {bW:.4f} ({100*(1-bW/bB):.1f}%) · model {bP:.4f} ({100*(1-bP/bB):.1f}%) | model skill at :59 {sk(ev,"P"):.1f}%, at :29 (interpolated) {sk(od,"P"):.1f}%')
    for lab,(a,b) in {'18:00–09:29':(0,31),'09:30–15:59':(31,44)}.items():
        d=t[(t.k>=a)&(t.k<b)]; print(f'      {lab}: model {sk(d,"P"):.1f}% · random walk {sk(d,"W"):.1f}% better than base rate')
print('\nCalibration, test 2025–26 NQ+ES, all checkpoints (predicted vs actual share already in):')
te['bin']=pd.cut(te.P,[0,.1,.2,.3,.4,.5,.6,.7,.8,.9,.95,1.0])
cal=te.groupby('bin',observed=True).agg(n=('y','size'),pred=('P','mean'),act=('y','mean'))
print((cal.assign(pred=lambda x:(x.pred*100).round(1),act=lambda x:(x.act*100).round(1))).to_string())
for s in ['NQ','ES']:
    t=te[te.sym==s]; t2=t.assign(bin=pd.cut(t.P,[0,.2,.4,.6,.8,.9,1.0]))
    c=t2.groupby('bin',observed=True).agg(n=('y','size'),pred=('P','mean'),act=('y','mean'))
    print(s,' '.join(f'[{iv.left:.1f}-{iv.right:.1f}] {r.pred*100:.0f}/{r.act*100:.0f}' for iv,r in c.iterrows()))
np.save('ext_coef_train.npy',coef); te.to_pickle('ext_test_rows.pkl')
