import pandas as pd, numpy as np
b=pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts'); G={d:x for d,x in b.groupby('tday')}
def seg(x,a,z): return x[(x.hm>=a)&(x.hm<=z)]
out=[]
for d,x in G.items():
    for name,(a,z,ra,rz,ne) in {'London':(200,459,2000,2359,1129),'NY AM':(930,1129,200,459,1614)}.items():
        s=seg(x,a,z); r=seg(x,ra,rz)
        if len(s)<60 or len(r)<10: continue
        H,L=r.High.max(),r.Low.min(); h,l=s.High.values,s.Low.values
        tH=np.argmax(h>H) if (h>H).any() else None; tL=np.argmax(l<L) if (l<L).any() else None
        if tH is None and tL is None: continue
        first='H' if tL is None or (tH is not None and tH<tL) else 'L'
        i=tH if first=='H' else tL
        after=pd.concat([s.iloc[i+1:],seg(x,z+1,ne)])
        opp=(after.Low<=L).any() if first=='H' else (after.High>=H).any()
        out.append(dict(sess=name,year=d.year,opp=opp))
O=pd.DataFrame(out); O['split']=np.where(O.year>=2025,'test','train')
print(O.groupby(['sess','split']).opp.agg(['size','mean']).round(3))
