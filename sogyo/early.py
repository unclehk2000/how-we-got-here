"""Real-time proxy for a consolidation day: the 09:30-10:29 range vs its trailing 20-day average, known at 10:30.
Only zone touches that happen at/after 10:30 are scored, so the proxy is known before the barrier is tested."""
import pandas as pd, numpy as np, pickle, sys
from barrier import race
from summary import wil
for m in sys.argv[1:] or ['NQ','ES']:
    rth,paths=pickle.load(open(f'twin_{m}.pkl','rb')); B=pd.read_pickle(f'barrier_{m}.pkl')
    fh=pd.Series({d:(lambda x:(x.High.max()-x.Low.min()))(paths[d].loc[930:1029]) for d in rth.index})
    blk=(fh.index.to_series().diff().dt.days>10).cumsum()
    rel=fh/fh.groupby(blk).transform(lambda r:r.shift().rolling(20).mean())
    rows=[]
    for d,r in B.iterrows():
        x=paths[d]; hm=x.index.values; n=(hm<=1614).sum(); h,l,c=x.High.values,x.Low.values,x.Close.values
        O=rth.loc[d,'O']; Cm=(rth.loc[d,'C1']+rth.loc[d,'C2'])/2; i0=np.searchsorted(hm,1030)
        rec=dict(day=d,rel=rel.get(d),state=r.state)
        for f in (0.375,0.5,0.625):
            L=O+f*(Cm-O); T=O+2*f*(Cm-O)
            mm=np.where((l[:n]<=L)&(h[:n]>=L))[0]
            if len(mm) and mm[0]>=i0: rec[f'a{f}']=race(h,l,c,mm[0],O,T,L,n)[0]
        rows.append(rec)
    E=pd.DataFrame(rows).set_index('day').dropna(subset=['rel'])
    E['tier']=pd.qcut(E.rel,3,labels=['narrow first hour','normal','wide first hour'])
    print(f'\n{m}: zone first touched at/after 10:30 — away rate by first-hour range tercile')
    for t,sub in E.groupby('tier',observed=True):
        s=sub['a0.5'].dropna(); k=s.sum(); n=len(s); lo,hi=wil(k,n)
        print(f'  {t:18s} CE zone {100*k/n:.1f}% (n {n}, CI {lo:.0f}–{hi:.0f}) | placebo 0.375 {100*sub["a0.375"].mean():.1f}% (n {sub["a0.375"].notna().sum()}) | 0.625 {100*sub["a0.625"].mean():.1f}% | became Consolidation {100*(sub.state=="Consolidation").mean():.0f}%')
    B2=B[B.state=='Consolidation']
    print('  same-day Consolidation away rate by year:',B2.groupby(B2.index.year)['away_0.5'].agg(lambda s:f'{100*s.mean():.0f}% ({s.notna().sum()})').to_dict())
