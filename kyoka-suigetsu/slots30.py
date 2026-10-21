"""Half-hour checkpoints (end of minute :29 and :59 of each hour slot) for checking the in-hour interpolation."""
import pandas as pd, numpy as np, sys
def build(sym):
    S1=pd.read_pickle(f'slots2_{sym}.pkl'); keep=S1.index
    b=pd.read_pickle(f'bars_{sym}_all.pkl'); b=b[b.tday.isin(keep)].sort_values('ts')
    b['slot']=(b.ts.dt.hour-18)%24; b=b[b.slot<=22]
    b['k']=b.slot*2+(b.ts.dt.minute>=30)          # 0..45 half-hour buckets
    g=b.groupby(['tday','k']).agg(H=('High','max'),L=('Low','min'),C=('Close','last'))
    o=b.groupby('tday').Open.first()
    H=g.H.unstack().reindex(columns=range(46)).ffill(axis=1).cummax(axis=1)
    L=g.L.unstack().reindex(columns=range(46)).ffill(axis=1).cummin(axis=1)
    C=g.C.unstack().reindex(columns=range(46)).ffill(axis=1)
    fH=H[45]; fL=L[45]; out={}
    for k in range(46):
        out[f'r{k}']=(H[k]-L[k])/o*100; out[f'p{k}']=((C[k]-L[k])/(H[k]-L[k])).where(H[k]>L[k],0.5)
        out[f'hi{k}']=(H[k]>=fH-1e-9).astype(int); out[f'lo{k}']=(L[k]<=fL+1e-9).astype(int)
        out[f'c{k}']=C[k]/o
    S=pd.DataFrame(out); S['final']=(fH-fL)/o*100; S.index.name='tday'
    return S
if __name__=='__main__':
    for s in ['ES','NQ']:
        S=build(s); S.to_pickle(f'slots30_{s}.pkl'); print(s,len(S))
