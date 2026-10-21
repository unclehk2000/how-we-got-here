import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np
from scipy import stats
W5=['Mon','Tue','Wed','Thu','Fri']
for s in ['NQ','ES','RTY']:
    D=pd.read_pickle(f'F_{s}.pkl'); D['wk']=D.index.to_period('W-FRI')
    full=D.groupby('wk').filter(lambda x: len(x)==5 and list(x.dow)==[0,1,2,3,4])
    g=full.groupby('wk')
    hi=g.apply(lambda x:x.ah.values.argmax()); lo=g.apply(lambda x:x.al.values.argmin())
    yrs=pd.Series([p.year for p in hi.index],index=hi.index)
    print(f'\n== {s}: day that set the week\'s high / low ({len(hi)} full Mon–Fri weeks) ==')
    for a,b in [(2010,2017),(2018,2026)]:
        h=hi[(yrs>=a)&(yrs<=b)]; l=lo[(yrs>=a)&(yrs<=b)]
        ph=np.bincount(h,minlength=5)/len(h)*100; pl=np.bincount(l,minlength=5)/len(l)*100
        print(f'  {a}-{b} high: '+' '.join(f'{W5[i]} {ph[i]:4.1f}' for i in range(5))+f'   | low: '+' '.join(f'{W5[i]} {pl[i]:4.1f}' for i in range(5)))
    # chi2 vs uniform, full sample
    print('  chi2 vs uniform p: high', round(stats.chisquare(np.bincount(hi,minlength=5)).pvalue,4),' low', round(stats.chisquare(np.bincount(lo,minlength=5)).pvalue,4))
    # high or low on Mon/Fri (week extremes at the edges)
    edge=((hi==0)|(hi==4)|(lo==0)|(lo==4)).mean()*100
    both_edges=(((hi==0)|(hi==4))&((lo==0)|(lo==4))).mean()*100
    print(f'  at least one extreme on Mon or Fri: {edge:.1f}%  (both on Mon/Fri: {both_edges:.1f}%)')
    # conditional: after Wednesday close, if the week's high so far was set Mon or Tue, how often does it stand?
    rows=[]
    for k in range(5):
        # after day k (0..3), P(week high already set) = P(argmax<=k); conditional on the high-so-far day
        pass
    stand=[]
    for wk,x in g:
        hs=x.ah.values; ls=x.al.values
        for k in range(4):
            j=hs[:k+1].argmax(); stood=hs[:k+1].max()>=hs[k+1:].max()
            jl=ls[:k+1].argmin(); stoodl=ls[:k+1].min()<=ls[k+1:].min()
            # direction of the week so far: close day k vs Monday open
            up=x.ac.values[k]>=x.ao.values[0]
            stand.append((wk.year,k,j,stood,jl,stoodl,up))
    S=pd.DataFrame(stand,columns=['y','k','j','stood','jl','stoodl','up'])
    for a,b in [(2010,2017),(2018,2026)]:
        x=S[(S.y>=a)&(S.y<=b)]
        t=x.groupby('k')[['stood','stoodl']].mean()*100
        print(f'  {a}-{b} after {"/".join(W5[:4])} close, P(high so far holds for the week): '+' '.join(f'{v:.0f}%' for v in t.stood)+'  | low holds: '+' '.join(f'{v:.0f}%' for v in t.stoodl))
    x=S[S.k==2]
    t=x.groupby('up')[['stood','stoodl']].mean()*100
    print(f'  after Wed close, week up so far: high holds {t.loc[True,"stood"]:.0f}% / low holds {t.loc[True,"stoodl"]:.0f}%;  week down so far: high holds {t.loc[False,"stood"]:.0f}% / low holds {t.loc[False,"stoodl"]:.0f}%')
