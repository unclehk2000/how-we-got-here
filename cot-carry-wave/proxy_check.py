import pandas as pd, numpy as np
d=pd.read_pickle('legacy_nq.pkl')
t=pd.read_csv('/mnt/user-data/outputs/COT_NQ_TFF_2015_2026.csv',parse_dates=['report_date']).sort_values('report_date')
t['am_net']=t.am_long-t.am_short; t['lev_net']=t.lev_long-t.lev_short; t['np_net']=-(t.am_net+t.lev_net)
d['comm_net']=d.comm_positions_long_all-d.comm_positions_short_all
d['nc_net']=d.noncomm_positions_long_all-d.noncomm_positions_short_all
d['nr_net']=d.nonrept_positions_long_all-d.nonrept_positions_short_all
def idx(s,n=26): lo=s.rolling(n).min(); hi=s.rolling(n).max(); return (s-lo)/(hi-lo)
for c in ['am_net','lev_net','np_net']: t[c+'_i']=idx(t[c])
d['seg']=(d.date.diff().dt.days>9).cumsum()
for c in ['comm_net','nc_net','nr_net']: d[c+'_i']=d.groupby('seg')[c].transform(idx)
m=d.merge(t,left_on='date',right_on='report_date')
print('levels corr: comm~AM %.2f  noncomm~Lev %.2f  nonrept~-(AM+Lev) %.2f'%(m.comm_net.corr(m.am_net),m.nc_net.corr(m.lev_net),m.nr_net.corr(m.np_net)))
print('weekly-change corr: comm~AM %.2f noncomm~Lev %.2f'%(m.comm_net.diff().corr(m.am_net.diff()),m.nc_net.diff().corr(m.lev_net.diff())))
v=m.dropna(subset=['comm_net_i','am_net_i'])
print('n index weeks',len(v))
print('index corr: comm %.2f noncomm %.2f nonrept %.2f'%(v.comm_net_i.corr(v.am_net_i),v.nc_net_i.corr(v.lev_net_i),v.nr_net_i.corr(v.np_net_i)))
for a,b,name in [('comm_net_i','am_net_i','comm>0.7'),('nc_net_i','lev_net_i','noncomm>0.7')]:
    x=v[a]>0.7; y=v[b]>0.7
    print(name,'legacy',x.sum(),'proxy',y.sum(),'both',(x&y).sum())
for a,b,name in [('comm_net_i','am_net_i','comm<0.3'),('nc_net_i','lev_net_i','noncomm<0.3')]:
    x=v[a]<0.3; y=v[b]<0.3
    print(name,'legacy',x.sum(),'proxy',y.sum(),'both',(x&y).sum())
print('comm long/OI legacy mean %.2f  AM long/OI %.2f'%((m.comm_positions_long_all/m.open_interest_all).mean(),(m.am_long/m.open_interest).mean()))
print('comm short/OI legacy mean %.2f min %.2f  AM short/OI %.2f'%((m.comm_positions_short_all/m.open_interest_all).mean(),(m.comm_positions_short_all/m.open_interest_all).min(),(m.am_short/m.open_interest).mean()))
