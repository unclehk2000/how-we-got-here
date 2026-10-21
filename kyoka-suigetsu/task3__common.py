import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
import har2
from har2 import fit, predict, CAL
COLS=['d1','d5','d22','dn1','up1','inside']+[c for c in CAL if c!='roll_week']
_orig=har2.design2
def design3(D):
    X=_orig(D); X['inside']=((D.h.shift(1)<=D.h.shift(2))&(D.l.shift(1)>=D.l.shift(2))).astype(int); return X
har2.design2=design3
def wf_har(D):
    out=pd.Series(np.nan,index=D.index)
    for y in range(2013,2027):
        m,ok=fit(D,COLS,D.year<y); out[D.year==y]=predict(D,m,COLS)[D.year==y]
    return out
def prep(sym,N=30):
    D=pd.read_pickle(f'F_{sym}.pkl'); D['har']=wf_har(D)
    S=pd.read_pickle(f'slots2_{sym}.pkl').join(D[['har']],how='inner')
    S=S[S.final>0].copy(); S['lf']=np.log(S.final)
    for i in range(23):
        sh=(S[f'r{i}']/S.final).clip(1e-4,1)
        S[f'sh{i}']=np.log(sh.rolling(N).median().shift(1))
    S['sym']=sym
    return S.dropna(subset=['har']+[f'sh{i}' for i in range(23)])
