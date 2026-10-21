from common import *
import statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg
Q=(0.10,0.25,0.5,0.75,0.90)
NQ=prep('NQ'); ES=prep('ES'); P=pd.concat([NQ,ES])
def xy(S,i):
    lrun=np.log(S[f'r{i}'].clip(lower=1e-4)); proj=lrun-S[f'sh{i}']
    X=sm.add_constant(pd.DataFrame({'gap':S.har-proj}),has_constant='add'); return X,S.lf-proj,proj,lrun
def fitq(S,i):
    X,y,_,_=xy(S,i); return {q:QuantReg(y,X).fit(q=q).params for q in Q}
def pred(S,i,par):
    X,_,proj,lrun=xy(S,i); return {q:np.maximum(proj+X@par[q],lrun) for q in Q}
tr=lambda S:S[S.index.year<=2024]; te=lambda S:S[S.index.year>=2025]
rows=[]
for i in range(23):
    pN=fitq(tr(NQ),i); pE=fitq(tr(ES),i); pP=fitq(tr(P),i)
    for tgt,T in [('ES',te(ES)),('NQ',te(NQ))]:
        r={'slot':i,'tgt':tgt}
        for nm,par in [('NQw',pN),('ESw',pE),('Pool',pP)]:
            p=pred(T,i,par); e=(T.lf-p[0.5]).abs().mean()
            r[nm]=e; r[nm+'_c50']=((T.lf>=p[0.25])&(T.lf<=p[0.75])).mean(); r[nm+'_c80']=((T.lf>=p[0.10])&(T.lf<=p[0.90])).mean()
        # baselines: typical day (median of last 30 finals, bias-corrected on train) and HAR alone
        base=np.log(pd.concat([tr(T.assign()) if False else T]).final)  # placeholder
        rows.append(r)
R=pd.DataFrame(rows)
# baselines
def base_err(S):
    b=np.log(S.final.rolling(30).median().shift(1)); c=(S.lf-b)[S.index.year<=2024].median()
    hc=(S.lf-S.har)[S.index.year<=2024].median()
    t=S.index.year>=2025
    return (S.lf-b-c)[t].abs().mean(), (S.lf-S.har-hc)[t].abs().mean()
for tgt,S in [('ES',ES),('NQ',NQ)]:
    bt,bh=base_err(S); x=R[R.tgt==tgt].set_index('slot')
    print(f'\n== {tgt} test 2025–26 ({len(te(S))} days) · MAE of log final range · typical-day {bt:.3f} · HAR alone {bh:.3f}')
    print(f"{'ET':>6} | {'NQ wts':>6} {'ES wts':>6} {'pooled':>6} | P25–75 cover NQw/ESw/Pool | P10–90 cover NQw/ESw/Pool")
    for i,r in x.iterrows():
        print(f"{(18+i)%24:02d}:59 | {r.NQw:6.3f} {r.ESw:6.3f} {r.Pool:6.3f} | {r.NQw_c50*100:4.0f} {r.ESw_c50*100:4.0f} {r.Pool_c50*100:4.0f}           | {r.NQw_c80*100:4.0f} {r.ESw_c80*100:4.0f} {r.Pool_c80*100:4.0f}")
    print(f"  mean | {x.NQw.mean():6.3f} {x.ESw.mean():6.3f} {x.Pool.mean():6.3f} | {x.NQw_c50.mean()*100:4.0f} {x.ESw_c50.mean()*100:4.0f} {x.Pool_c50.mean()*100:4.0f}           | {x.NQw_c80.mean()*100:4.0f} {x.ESw_c80.mean()*100:4.0f} {x.Pool_c80.mean()*100:4.0f}")
R.to_pickle('proj_cmp.pkl')
