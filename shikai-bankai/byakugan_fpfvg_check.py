"""Byakugan sanity check + first presented FVG (09:30) on NQ 1-min, 2018 + 2022-26. Train 2018-24 / test 2025-26.
Byakugan: 07:00-08:59 range; raw bias = 09:30 open vs range midpoint; day close = 16:59 bar close (no RTH).
Key question: is 'AL extreme swept in the 0.30-1.00% zone -> 76-81% accuracy' a signal, or just
'price already moved that far in the bias direction'? Placebo = any level the same % distance from the open in the bias direction."""
import pandas as pd, numpy as np
b=pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts'); G={d:x for d,x in b.groupby('tday')}
def seg(x,a,z): return x[(x.hm>=a)&(x.hm<=z)]
rows=[]
for d,x in G.items():
    pre=seg(x,700,859); ny=seg(x,930,1659); A=x[(x.hm>=2000)|(x.hm<=0)]; Lo=seg(x,200,459); bf=seg(x,500,929)
    if len(pre)<100 or len(ny)<300 or ny.hm.iloc[0]!=930 or len(A)<100 or len(Lo)<100: continue
    H,L=pre.High.max(),pre.Low.min(); mid=(H+L)/2; O=ny.Open.iloc[0]; C=ny.Close.iloc[-1]
    bull=O>mid
    alH=max(A.High.max(),Lo.High.max()); alL=min(A.Low.min(),Lo.Low.min())
    lvl=alH if bull else alL
    pre_swept = (x[(x.hm>=459)|(x.hm<=929)].High.max()>=alH) if bull else (x[(x.hm>=459)|(x.hm<=929)].Low.min()<=alL)
    # simpler: swept between London end and 09:29
    pre_swept = (seg(x,500,929).High.max()>=alH) if bull else (seg(x,500,929).Low.min()<=alL)
    dist=abs(lvl-O)/O*100
    sw = (ny.High.max()>=lvl) if bull else (ny.Low.min()<=lvl)
    acc = (C>O) if bull else (C<O)
    # placebo: price reached the same distance in the bias direction (from the open), whatever the level
    rec=dict(day=d,year=d.year,bull=bull,dist=dist,pre_swept=pre_swept,sw=sw,acc=acc,
             tapH=(ny.High.max()>=H),tapL=(ny.Low.min()<=L),
             tap_bias=(ny.High.max()>=H) if bull else (ny.Low.min()<=L),
             tap_other=(ny.Low.min()<=L) if bull else (ny.High.max()>=H),
             r79=(H-L)/O*100, rday=(ny.High.max()-ny.Low.min())/O*100)
    # first presented FVG after 09:30 (completes by 10:00), 1-min, wick-based
    h,l,c,o=ny.High.values,ny.Low.values,ny.Close.values,ny.Open.values; fp=None
    for i in range(2,min(31,len(ny))):
        if l[i]>h[i-2]: fp=(1,i,h[i-2],l[i]); break
        if h[i]<l[i-2]: fp=(-1,i,h[i],l[i-2]); break
    if fp:
        s,i,bot,top=fp; ce=(top+bot)/2
        rec.update(fp=s,fp_i=i,fp_acc=(C>O) if s>0 else (C<O),
                   fp_ce_ret=((l[i+1:]<=ce).any() if s>0 else (h[i+1:]>=ce).any()),
                   fp_inv=((c[i+1:]<bot).any() if s>0 else (c[i+1:]>top).any()))
    rows.append(rec)
D=pd.DataFrame(rows); D['split']=np.where(D.year>=2025,'test','train')
D.to_pickle('/home/claude/byk/D.pkl')
def r(v): v=v.dropna().astype(float); return f"{100*v.mean():.1f}% (n{len(v)})"
print('days',len(D))
for sp in ['train','test']:
    Z=D[D.split==sp]
    print(f"\n[{sp}] raw bias -> 16:59 close: all {r(Z.acc)} | bull {r(Z[Z.bull].acc)} | bear {r(Z[~Z.bull].acc)} | always-long base {r((Z.acc==Z.bull))}")
    print(f"  NY taps the 7-9 extreme on the bias side {r(Z.tap_bias)} vs the other side {r(Z.tap_other)}")
    Q=Z[~Z.pre_swept]
    for lo,hi in [(0,.15),(.15,.30),(.30,.50),(.50,1.0)]:
        q=Q[(Q.dist>=lo)&(Q.dist<hi)]
        print(f"  AL dist {lo:.2f}-{hi:.2f}%: swept {r(q.sw)} | acc if swept {r(q[q.sw].acc)} | acc if not {r(q[~q.sw].acc)}")
# placebo for the 'if swept' accuracy: P(close in bias dir | price reached >= dist% in bias direction), ALL days
print('\nPlacebo: P(close on bias side | NY reached at least X% from the open on that side), any level')
for lo,hi in [(.30,.50),(.50,1.0)]:
    out=[]
    for sp in ['train','test']:
        Z=D[D.split==sp]; hits=[];
        for _,q in Z.iterrows():
            pass
    print('  (computed below)')
