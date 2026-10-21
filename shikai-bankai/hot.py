"""Shikai hot-block tool, real-time version: the widest 30-min block SO FAR (known at its close).
Target = its midpoint; touched before session end? Mirror placebo = same distance from the block close, opposite side.
Also the hindsight version (true hottest block of the session) to show the look-ahead gap."""
import pandas as pd, numpy as np
b=pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts'); G={d:x for d,x in b.groupby('tday')}
S=pd.read_pickle('/home/claude/twin/states_NQ.pkl')
def seg(x,a,z): return x[(x.hm>=a)&(x.hm<=z)]
def mins(hm,a): return ((hm//100)*60+hm%100-((a//100)*60+a%100))%1440
SES={'Asia':(2000,2359),'London':(200,459),'NY AM':(930,1059),'NY PM':(1330,1559)}
def touched(h,l,lvl,c): return (h>=lvl).any() if lvl>c else (l<=lvl).any()
rows=[]
for d,x in G.items():
    for nm,(a,z) in SES.items():
        s=seg(x,a,z)
        if len(s)<60: continue
        h,l,c=s.High.values,s.Low.values,s.Close.values; k=mins(s.hm.values,a)//30
        blocks=[(np.where(k==q)[0]) for q in sorted(set(k))]
        rng=[h[m].max()-l[m].min() for m in blocks]
        # real-time: each time a block closes as the widest so far (excluding the last block), test from next bar
        best=-1; rt=[]
        for q,m in enumerate(blocks[:-1]):
            if rng[q]>best:
                best=rng[q]; mid=(h[m].max()+l[m].min())/2; e=m[-1]; cc=c[e]
                if abs(cc-mid)<1e-9: continue
                mir=cc+(cc-mid); hh,ll=h[e+1:],l[e+1:]
                rt.append((touched(hh,ll,mid,cc),touched(hh,ll,mir,cc)))
        if rt: # use the LAST widest-so-far signal (the live one at the time the session's hottest is known in real time)
            m_,r_=rt[-1]
            rows.append(dict(day=d,year=d.year,sess=nm,rt_mid=m_,rt_mir=r_))
        q=int(np.argmax(rng)); m=blocks[q]
        if q<len(blocks)-1:
            mid=(h[m].max()+l[m].min())/2; e=m[-1]; cc=c[e]; mir=cc+(cc-mid)
            rows[-1].update(hs_mid=touched(h[e+1:],l[e+1:],mid,cc),hs_mir=touched(h[e+1:],l[e+1:],mir,cc)) if rows and rows[-1]['day']==d and rows[-1]['sess']==nm else None
D=pd.DataFrame(rows).set_index('day').join(S[['prev_state']])
D['split']=np.where(D.year>=2025,'test','train')
pd.set_option('display.width',200)
g=D.groupby(['sess','split'])[['rt_mid','rt_mir','hs_mid','hs_mir']].mean().mul(100).round(1)
g['n']=D.groupby(['sess','split']).size(); print(g)
print('\nreal-time mid vs mirror by prev_state:')
print(D.groupby(['sess','prev_state','split'])[['rt_mid','rt_mir']].agg(['mean','size']).round(3).to_string())
