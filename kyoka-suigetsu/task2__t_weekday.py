import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np
from scipy import stats
W=['Mon','Tue','Wed','Thu','Fri']
out=[]
for s in ['NQ','ES','RTY']:
    D=pd.read_pickle(f'F_{s}.pkl')
    D=D[(D.rvol>0.4)|D.rvol.isna()]          # drop abbreviated holiday sessions
    D['nrm']=D.rng/D.atr14                    # range relative to the prior 14-day ATR
    print(f'\n== {s} weekday range (median of range / prior ATR14, ×all-days) ==')
    per={'2010-17':(2010,2017),'2018-24':(2018,2024),'2025-26':(2025,2026),'2010-26':(2010,2026)}
    rows={}
    for k,(a,b) in per.items():
        d=D[(D.year>=a)&(D.year<=b)].dropna(subset=['nrm'])
        m=d.nrm.median()
        rows[k]=[d[d.dow==i].nrm.median()/m for i in range(5)]
    T=pd.DataFrame(rows,index=W).round(3); print(T.to_string())
    # per-year: ratio of each weekday's median normalised range to the year's median
    Y=D.dropna(subset=['nrm']).groupby(['year','dow']).nrm.median().unstack()
    Y=Y.div(D.dropna(subset=['nrm']).groupby('year').nrm.median(),axis=0)
    print('years where weekday > all-days median:', {W[i]:int((Y[i]>1).sum()) for i in range(5)}, 'of',len(Y))
    # Kruskal across weekdays within each period
    for k,(a,b) in per.items():
        d=D[(D.year>=a)&(D.year<=b)].dropna(subset=['nrm'])
        h,p=stats.kruskal(*[d[d.dow==i].nrm for i in range(5)])
        print(f'  Kruskal {k}: p={p:.2g}')
    # out-of-sample usefulness: forecast log range = log(median of last 20 ranges) [+ log weekday mult from train]
    D['base']=np.log(D.rng.rolling(20).median().shift(1))
    tr=D[(D.year<=2017)].dropna(subset=['nrm']); m=tr.nrm.median()
    mult={i:np.log(tr[tr.dow==i].nrm.median()/m) for i in range(5)}
    te=D[D.year>=2018].dropna(subset=['base'])
    e0=(te.lr-te.base); e1=(te.lr-(te.base+te.dow.map(mult)))
    # optimal intercept from train to be fair
    c0=(tr.lr-tr.base).dropna().mean() if 'base' in tr else 0
    tr2=D[D.year<=2017].dropna(subset=['base']); c0=(tr2.lr-tr2.base).mean(); c1=(tr2.lr-tr2.base-tr2.dow.map(mult)).mean()
    mae0=(e0-c0).abs().mean(); mae1=(e1-c1).abs().mean()
    dm=stats.ttest_rel((e0-c0).abs(),(e1-c1).abs())
    print(f'  OOS 2018-26 MAE log-range: trailing median {mae0:.4f} | + weekday mult {mae1:.4f} | improvement {100*(mae0-mae1)/mae0:.2f}%  p={dm.pvalue:.2g}')
