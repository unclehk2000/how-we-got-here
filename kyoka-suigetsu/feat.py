import pandas as pd, numpy as np
from load import third_friday

def holidays_from_calendar(idx):
    # business days (Mon-Fri) missing from the CME calendar = exchange holidays / closures
    bd=pd.bdate_range(idx.min(),idx.max())
    return bd.difference(idx)

def make(sym, cal=None):
    D=pd.read_pickle(f'/home/claude/t2/D_{sym}.pkl')
    D=D[D.index>='2010-01-01'].copy()
    if cal is not None: D=D[D.index.isin(cal)]
    D['rng']=(D.h-D.l)/D.o*100
    D['net']=(D.c-D.o)/D.o*100
    D['ret']=D.ac.pct_change()*100          # close-to-close, roll-free
    pc=D.ac.shift(1)
    D['tr']=np.maximum(D.ah,pc)-np.minimum(D.al,pc)
    D['trp']=D.tr/D.o.shift(0)*100
    D['atr14']=D.tr.rolling(14).mean().shift(1)/D.o*100   # known before the day starts
    D['lr']=np.log(D.rng)
    D['dow']=D.index.dayofweek   # 0=Mon
    D['mon']=D.index.month
    D['year']=D.index.year
    ym=D.index.to_period('M')
    D['tdom']=D.groupby(ym).cumcount()+1
    D['tdom_rev']=D.groupby(ym).cumcount(ascending=False)+1
    D['tom']=((D.tdom_rev==1)|(D.tdom<=3)).astype(int)
    # options expiry: 3rd Friday of each month; week containing it (Mon..Fri)
    tf=pd.Series([third_friday(d.year,d.month) for d in D.index],index=D.index)
    wk_start=D.index-pd.to_timedelta(D.index.dayofweek,unit='D')
    D['opex_week']=((tf>=wk_start)&(tf<=wk_start+pd.Timedelta(days=4))).astype(int)
    D['opex_day']=(D.index==tf).astype(int)
    D['qopex_week']=(D.opex_week.astype(bool)&D.mon.isin([3,6,9,12])).astype(int)
    D['qopex_day']=(D.opex_day.astype(bool)&D.mon.isin([3,6,9,12])).astype(int)
    # roll week: week containing the roll date (8 calendar days before quarterly 3rd Friday = Thursday of prior week)
    rd=pd.Series([third_friday(d.year,d.month)-pd.Timedelta(days=8) if d.month in (3,6,9,12) else pd.NaT for d in D.index],index=D.index)
    D['roll_week']=((rd>=wk_start)&(rd<=wk_start+pd.Timedelta(days=4))).astype(int)
    # holidays
    hol=holidays_from_calendar(D.index)
    nxt=pd.Series(D.index[1:].tolist()+[pd.NaT],index=D.index)
    prv=pd.Series([pd.NaT]+D.index[:-1].tolist(),index=D.index)
    D['pre_hol']=[int(((h>d)&(h<n)).any()) if pd.notna(n) else 0 for d,n in zip(D.index,nxt) for h in [hol]]
    D['post_hol']=[int(((h>p)&(h<d)).any()) if pd.notna(p) else 0 for d,p in zip(D.index,prv) for h in [hol]]
    # carry: annualised log spread next vs front, using settlements
    T=(D.exp_next-D.exp_front).dt.days/365.0
    D['carry']=np.log(D.next_c/D.c)/T*100
    D['dte']=(D.exp_front-D.index.to_series()).dt.days
    # volume / OI context (known at the close of the prior day)
    D.loc[D.vol_tot<=0,'vol_tot']=np.nan; D.loc[D.oi_tot<=0,'oi_tot']=np.nan
    D['rvol']=(D.vol_tot/D.vol_tot.rolling(20,min_periods=15).mean())
    D['doi']=D.oi_tot.pct_change(5)*100
    return D

if __name__=='__main__':
    cal=pd.read_pickle('/home/claude/t2/D_ES.pkl').index
    for s in ['NQ','ES','RTY']:
        D=make(s,cal); D.to_pickle(f'/home/claude/t2/F_{s}.pkl')
        print(s,len(D),D.index.min().date(),D.index.max().date())
        print(D[['rng','atr14','carry','dte','rvol','doi']].describe().round(3).T)
        print('flags',D[['tom','opex_week','opex_day','qopex_week','qopex_day','roll_week','pre_hol','post_hol']].sum().to_dict())
