"""ET 1-min bars, trade dates on the CME convention: a holiday session belongs to the next trade date.
ES = 2018–2022 (new) + 2023–2026 (earlier upload); NQ = 2018–2026."""
import pandas as pd, numpy as np
T2='/home/claude/t2'
def remap(b,sym):
    cal=pd.DatetimeIndex(pd.read_pickle(f'{T2}/D_{sym}.pkl').index)
    td=pd.DatetimeIndex(b.tday.unique()).sort_values()
    pos=cal.searchsorted(td)                       # next calendar trade date on or after the session date
    ok=pos<len(cal)
    m=pd.Series(pd.NaT,index=td,dtype='datetime64[us]'); m[ok]=cal[pos[ok]]
    b=b.copy(); b['tday0']=b.tday; b['tday']=b.tday.map(m)
    return b.dropna(subset=['tday'])
def es():
    a=pd.read_pickle('/home/claude/t3/bars_ES_1822.pkl'); c=pd.read_pickle('/home/claude/twin/bars_ES.pkl')
    b=pd.concat([a,c[a.columns]]).sort_values('ts').drop_duplicates('ts').reset_index(drop=True)
    return remap(b,'ES')
def nq():
    return remap(pd.read_pickle('/home/claude/twin/bars_NQ_full.pkl'),'NQ')
if __name__=='__main__':
    E=es(); E.to_pickle('bars_ES_all.pkl'); N=nq(); N.to_pickle('bars_NQ_all.pkl')
    for s,b in [('ES',E),('NQ',N)]:
        D=pd.read_pickle(f'{T2}/D_{s}.pkl')
        g=b.groupby('tday').agg(H=('High','max'),L=('Low','min'),n=('ts','size'),con=('Contract','last'))
        print(s,len(b),'tdays',len(g),g.index.min().date(),g.index.max().date(),'merged holiday sessions:',(b.tday!=b.tday0).groupby(b.tday).any().sum())
        yr=g.groupby(g.index.year).size(); print(yr.to_dict())
