"""Shikai/Bankai on a carry-charge market (NQ): does the long side carry the edge?
Meaningful days only (open >= 0.15% from the overnight midpoint). Train 2018-24, test 2025-26. Cost 1.0 pt round trip.
A) INTO: enter at the 09:30 open toward the midpoint; target = mid, stop = mirror (same distance other side). Race.
   Benchmark = the same race in the other direction (toward the mirror) on the other days -> pure carry/drift.
B) SWEEP-RECLAIM ('go through and trade back out'): after price trades THROUGH the level, enter on the first 1-min close
   back on the approach side; stop = extreme beyond the level - 1 tick; target 1R / 2R; time exit at 16:14 (or 11:00).
   Same rule at placebo levels: 3/8 and 5/8 of the overnight range and the mirror. Split long vs short."""
import pandas as pd, numpy as np
b=pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts'); G={d:x for d,x in b.groupby('tday')}
def seg(x,a,z): return x[(x.hm>=a)&(x.hm<=z)]
COST=1.0; TICK=0.25
def race(h,l,c,s,E,T,S,dr,end):
    risk=abs(E-S)
    for i in range(s,end):
        hitT=(h[i]>=T) if dr>0 else (l[i]<=T); hitS=(l[i]<=S) if dr>0 else (h[i]>=S)
        if hitS: return -1-COST/risk
        if hitT: return abs(T-E)/risk-COST/risk
    return dr*(c[end-1]-E)/risk-COST/risk
def reclaim(h,l,c,lvl,frm_above,start,end,tgt_R):
    """price approaches lvl; frm_above=True means price is above lvl (coming down) -> reclaim = long."""
    i0=None
    for i in range(start,end):
        if (frm_above and l[i]<=lvl) or ((not frm_above) and h[i]>=lvl): i0=i; break
    if i0 is None: return None
    ext=None
    for j in range(i0,end):
        ext=min(l[i0:j+1]) if frm_above else max(h[i0:j+1])
        through=(ext<lvl) if frm_above else (ext>lvl)
        back=(c[j]>lvl) if frm_above else (c[j]<lvl)
        if through and back:
            dr=1 if frm_above else -1; E=c[j]; S=ext-TICK if dr>0 else ext+TICK; risk=abs(E-S)
            if risk<2: return None
            T=E+dr*tgt_R*risk
            return dict(dr=dr,R=race(h,l,c,j+1,E,T,S,dr,end),t=j)
    return None
if __name__=='__main__':
    rows=[]
    for d,x in G.items():
        on=x[(x.hm>=1800)|(x.hm<=929)]; r=seg(x,930,1614)
        if len(on)<500 or len(r)<300 or r.hm.iloc[0]!=930: continue
        H,L=on.High.max(),on.Low.min(); mid=(H+L)/2; O=r.Open.iloc[0]; dist=abs(O-mid)
        if dist/O<0.0015: continue
        up=mid>O; h,l,c=r.High.values,r.Low.values,r.Close.values; n=len(r); e11=int((r.hm<=1059).sum())
        mir=O-(mid-O)
        rec=dict(day=d,year=d.year,up=up,dist=dist)
        for tag,end in [('rth',n),('11',e11)]:
            dr=1 if up else -1
            # entry at the open: race toward mid (into) with stop at mirror
            rec[f'into_{tag}']=race(h,l,c,0,O,mid,mir,dr,end)
        # sweep-reclaim at the midpoint and placebo levels; approach side is the open's side
        lv={'mid':mid,'3/8':L+(H-L)*3/8 if up else H-(H-L)*3/8,'5/8':L+(H-L)*5/8 if up else H-(H-L)*5/8,'mirror':mir}
        for name,v in lv.items():
            frm_above = O>v     # price starts above the level -> it must come down into it -> long reclaim
            if abs(O-v)<1: continue
            for tR in (1,2):
                for tag,end in [('rth',n),('11',e11)]:
                    q=reclaim(h,l,c,v,frm_above,0,end,tR)
                    if q: rec[f'rc_{name}_{tR}R_{tag}']=q['R']; rec[f'rcdir_{name}']=q['dr']
        rows.append(rec)
    D=pd.DataFrame(rows); D['split']=np.where(D.year>=2025,'test','train')
    D.to_pickle('/home/claude/sb/carry.pkl')
    def s(v): v=v.dropna(); return f"{v.mean():+.3f}R win {100*(v>0).mean():.0f}% n{len(v)}" if len(v) else '-'
    print('A) INTO the midpoint from the 09:30 open (stop = mirror). long = mid above open, short = mid below')
    for tag in ['11','rth']:
        for sp in ['train','test']:
            Z=D[D.split==sp]
            print(f"  to {tag:3s} {sp:5s} LONG into mid {s(Z[Z.up][f'into_{tag}'])} | SHORT into mid {s(Z[~Z.up][f'into_{tag}'])}")
    print('\nB) SWEEP-RECLAIM (through the level, then a close back) by direction')
    for name in ['mid','3/8','5/8','mirror']:
        for tR in (1,2):
            for tag in ['11','rth']:
                col=f'rc_{name}_{tR}R_{tag}'
                if col not in D: continue
                out=[]
                for sp in ['train','test']:
                    Z=D[(D.split==sp)&D[col].notna()]
                    out.append(f"{sp} L {s(Z[Z[f'rcdir_{name}']>0][col])} | S {s(Z[Z[f'rcdir_{name}']<0][col])}")
                print(f"  {name:6s} {tR}R to {tag:3s}  "+'  ||  '.join(out))
