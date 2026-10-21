"""Kekkai shift mechanic re-test, RTH NY and ETH sessions, with three fill assumptions.
Shift: two consecutive 30-min blocks HH+HL (bull) / LL+LH (bear), confirmed when the 3rd block closes.
Pre-shift block = the block before the confirming block (default reading of Model 4).
Fills: A 'as written' = filled at the pre-shift extreme at confirmation even if price is already past it (optimistic)
       B 'market'     = enter at the open of the first bar after confirmation; stop = pre-shift opposite extreme
       C 'limit'      = resting limit at the pre-shift extreme; filled only if price comes back to it before session end
Exit: 50% at +0.5R then stop to breakeven; rest at +1.0R (bull) / +1.5R (bear); flat at session end."""
import pandas as pd, numpy as np, sys
b=pd.read_pickle('/home/claude/twin/bars_NQ.pkl')
SESS={'NY RTH':(930,1500,1614),'Asia':(2000,2359,2359),'London':(200,459,459),'NY AM 7-9 (pre-open)':(700,929,929)}
def sim(h,l,c,i0,n,entry,stop,d,t2m):
    R=abs(entry-stop); t1=entry+d*0.5*R; t2=entry+d*t2m*R; half=False; pnl=0.0
    for j in range(i0,n):
        if not half:
            if (l[j]<=stop) if d>0 else (h[j]>=stop): return -1.0
            if (h[j]>=t1) if d>0 else (l[j]<=t1):
                half=True; pnl=0.25                                   # 50% x 0.5R
                if (h[j]>=t2) if d>0 else (l[j]<=t2): return pnl+0.5*t2m
                continue
        else:
            if (l[j]<=entry) if d>0 else (h[j]>=entry): return pnl     # breakeven on the rest
            if (h[j]>=t2) if d>0 else (l[j]<=t2): return pnl+0.5*t2m
    return (pnl+0.5*d*(c[n-1]-entry)/R) if half else d*(c[n-1]-entry)/R
def run(name,a,watch_end,end):
    g=b.copy(); g['hm']=g.hm
    if a>=1800: sel=(g.hm>=a)&(g.hm<=end)
    else: sel=(g.hm>=a)&(g.hm<=end)
    x=g[sel]; out=[]; rngs=[]
    for d,s in x.groupby('tday'):
        s=s.sort_values('ts'); hm=s.hm.values
        mins=np.where(hm>=1800,(hm//100)*60+hm%100-((a//100)*60+a%100),(hm//100)*60+hm%100-((a//100)*60+a%100)) if a<1800 else ((hm//100)*60+hm%100-((a//100)*60+a%100))
        h,l,c,o=s.High.values,s.Low.values,s.Close.values,s.Open.values
        rngs.append((d,h.max()-l.min()))
        k=mins//30; blocks=[]
        for kk in sorted(set(k)):
            m=k==kk; blocks.append((kk,h[m].max(),l[m].min(),np.where(m)[0][-1]))
        for z in range(2,len(blocks)):
            (_,h0,l0,_),(_,h1,l1,_),(kk,h2,l2,iend)=blocks[z-2],blocks[z-1],blocks[z]
            if hm[iend]>watch_end: break
            bull=h1>h0 and l1>l0 and h2>h1 and l2>l1; bear=l1<l0 and h1<h0 and l2<l1 and h2<h1
            if not(bull or bear): continue
            dd=1 if bull else -1; ent=h1 if bull else l1; stp=l1 if bull else h1; t2m=1.0 if bull else 1.5
            i0=iend+1; n=len(h)
            if i0>=n: break
            rA=sim(h,l,c,i0,n,ent,stp,dd,t2m)
            eB=o[i0]; rB=sim(h,l,c,i0,n,eB,stp,dd,t2m) if (eB-stp)*dd>0 else np.nan
            fill=next((j for j in range(i0,n) if l[j]<=ent<=h[j]),None)
            rC=sim(h,l,c,fill+1,n,ent,stp,dd,t2m) if fill is not None else np.nan
            out.append(dict(day=d,dir=dd,A=rA,B=rB,C=rC,filledC=fill is not None,
                            past=(eB-ent)*dd/abs(ent-stp)))
            break
    T=pd.DataFrame(out).set_index('day'); R=pd.Series(dict(rngs))
    blk=(R.index.to_series().diff().dt.days>10).cumsum()
    prev=R.shift(); avg=R.groupby(blk).transform(lambda r:r.shift(2).rolling(20).mean())
    cons=(prev<0.75*avg)
    T['cons']=cons.reindex(T.index).fillna(False)
    T['nfp']=[(d.weekday()==4 and d.day<=7) for d in T.index]
    return T
pd.set_option('display.width',200)
rows=[]
for name,(a,we,end) in SESS.items():
    T=run(name,a,we,end)
    for lab,S in [('all days',T),('after a consolidation session',T[T.cons&~T.nfp])]:
        r=dict(session=name,set=lab,n=len(S),
               A_anyprofit=100*(S.A>0).mean(),A_R=S.A.mean(),
               B_anyprofit=100*(S.B>0).mean(),B_R=S.B.mean(),
               C_fill=100*S.filledC.mean(),C_R=S.C.mean(),
               entry_already_past_R=S.past.median())
        rows.append(r)
print(pd.DataFrame(rows).round(2).to_string(index=False))
