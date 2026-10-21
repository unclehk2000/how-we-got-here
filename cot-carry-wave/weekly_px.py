import pandas as pd, numpy as np, sys
def daily(path):
    d=pd.read_csv(path)
    d=d[d.Time.astype(str).str.match(r'^\d\d:\d\d$')]
    ts=pd.to_datetime(d.Date+' '+d.Time)+pd.Timedelta(hours=1)   # CT -> ET
    d=d.assign(ts=ts).sort_values('ts')
    d['tday']=(d.ts+pd.Timedelta(hours=6)).dt.normalize()          # >=18:00 ET -> next day
    # one contract per trading day: highest volume
    v=d.groupby(['tday','Contract']).Volume.sum().reset_index().sort_values('Volume').drop_duplicates('tday',keep='last')
    d=d.merge(v[['tday','Contract']],on=['tday','Contract'])
    g=d.groupby('tday')
    out=pd.DataFrame({'open':g.Open.first(),'close':g.Close.last(),'ctr':g.Contract.first()})
    return out
def adjusted(day):
    day=day.sort_index().copy()
    same=day.ctr.eq(day.ctr.shift())
    rc=np.where(same,day.close/day.close.shift(),day.close/day.open)          # close-to-close, roll day open-to-close
    ro=np.where(same,day.open/day.close.shift(),1.0)                          # overnight gap into today's open
    rc[0]=1; ro[0]=1
    P=np.cumprod(rc); day['P_close']=P
    day['P_open']=np.r_[day.open.iloc[0]/day.close.iloc[0]*P[0], P[:-1]*ro[1:]]
    day['rolled']=~same
    return day
def weekly(day):
    day=day.copy(); day['wk']=day.index.to_period('W-FRI')
    g=day.groupby('wk')
    return pd.DataFrame({'P_open':g.P_open.first(),'P_close':g.P_close.last(),'last_day':g.apply(lambda x:x.index[-1]),'ndays':g.size()})
if __name__=='__main__':
    day=adjusted(daily(sys.argv[1])); w=weekly(day)
    print(day.head(3)); print(w.head()); print(len(day),len(w), day.rolled.sum())
