"""SRC25 claims on NQ: sessions Asia 18:00-01:59, London 02:00-07:59, NY 08:00-16:59 (ET). Train 2018-24 / test 2025-26.
Regime = London vs Asia H/L. NY bullish (close>open) by regime vs all days (carry baseline).
London 25% (of the London body, from the close): bull London -> does NY stay above / wick below and close back above;
bear London mirror. Also ladder reach by 11:00 for Bankai mode."""
import pandas as pd, numpy as np
b=pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts'); G={d:x for d,x in b.groupby('tday')}
def seg(x,a,z): return x[(x.hm>=a)&(x.hm<=z)]
rows=[]
for d,x in G.items():
    A=x[(x.hm>=1800)|(x.hm<=159)]; Lo=seg(x,200,759); N=seg(x,800,1659)
    if len(A)<300 or len(Lo)<300 or len(N)<400: continue
    ah,al=A.High.max(),A.Low.min(); lh,ll=Lo.High.max(),Lo.Low.min(); lo,lc=Lo.Open.iloc[0],Lo.Close.iloc[-1]
    no,nc,nh,nl=N.Open.iloc[0],N.Close.iloc[-1],N.High.max(),N.Low.min()
    reg=('London Engulfs Asia' if lh>ah and ll<al else 'Asia Engulfs London' if ah>=lh and al<=ll else
         'London Partial Up' if lh>ah else 'London Partial Down' if ll<al else 'Inside')
    bt,bb=max(lo,lc),min(lo,lc); bull=lc>lo; br=bt-bb
    l25=(bt-0.25*br) if bull else (bb+0.25*br)
    rec=dict(day=d,year=d.year,reg=reg,ny_bull=nc>no,lon_bull=bull,
             Ltaken=nh>=lh,Lltaken=nl<=ll)
    if br>0:
        if bull: rec.update(stay=nl>=l25, wick_back=(nl<l25) and (nc>l25), wick_fail=(nl<l25) and (nc<=l25))
        else:    rec.update(stay=nh<=l25, wick_back=(nh>l25) and (nc<l25), wick_fail=(nh>l25) and (nc>=l25))
    rows.append(rec)
D=pd.DataFrame(rows); D['split']=np.where(D.year>=2025,'test','train')
pd.set_option('display.width',200)
print('NY (08:00-16:59) bullish by regime:')
g=D.groupby(['reg','split']).ny_bull.agg(['mean','size']).unstack('split'); print(g.round(3))
print('all days:',D.groupby('split').ny_bull.mean().round(3).to_dict())
print('\nLondon 25% behaviour (NY session) by London candle direction:')
print(D.groupby(['lon_bull','split'])[['stay','wick_back','wick_fail']].mean().round(3))
# ladder by 11:00 from the earlier re-test frame
S=pd.read_pickle('/home/claude/sb/D.pkl')
