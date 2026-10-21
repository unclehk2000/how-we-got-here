"""Session-on-session Kekkai: does a sweep of the previous session's wall followed by a block shift tell us anything?
Asia 20:00-23:59 (walls = prior RTH 09:30-16:14), London 02:00-04:59 (walls = Asia), NY AM 09:30-11:29 (walls = London).
Shift = two consecutive blocks HH+HL / LL+LH (Asia 15-min blocks, London / NY AM 30-min).
Outcome after confirmation: direction-signed move to the end of the NEXT session, in units of this session's 20-day average range;
and whether the opposite wall is reached by then."""
import pandas as pd, numpy as np
b=pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
G={d:x for d,x in b.groupby('tday')}; days=sorted(G); prev={days[i]:days[i-1] for i in range(1,len(days))}
S={'Asia':(2000,2359,15),'London':(200,459,30),'NY AM':(930,1129,30)}
REF={'Asia':'RTH_prev','London':'Asia','NY AM':'London'}
NEXT_END={'Asia':459,'London':1129,'NY AM':1614}
def seg(x,a,z): return x[(x.hm>=a)&(x.hm<=z)]
def mins(hm,a): return ((hm//100)*60+hm%100-((a//100)*60+a%100))%1440
rows=[]
for d in days:
    x=G[d]
    for name,(a,z,bl) in S.items():
        s=seg(x,a,z)
        if len(s)<bl*3: continue
        if REF[name]=='RTH_prev':
            p=prev.get(d); 
            if p is None: continue
            r=seg(G[p],930,1614)
        else:
            ra,rz,_=S[REF[name]]; r=seg(x,ra,rz)
        if len(r)<10: continue
        H,L=r.High.max(),r.Low.min()
        h,l,c,hm=s.High.values,s.Low.values,s.Close.values,s.hm.values
        k=mins(hm,a)//bl; blocks=[]
        for kk in sorted(set(k)):
            m=np.where(k==kk)[0]; blocks.append((h[m].max(),l[m].min(),m[-1]))
        sh=None
        for zz in range(2,len(blocks)-0):
            (h0,l0,_),(h1,l1,_),(h2,l2,ie)=blocks[zz-2],blocks[zz-1],blocks[zz]
            if ie>=len(h)-1: break                      # need at least one bar after confirmation
            if h1>h0 and l1>l0 and h2>h1 and l2>l1: sh=(1,ie); break
            if l1<l0 and h1<h0 and l2<l1 and h2<h1: sh=(-1,ie); break
        tH=np.argmax(h>H) if (h>H).any() else None; tL=np.argmax(l<L) if (l<L).any() else None
        rec=dict(day=d,sess=name,rng=h.max()-l.min(),sweptH=tH is not None,sweptL=tL is not None)
        if sh:
            dr,ic=sh
            sH=tH is not None and tH<=ic; sL=tL is not None and tL<=ic
            cls='both swept' if (sH and sL) else ('reversal' if ((sH and dr<0) or (sL and dr>0)) else ('continuation' if (sH or sL) else 'no sweep'))
            # path to end of next session
            after=pd.concat([s.iloc[ic+1:]]+[seg(x,z+1 if z!=2359 else 0,NEXT_END[name])] if name!='Asia' else [s.iloc[ic+1:],seg(x,0,NEXT_END[name])])
            ce=c[ic]; endp=after.Close.iloc[-1] if len(after) else ce
            opp=(after.Low<=L).any() if dr<0 else (after.High>=H).any()
            rec.update(shift=dr,cls=cls,move=dr*(endp-ce),oppwall=float(opp))
        rows.append(rec)
D=pd.DataFrame(rows)
D['avg']=D.groupby('sess').rng.transform(lambda r:r.shift().rolling(20).mean())
D['move_u']=D.move/D.avg
D['year']=pd.to_datetime(D.day).dt.year
D['split']=np.where(D.year>=2025,'TEST 2025-26','train 2018-24')
D.to_pickle('sos.pkl')
pd.set_option('display.width',220)
X=D[D['shift'].notna()&D.avg.notna()]
g=X.groupby(['sess','split','cls']).agg(n=('move_u','size'),hit=('move_u',lambda v:100*(v>0).mean()),mean_move=('move_u','mean'),opp_wall=('oppwall',lambda v:100*v.mean()))
print(g.round(3).to_string())
print('\nshift frequency by session:',D.groupby('sess').apply(lambda s:f"{100*s['shift'].notna().mean():.0f}% of {len(s)}").to_dict())
print('wall swept at all during session:',D.groupby('sess').apply(lambda s:f"H {100*s.sweptH.mean():.0f}% L {100*s.sweptL.mean():.0f}% both {100*(s.sweptH&s.sweptL).mean():.0f}%").to_dict())
