import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np, statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg
from har2 import fit, predict, CAL
import warnings; warnings.filterwarnings('ignore')
COLS=['d1','d5','d22','dn1','up1','inside']+[c for c in CAL if c!='roll_week']
import har2
_orig=har2.design2
def design3(D):
    X=_orig(D); X['inside']=((D.h.shift(1)<=D.h.shift(2))&(D.l.shift(1)>=D.l.shift(2))).astype(int); return X
har2.design2=design3
def wf_har(D):
    out=pd.Series(np.nan,index=D.index)
    for y in range(2013,2027):
        m,ok=fit(D,COLS,D.year<y); out[D.year==y]=predict(D,m,COLS)[D.year==y]
    return out
def prep(sym):
    D=pd.read_pickle(f'F_{sym}.pkl'); D['har']=wf_har(D)
    S=pd.read_pickle(f'slots_{sym}.pkl').join(D[['har']],how='inner')
    S=S.dropna(subset=[f's{i}' for i in range(23)]); S=S[S.final>0]; S['lf']=np.log(S.final)
    for i in range(23):
        sh=(S[f's{i}']/S.final).clip(1e-4,1)
        S[f'sh{i}']=np.log(sh.rolling(30).median().shift(1))
    return S.dropna(subset=['har']+[f'sh{i}' for i in range(23)])
def slot_fit(S,i,mask):
    r=S[f's{i}'].clip(lower=1e-4); lrun=np.log(r); proj=lrun-S[f'sh{i}']
    gap=S.har-proj; y=S.lf-proj
    X=sm.add_constant(pd.DataFrame({'gap':gap}))
    fits={q:QuantReg(y[mask],X[mask]).fit(q=q) for q in (0.10,0.25,0.5,0.75,0.90)}
    return fits,proj,lrun,X
NQ=prep('NQ'); ES=prep('ES')
rows=[]
print('Per-hour projection: weight on HAR (rest on range-so-far ÷ typical share), test NQ 2025–26 and ES 2023–26 with NQ-fitted weights\n')
print(f"{'slot':>5} {'ET':>5} | {'w_HAR':>5} | NQ MAE proj / share / typical | P25–75 cov | ES MAE proj / share / typical | ES cov")
for i in range(23):
    tr=NQ.index.year<=2024; te=NQ.index.year>=2025
    fits,proj,lrun,X=slot_fit(NQ,i,tr)
    def pr(S,fits,proj,lrun,X,q): return np.maximum(proj+fits[q].predict(X),lrun)
    p=pr(NQ,fits,proj,lrun,X,0.5); lo=pr(NQ,fits,proj,lrun,X,0.25); hi=pr(NQ,fits,proj,lrun,X,0.75)
    e=(NQ.lf-p)[te].abs().mean()
    c0=(NQ.lf-proj)[tr].median(); es=(NQ.lf-proj-c0)[te].abs().mean()
    base=np.log(NQ.final.rolling(30).median().shift(1)); cb=(NQ.lf-base)[tr].median(); et=(NQ.lf-base-cb)[te].abs().mean()
    cov=((NQ.lf>=lo)&(NQ.lf<=hi))[te].mean()
    # transfer to ES
    f2,proj2,lrun2,X2=slot_fit(ES,i,ES.index.year>=0)  # only for proj/X construction
    pE=np.maximum(proj2+fits[0.5].predict(X2),lrun2); loE=np.maximum(proj2+fits[0.25].predict(X2),lrun2); hiE=np.maximum(proj2+fits[0.75].predict(X2),lrun2)
    eE=(ES.lf-pE).abs().mean(); esE=(ES.lf-proj2-c0).abs().mean()
    baseE=np.log(ES.final.rolling(30).median().shift(1)); etE=(ES.lf-baseE-cb).abs().mean()
    covE=((ES.lf>=loE)&(ES.lf<=hiE)).mean()
    et_lab=f'{(18+i)%24:02d}:59'
    print(f"{i:>5} {et_lab:>5} | {fits[0.5].params.gap:5.2f} | {e:.3f} / {es:.3f} / {et:.3f}       | {cov*100:6.0f}%   | {eE:.3f} / {esE:.3f} / {etE:.3f}       | {covE*100:4.0f}%")
    # production weights from all NQ data
    fa,_,_,_=slot_fit(NQ,i,NQ.index.year>=0)
    rows.append(dict(slot=i,**{f'w{int(q*100)}':fa[q].params.gap for q in fa},**{f'c{int(q*100)}':fa[q].params.const for q in fa}))
W=pd.DataFrame(rows).set_index('slot'); W.to_pickle('proj_weights.pkl'); print(); print(W.round(3).to_string())
