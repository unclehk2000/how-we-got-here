"""Same NY AM trade at decoy fractions: enter at level f of the gap on first touch, stop 0.25 gap beyond, target the open.
Zero drift => expected R = 0 at every f, so R is comparable across levels."""
import pandas as pd, numpy as np, pickle, sys
def trade(h,l,c,n,O,Cm,f):
    g=np.sign(O-Cm); L=O+f*(Cm-O); stop=O+(f+0.25)*(Cm-O)
    mm=np.where((l[:n]<=L)&(h[:n]>=L))[0]
    if not len(mm): return np.nan
    for j in range(mm[0]+1,n):
        hs=(l[j]<=stop) if g>0 else (h[j]>=stop); ht=(h[j]>=O) if g>0 else (l[j]<=O)
        if hs: return -1.0
        if ht: return f/0.25
    return g*(c[n-1]-L)/abs(L-stop)
FR=[0.25,0.375,0.5,0.625,0.75]
for m in sys.argv[1:] or ['NQ','ES']:
    F=pd.read_pickle(f'nyam_{m}.pkl'); rth,paths=pickle.load(open(f'twin_{m}.pkl','rb')); rows=[]
    for d,r in F.iterrows():
        x=paths[d]; hm=x.index.values; n=(hm<=1059).sum()
        rows.append({'day':d,'g':r.g,**{f:trade(x.High.values,x.Low.values,x.Close.values,n,r.O,r.Cm,f) for f in FR}})
    Q=pd.DataFrame(rows).set_index('day')
    print(f'\n{m}: mean R (t) by entry fraction — NY AM, stop 0.25 gap beyond, target = 09:30 open')
    for lab,s in [('all',Q),('gap up (long)',Q[Q.g>0]),('gap down (short)',Q[Q.g<0]),('2018/2022',Q[Q.index.year.isin([2018,2022])]),('2023-24',Q[Q.index.year.isin([2023,2024])]),('2025-26',Q[Q.index.year.isin([2025,2026])])]:
        print(f'  {lab:17s}'+'  '.join([f'{f}: {s[f].mean():+.3f} ({s[f].mean()/s[f].std()*np.sqrt(s[f].notna().sum()):+.1f}, n {s[f].notna().sum()})' for f in FR]))
    Q.to_pickle(f'decoytr_{m}.pkl')
