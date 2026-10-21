"""Per trading day, at the end of each hour slot (18:00 … 16:00 ET): running range %, close position in the range,
and whether the day's final high / low is already in. Merged holiday days and days that disagree with the
Barchart daily range by >5% are left out."""
import pandas as pd, numpy as np, sys
T2='/home/claude/t2'
def build(sym):
    b=pd.read_pickle(f'bars_{sym}_all.pkl')
    D=pd.read_pickle(f'{T2}/D_{sym}.pkl')
    merged=(b.tday!=b.tday0).groupby(b.tday).any()
    b=b[~b.tday.isin(merged[merged].index)].sort_values('ts')
    b['slot']=(b.ts.dt.hour-18)%24; b=b[b.slot<=22]
    g=b.groupby(['tday','slot']).agg(H=('High','max'),L=('Low','min'),C=('Close','last'))
    o=b.groupby('tday').Open.first(); n=b.groupby('tday').size()
    H=g.H.unstack().reindex(columns=range(23)); L=g.L.unstack().reindex(columns=range(23)); C=g.C.unstack().reindex(columns=range(23))
    first=H.notna().idxmax(axis=1)
    H=H.ffill(axis=1).cummax(axis=1); L=L.ffill(axis=1).cummin(axis=1); C=C.ffill(axis=1)
    fH=H[22]; fL=L[22]
    rng=(fH-fL)/o*100
    bd=((D.h-D.l)/D.o*100).reindex(rng.index)
    ok=(n>=1000)&((rng/bd-1).abs()<=0.05)&(first==0)&H[0].notna()
    out={}
    for s in range(23):
        out[f'r{s}']=(H[s]-L[s])/o*100
        out[f'p{s}']=((C[s]-L[s])/(H[s]-L[s])).where(H[s]>L[s],0.5)
        out[f'hi{s}']=(H[s]>=fH-1e-9).astype(int)
        out[f'lo{s}']=(L[s]<=fL+1e-9).astype(int)
    S=pd.DataFrame(out); S['final']=rng; S['open']=o; S['n']=n
    S=S[ok]; S.index.name='tday'
    print(sym,'days kept',len(S),'of',len(ok),'| dropped',(~ok).sum(),'| merged-holiday days excluded',merged.sum())
    return S
if __name__=='__main__':
    for s in sys.argv[1:] or ['ES','NQ']:
        S=build(s); S.to_pickle(f'slots2_{s}.pkl')
        print(S.groupby(S.index.year).size().to_dict())
