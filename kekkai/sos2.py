"""Kekkai session-on-session re-test on the user's session definitions:
Asia 20:00-00:00, London 02:00-05:00, NY AM 09:30-11:00, NY Lunch 11:30-13:00, NY PM 13:30-16:00 (ET).
Chain: London hunts Asia walls; NY AM hunts London walls; NY PM hunts Lunch walls.
Shift = two consecutive 30-min blocks HH+HL / LL+LH; may confirm on the session's final block (checked at the close).
Outcome: direction to the end of the next hunt session (London->NY AM 11:00, NY AM->NY PM 16:00, NY PM->16:59 close),
and whether the opposite wall is reached by then; baseline = same after any first sweep."""
import pandas as pd, numpy as np
b=pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts'); G={d:x for d,x in b.groupby('tday')}
def seg(x,a,z): return x[(x.hm>=a)&(x.hm<=z)]
def mins(hm,a): return ((hm//100)*60+hm%100-((a//100)*60+a%100))%1440
# name: (start, end, wall_start, wall_end, outcome_end)
S={'London':(200,459,2000,2359,1059),'NY AM':(930,1059,200,459,1559),'NY PM':(1330,1559,1130,1259,1659)}
rows=[]
for d,x in G.items():
    for name,(a,z,ra,rz,ne) in S.items():
        s=seg(x,a,z); r=seg(x,ra,rz)
        if len(s)<60 or len(r)<30: continue
        H,L=r.High.max(),r.Low.min(); h,l,c,hm=s.High.values,s.Low.values,s.Close.values,s.hm.values
        k=mins(hm,a)//30; blocks=[]
        for kk in sorted(set(k)):
            m=np.where(k==kk)[0]; blocks.append((h[m].max(),l[m].min(),m[-1]))
        sh=None
        for zz in range(2,len(blocks)):
            (h0,l0,_),(h1,l1,_),(h2,l2,ie)=blocks[zz-2],blocks[zz-1],blocks[zz]
            if h1>h0 and l1>l0 and h2>h1 and l2>l1: sh=(1,ie); break
            if l1<l0 and h1<h0 and l2<l1 and h2<h1: sh=(-1,ie); break
        tH=np.argmax(h>H) if (h>H).any() else None; tL=np.argmax(l<L) if (l<L).any() else None
        rec=dict(day=d,sess=name,year=d.year,rng=h.max()-l.min(),sweptH=tH is not None,sweptL=tL is not None)
        if tH is not None or tL is not None:
            first='H' if tL is None or (tH is not None and tH<tL) else 'L'; i=tH if first=='H' else tL
            aft=pd.concat([s.iloc[i+1:],seg(x,z+1,ne)])
            rec['base_opp']=float((aft.Low<=L).any() if first=='H' else (aft.High>=H).any())
        if sh:
            dr,ic=sh; sH=tH is not None and tH<=ic; sL=tL is not None and tL<=ic
            cls='both swept' if (sH and sL) else ('reversal' if ((sH and dr<0) or (sL and dr>0)) else ('continuation' if (sH or sL) else 'no sweep'))
            aft=pd.concat([s.iloc[ic+1:],seg(x,z+1,ne)])
            if len(aft):
                rec.update(shift=dr,cls=cls,hit=float(dr*(aft.Close.iloc[-1]-c[ic])>0),
                           opp=float((aft.Low<=L).any() if dr<0 else (aft.High>=H).any()),
                           conf=int(hm[ic]))
        rows.append(rec)
D=pd.DataFrame(rows); D['split']=np.where(D.year>=2025,'test 25-26','train 18-24')
pd.set_option('display.width',200)
print('sessions:',D.groupby('sess').size().to_dict())
print('\nwalls swept during the hunt session (%):')
print(D.groupby('sess').agg(H=('sweptH','mean'),L=('sweptL','mean')).mul(100).round(0).assign(both=D.groupby('sess').apply(lambda s:round(100*(s.sweptH&s.sweptL).mean()))))
print('\nshift frequency (%):',D.groupby('sess')['shift'].apply(lambda v:round(100*v.notna().mean())).to_dict())
X=D[D['shift'].notna()]
print('\nshift confirmation time (share):'); print(X.groupby('sess').conf.apply(lambda v:(v//100*100+(v%100>=30)*30).value_counts(normalize=True).round(2).to_dict()))
print('\ndirection hit % to end of next session, by class:')
print(X.groupby(['sess','cls','split']).hit.agg(n='size',hit=lambda v:round(100*v.mean(),1)).unstack('split'))
print('\nreversal -> opposite wall vs baseline after any first sweep:')
rv=X[X.cls=='reversal'].groupby(['sess','split']).opp.agg(n='size',pct=lambda v:round(100*v.mean(),1))
bs=D.dropna(subset=['base_opp']).groupby(['sess','split']).base_opp.agg(n='size',pct=lambda v:round(100*v.mean(),1))
print(rv.join(bs,lsuffix='_rev',rsuffix='_base'))
