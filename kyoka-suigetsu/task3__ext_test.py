"""Is today's high / low already in? Per hour slot, logistic models on:
u = ln(range so far) − expected log range (HAR, walk-forward), pos = close position in today's range (0 low … 1 high).
High and mirrored low are pooled (low uses 1 − pos). Train 2018–24, test 2025–26."""
import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
from common import *
import statsmodels.api as sm
NQ=prep('NQ'); ES=prep('ES')
def stack(S,i):
    u=np.log(S[f'r{i}'].clip(lower=1e-4))-S.har; p=S[f'p{i}']
    a=pd.DataFrame({'u':u,'pos':p,'y':S[f'hi{i}'],'side':'hi','sym':S.sym,'yr':S.index.year},index=S.index)
    b=pd.DataFrame({'u':u,'pos':1-p,'y':S[f'lo{i}'],'side':'lo','sym':S.sym,'yr':S.index.year},index=S.index)
    return pd.concat([a,b])
SPECS={'base rate':[], 'pos':['pos'], 'u':['u'], 'u+pos':['u','pos'], 'u+pos+u·pos':['u','pos','up'], 'u+pos+pos²':['u','pos','pos2']}
def X(d,cols):
    d=d.assign(up=d.u*d.pos,pos2=d.pos**2); return sm.add_constant(d[cols],has_constant='add')
def ll(y,p): p=np.clip(p,1e-6,1-1e-6); return -(y*np.log(p)+(1-y)*np.log(1-p)).mean()
res=[]; coefs={}
for i in range(22):
    A=pd.concat([stack(NQ,i),stack(ES,i)]); tr=A[A.yr<=2024]; te=A[A.yr>=2025]
    for nm,cols in SPECS.items():
        m=sm.GLM(tr.y,X(tr,cols),family=sm.families.Binomial()).fit()
        for sym in ['NQ','ES']:
            t=te[te.sym==sym]; p=m.predict(X(t,cols))
            res.append(dict(slot=i,spec=nm,sym=sym,ll=ll(t.y,p),brier=((t.y-p)**2).mean(),base=t.y.mean()))
        if nm=='u+pos': coefs[i]=m.params
R=pd.DataFrame(res)
for sym in ['NQ','ES']:
    x=R[R.sym==sym].pivot(index='slot',columns='spec',values='brier')
    b=R[(R.sym==sym)&(R.spec=='base rate')].set_index('slot')
    print(f'\n== {sym} test 2025–26 · Brier score (lower = better) · skill vs base rate by hour')
    print(f"{'ET':>6} {'P(in) act':>9} | "+' '.join(f'{c:>11}' for c in SPECS)+' | skill u+pos')
    for i,r in x.iterrows():
        print(f"{(18+i)%24:02d}:59 {b.base[i]*100:8.0f}% | "+' '.join(f'{r[c]:11.4f}' for c in SPECS)+f' | {100*(1-r["u+pos"]/r["base rate"]):5.1f}%')
    m=x.mean(); print(f"  mean           | "+' '.join(f'{m[c]:11.4f}' for c in SPECS)+f' | {100*(1-m["u+pos"]/m["base rate"]):5.1f}%')
print('\ncoefficients u+pos (pooled, train 2018–24):'); print(pd.DataFrame(coefs).T.round(3).to_string())
R.to_pickle('ext_cmp.pkl')
