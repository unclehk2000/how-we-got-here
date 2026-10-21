"""Dreesmann, Herberger & Charifzadeh (2023) CoT short-term reversal strategy, run on NQ.
Legacy futures-only COT (code 209742) + roll-adjusted weekly prices from the 1-min files."""
import pandas as pd, numpy as np, sys
from legacy_load import load
from weekly_px import daily, adjusted, weekly

def legacy_series():
    d=load()[['date','open_interest_all','comm_positions_long_all','comm_positions_short_all',
              'noncomm_positions_long_all','noncomm_positions_short_all']]
    d.columns=['date','oi','cl','cs','nl','ns']
    j=pd.read_csv('j2017.csv',names=['id','oi','cl','cs','nl','ns'])          # 2017-Q4, verified vs TFF OI + 2018-01-02 change fields
    j['date']=pd.to_datetime(j.id.str[:6],format='%y%m%d')
    d=pd.concat([j.drop(columns='id'),d]).sort_values('date').drop_duplicates('date').reset_index(drop=True)
    d['comm']=d.cl-d.cs; d['nonc']=d.nl-d.ns; d['nrep']=-(d.comm+d.nonc)      # legacy nets sum to zero
    d['seg']=(d.date.diff().dt.days>9).cumsum()
    def idx(s,n=26): lo=s.rolling(n).min(); hi=s.rolling(n).max(); return (s-lo)/(hi-lo)
    for c in ['comm','nonc','nrep']: d[c+'_i']=d.groupby('seg')[c].transform(idx)
    d['cl_oi']=d.cl/d.oi; d['cs_oi']=d.cs/d.oi
    d['wk']=d.date.dt.to_period('W-FRI')
    return d

def run(w,hi=0.7,lo=0.3,oi_min=0.30,lag=0,cost=0.002,long_short=True):
    w=w.copy()
    for c in ['comm_i','nonc_i','nrep_i','cl_oi','cs_oi']: w[c]=w[c].shift(lag)
    up=w.sma>w.sma.shift(); dn=w.sma<w.sma.shift()
    pos=0; P=[]; trades=[]
    for i in range(len(w)):
        r=w.iloc[i]; valid=not np.isnan(r.comm_i) and not np.isnan(r.sma) and not np.isnan(w.sma.iloc[i-1] if i else np.nan)
        if valid:
            if pos==1 and r.nonc_i>hi and dn.iloc[i]: pos=0; trades[-1]['exit']=w.index[i]
            elif pos==-1 and r.nonc_i<lo and up.iloc[i]: pos=0; trades[-1]['exit']=w.index[i]
            if pos==0:
                if r.comm_i>hi and r.cl_oi>=oi_min and r.nrep_i<lo and up.iloc[i]: pos=1; trades.append({'side':1,'sig':w.index[i]})
                elif long_short and r.comm_i<lo and r.cs_oi>=oi_min and r.nrep_i>hi and dn.iloc[i]: pos=-1; trades.append({'side':-1,'sig':w.index[i]})
        P.append(pos)                          # decided at this week's close -> held from next week's open
    w['pos']=pd.Series(P,index=w.index).shift().fillna(0)
    ret=w.P_open.shift(-1)/w.P_open-1; ret.iloc[-1]=w.P_close.iloc[-1]/w.P_open.iloc[-1]-1
    turn=w.pos.diff().abs().fillna(w.pos.abs())
    w['strat']=w.pos*ret-turn*cost; w['bh']=ret
    return w,trades

if __name__=='__main__':
    c=legacy_series()
    px=weekly(adjusted(daily('/mnt/user-data/uploads/NQ_2018_1min_continuous.csv')))
    px['sma']=px.P_close.rolling(10).mean()
    w=px.join(c.set_index('wk')[['date','comm_i','nonc_i','nrep_i','cl_oi','cs_oi']],how='left')
    live=w.comm_i.notna()&w.sma.notna()&w.sma.shift().notna()
    print('tradeable weeks',live.sum(),w.index[live][0],'->',w.index[live][-1])
    ww=w[live.cummax()]
    print('condition frequency over tradeable weeks:')
    up=(w.sma>w.sma.shift())[live]
    L=w[live]
    print(' comm_i>0.7 %d  cl/OI>=0.30 %d  nrep_i<0.3 %d  SMA up %d  -> all four %d'%((L.comm_i>.7).sum(),(L.cl_oi>=.3).sum(),(L.nrep_i<.3).sum(),up.sum(),((L.comm_i>.7)&(L.cl_oi>=.3)&(L.nrep_i<.3)&up).sum()))
    dn=(w.sma<w.sma.shift())[live]
    print(' comm_i<0.3 %d  cs/OI>=0.30 %d  nrep_i>0.7 %d  SMA dn %d  -> all four %d'%((L.comm_i<.3).sum(),(L.cs_oi>=.3).sum(),(L.nrep_i>.7).sum(),dn.sum(),((L.comm_i<.3)&(L.cs_oi>=.3)&(L.nrep_i>.7)&dn).sum()))
    print('corr comm_i vs nrep_i %.2f'%L.comm_i.corr(L.nrep_i))
    for ls in [False,True]:
        for cost in [0.002,0.0001]:
            r,t=run(ww,cost=cost,long_short=ls)
            print(('L/S ' if ls else 'Long'),'cost %.2f%%'%(cost*100),'strategy %+.2f%%'%(100*((1+r.strat).prod()-1)),'always-long %+.2f%%'%(100*((1+r.bh).prod()-1)),'weeks in market',int((r.pos!=0).sum()),'trades',t)
    ww.to_pickle('nq2018_weekly.pkl')
