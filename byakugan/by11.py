import pandas as pd, numpy as np
b=pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
def seg(x,a,z): return x[(x.hm>=a)&(x.hm<=z)]
rows=[]
for d,x in b.groupby('tday'):
    pre=seg(x,700,859); ny=seg(x,930,1659); am=seg(x,930,1059)
    if len(pre)<100 or len(ny)<300 or ny.hm.iloc[0]!=930 or len(am)<80: continue
    H,L=pre.High.max(),pre.Low.min(); mid=(H+L)/2; O=ny.Open.iloc[0]; bull=O>mid
    rec=dict(year=d.year,
        tb_day=(ny.High.max()>=H) if bull else (ny.Low.min()<=L), to_day=(ny.Low.min()<=L) if bull else (ny.High.max()>=H),
        tb_11=(am.High.max()>=H) if bull else (am.Low.min()<=L), to_11=(am.Low.min()<=L) if bull else (am.High.max()>=H))
    h,l,c=am.High.values,am.Low.values,am.Close.values; fp=None
    for i in range(2,min(31,len(am))):
        if l[i]>h[i-2]: fp=(1,i,h[i-2],l[i]); break
        if h[i]<l[i-2]: fp=(-1,i,h[i],l[i-2]); break
    if fp:
        s,i,bot,top=fp; ce=(top+bot)/2
        rec.update(has=True, ce11=((l[i+1:]<=ce).any() if s>0 else (h[i+1:]>=ce).any()),
                   inv11=((c[i+1:]<bot).any() if s>0 else (c[i+1:]>top).any()))
    else: rec.update(has=False)
    rows.append(rec)
D=pd.DataFrame(rows); D['sp']=np.where(D.year>=2025,'test','train')
for sp in ['train','test']:
    Z=D[D.sp==sp]; F=Z[Z.has]
    print(sp, len(Z), 'FP found', round(100*Z.has.mean(),1),
      '| bias-side tap day/11:', round(100*Z.tb_day.mean(),1), round(100*Z.tb_11.mean(),1),
      '| other day/11:', round(100*Z.to_day.mean(),1), round(100*Z.to_11.mean(),1),
      '| CE by 11', round(100*F.ce11.astype(float).mean(),1), '| far side close-through by 11', round(100*F.inv11.astype(float).mean(),1))
