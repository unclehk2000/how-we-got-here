"""Day table for the RTH / RTH2 gap midpoints.
RTH = 09:30-16:14 ET (close = 16:14 bar close), RTH2 = 09:30-16:59 ET (close = 16:59 bar close).
CE1 = (prior RTH close + today's 09:30 open)/2 ; CE2 = (prior RTH2 close + today's 09:30 open)/2."""
import pandas as pd, numpy as np
def build(mkt='NQ'):
    b=pd.read_pickle(f'bars_{mkt}.pkl')
    g=b.groupby('tday')
    def at(hm,col):
        x=b[b.hm==hm].drop_duplicates('tday').set_index('tday'); return x[col],x['Contract']
    o,oc=at(930,'Open'); c1,cc1=at(1614,'Close'); c2,cc2=at(1659,'Close')
    D=pd.DataFrame({'O':o,'ctr':oc}).join(pd.DataFrame({'c1':c1,'cc1':cc1,'c2':c2,'cc2':cc2}),how='outer').sort_index()
    D=D[D.O.notna()|D.c1.notna()]
    # prior trading day's closes (previous row that has an RTH open)
    rth=D[D.O.notna()].copy()
    rth['C1']=rth.c1.shift(); rth['C2']=rth.c2.shift(); rth['pctr1']=rth.cc1.shift(); rth['pctr2']=rth.cc2.shift()
    rth['prev_day']=pd.Series(rth.index,index=rth.index).shift()
    rth=rth[(rth.pctr1==rth.ctr)&(rth.pctr2==rth.ctr)&((rth.index-rth.prev_day).dt.days<=4)].copy()
    rth['CE1']=(rth.C1+rth.O)/2; rth['CE2']=(rth.C2+rth.O)/2
    # today's RTH and RTH2 paths
    rows=[]
    for d,r in rth.iterrows():
        x=b[(b.tday==d)&(b.hm>=930)&(b.hm<=1659)]
        if x.hm.min()!=930 or x.hm.max()<1614: continue
        x=x.set_index('hm')
        rows.append((d,x))
    return rth,dict(rows)
if __name__=='__main__':
    import pickle,sys
    for m in sys.argv[1:] or ['NQ','ES']:
        rth,paths=build(m); rth=rth.loc[list(paths)]
        pickle.dump((rth,paths),open(f'twin_{m}.pkl','wb')); print(m,len(rth),'days', rth.index.min().date(), rth.index.max().date())
