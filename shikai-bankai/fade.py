"""Reversal at the level with a fixed stop (limit fill at first touch): stop 0.5 x d beyond the level,
target 0.5 x d (1R) or 1.0 x d back toward the open (2R). d = |open - midpoint|. Cost 1 pt. By direction + placebos."""
import pandas as pd, numpy as np
from carry import race, seg, G
rows=[]
for d,x in G.items():
    on=x[(x.hm>=1800)|(x.hm<=929)]; r=seg(x,930,1614)
    if len(on)<500 or len(r)<300 or r.hm.iloc[0]!=930: continue
    H,L=on.High.max(),on.Low.min(); mid=(H+L)/2; O=r.Open.iloc[0]; dist=abs(O-mid)
    if dist/O<0.0015: continue
    up=mid>O; h,l,c=r.High.values,r.Low.values,r.Close.values; n=len(r); e11=int((r.hm<=1059).sum())
    lv={'mid':mid,'3/8':L+(H-L)*3/8 if up else H-(H-L)*3/8,'5/8':L+(H-L)*5/8 if up else H-(H-L)*5/8,'mirror':O-(mid-O)}
    rec=dict(day=d,year=d.year)
    for name,v in lv.items():
        fa=O>v
        if abs(O-v)<1: continue
        m=(l<=v) if fa else (h>=v)
        if not m.any(): continue
        i=int(np.argmax(m)); dr=1 if fa else -1; k=0.5*dist
        S=v-dr*k
        # the touch bar itself may also hit the stop: conservative -> start race at touch bar for stop, next bar for target
        if (fa and l[i]<=S) or ((not fa) and h[i]>=S): R1=R2=-1-COST/k if False else -1-1.0/k
        else:
            R1=race(h,l,c,i+1,v,v+dr*k,S,dr,n); R2=race(h,l,c,i+1,v,v+dr*2*k,S,dr,n)
        rec[f'{name}_dr']=dr; rec[f'{name}_1R']=R1; rec[f'{name}_2R']=R2; rec[f'{name}_by11']=i<e11
    rows.append(rec)
D=pd.DataFrame(rows); D['split']=np.where(D.year>=2025,'test','train')
def s(v): v=v.dropna(); return f"{v.mean():+.3f}R win {100*(v>0).mean():.0f}% n{len(v)}" if len(v) else '-'
for name in ['mid','3/8','5/8','mirror']:
    for t in ['1R','2R']:
        out=[]
        for sp in ['train','test']:
            Z=D[(D.split==sp)&D[f'{name}_{t}'].notna()]
            out.append(f"{sp} LONG {s(Z[Z[f'{name}_dr']>0][f'{name}_{t}'])} | SHORT {s(Z[Z[f'{name}_dr']<0][f'{name}_{t}'])}")
        print(f"{name:6s} {t}  "+'  ||  '.join(out))
