"""NQ 2023-2026: roll-adjusted daily + weekly futures returns, implied-carry path, COT at release timing."""
import pandas as pd, numpy as np
from panel import daily_from_minutes, cot
from weekly_px import adjusted

# Effective fed funds path (FOMC decision days, effective next day). 2026: held at the Dec-2025 level (assumption, see doc).
EFFR=[('2022-12-15',4.33),('2023-02-02',4.58),('2023-03-23',4.83),('2023-05-04',5.08),('2023-07-27',5.33),
      ('2024-09-19',4.83),('2024-11-08',4.58),('2024-12-19',4.33),('2025-09-18',4.09),('2025-10-30',3.87),('2025-12-11',3.64)]
DIV=0.70          # Nasdaq-100 dividend yield, %
SPREAD=0.76       # equity-financing spread over EFFR, calibrated so the path matches implied carry measured from
                  # NQH26/NQM26 (3.48%, 13 Mar 2026) and NQM26/NQU26 (3.90%, 10-17 Jun 2026)
def carry_path(idx):
    s=pd.Series({pd.Timestamp(d):v for d,v in EFFR}).sort_index()
    e=s.reindex(s.index.union(idx)).ffill().reindex(idx)
    return (e-DIV+SPREAD)/100          # annual implied carry c = r - q (decimal)

def daily():
    d=daily_from_minutes('NQ'); d=d[d.index>='2023-01-01']
    blk=(d.index.to_series().diff().dt.days>5).cumsum()
    out=[]
    for _,b in d.groupby(blk):
        a=adjusted(b); a['r']=a.P_close.pct_change(); out.append(a.iloc[1:])
    d=pd.concat(out)
    d['carry']=carry_path(d.index)
    return d

def weekly(d=None):
    d=daily() if d is None else d
    d=d.copy(); d['wk']=d.index.to_period('W-FRI')
    g=d.groupby('wk')
    w=pd.DataFrame({'r_fut':g.r.apply(lambda x:(1+x).prod()-1),'n':g.size(),'carry':g.carry.last(),
                    'rv':g.r.apply(lambda x:np.sqrt((x**2).sum())),'last_day':g.apply(lambda x:x.index[-1]),
                    'ctr':g.ctr.last()})
    w=w[w.n>=4]
    full=pd.period_range(w.index.min(),w.index.max(),freq='W-FRI'); w=w.reindex(full)
    w['dt']=w.n*(7/5)/365                                   # calendar time covered (trading days -> calendar)
    w['bleed']=w.carry*w.dt                                 # carry the futures gives up converging to spot
    w['r_spot']=w.r_fut+w.bleed                             # carry-adjusted (spot-equivalent) return
    # roll week = week in which the front contract changes (Mar/Jun/Sep/Dec expiry week)
    prev=w.ctr.ffill().shift()
    w['roll_wk']=((w.ctr!=prev)&prev.notna()).astype(float).where(w.ctr.notna())
    return w

def cot_features():
    c=cot('NQ').set_index('report_date')
    f=pd.DataFrame(index=c.index)
    f['am']=c.am_net; f['lev']=c.lev_net
    f['am_d1']=f.am.diff(); f['lev_d1']=f.lev.diff(); f['am_d4']=f.am.diff(4); f['lev_d4']=f.lev.diff(4)
    f['am_z52']=(f.am-f.am.rolling(52).mean())/f.am.rolling(52).std()
    f['lev_z52']=(f.lev-f.lev.rolling(52).mean())/f.lev.rolling(52).std()
    f['oi_chg']=np.log(c.open_interest).diff(4)
    f['first_week']=c.first_week.values
    f=f[f.first_week.notna()]
    f.index=pd.PeriodIndex(f.pop('first_week'),freq='W-FRI'); f=f[~f.index.duplicated(keep='last')]
    return f

if __name__=='__main__':
    d=daily(); w=weekly(d)
    print('daily',len(d),d.index.min().date(),d.index.max().date(),'| weekly with data',w.r_fut.notna().sum())
    print('carry path (annual %): ', (100*w.carry.groupby(w.index.year).mean()).round(2).to_dict())
    print('mean weekly: futures %.3f%%  spot-equiv %.3f%%  bleed %.3f%%'%(100*w.r_fut.mean(),100*w.r_spot.mean(),100*w.bleed.mean()))
    print('roll weeks',int(w.roll_wk.sum()))
    d.to_pickle('daily.pkl'); w.to_pickle('weekly.pkl'); cot_features().to_pickle('cotf.pkl')
