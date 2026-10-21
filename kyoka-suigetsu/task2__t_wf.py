import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np
from har2 import fit, predict, CAL
COLS=['d1','d5','d22','dn1','up1']+CAL
res={}
for s in ['NQ','ES','RTY']:
    D=pd.read_pickle(f'F_{s}.pkl')
    base=np.log(D.rng.rolling(30).median().shift(1)); atr=np.log(D.atr14)
    rows=[]
    for y in range(2013,2027):
        tr=(D.year<y); te=D.year==y
        m,ok=fit(D,COLS,tr); p=predict(D,m,COLS)
        c0=(D.lr-base)[ok&tr].median(); c1=(D.lr-atr)[ok&tr].median()
        e=(D.lr-p)[ok&te]; eb=(D.lr-base-c0)[ok&te]; ea=(D.lr-atr-c1)[ok&te]
        q25,q75=np.percentile(m.resid,[25,75])
        rows.append(dict(year=y,n=len(e),HAR=e.abs().mean(),Kyoka=eb.abs().mean(),ATR=ea.abs().mean(),bias=e.mean(),cov50=((e>=q25)&(e<=q75)).mean()))
    T=pd.DataFrame(rows).set_index('year'); T['gain_vs_Kyoka_%']=100*(1-T.HAR/T.Kyoka)
    res[s]=T
    print(f'\n== {s}: walk-forward (refit every year on all prior years) — MAE of log range ==')
    print(T.round(3).to_string())
    print(f'  years HAR beats Kyōka typical: {(T.HAR<T.Kyoka).sum()}/{len(T)}; beats ATR14: {(T.HAR<T.ATR).sum()}/{len(T)}; pooled gain {100*(1-(T.HAR*T.n).sum()/(T.Kyoka*T.n).sum()):.1f}%')
pd.to_pickle(res,'wf.pkl')
