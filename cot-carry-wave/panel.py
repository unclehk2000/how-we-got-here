"""Weekly price + COT panel for NQ/ES/YM/RTY.
Price: Barchart weekly export if present in uploads (preferred), else built from 1-min files.
Week bar = Sunday 18:00 ET open -> Friday close.  Target for COT report dated Tue of week t is week t+1
(release Fri 15:30 ET of week t), shifted one more week if a federal holiday delays release."""
import pandas as pd, numpy as np, glob, re, os
from pandas.tseries.holiday import USFederalHolidayCalendar
from weekly_px import adjusted
UP='/mnt/user-data/uploads'
COT='/mnt/user-data/outputs/COT_TFF_NQ_ES_RTY_YM_2015_2026.csv'

def _minute_frames(mkt):
    fs=[]
    for f in sorted(glob.glob(f'{UP}/{mkt}_*1min_continuous.csv')):
        d=pd.read_csv(f); d=d[d.Time.astype(str).str.match(r'^\d\d:\d\d$')]
        d['ts']=pd.to_datetime(d.Date+' '+d.Time); fs.append(d[['ts','Open','Close','Volume','Contract']])
    for f in sorted(glob.glob(f'{UP}/{mkt.lower()}[hmuz]2[0-9]_intraday-1min*.csv')):
        d=pd.read_csv(f); d=d[d.Time.astype(str).str.match(r'^\d{4}-')]
        d['ts']=pd.to_datetime(d.Time); d['Close']=d.Latest
        d['Contract']=os.path.basename(f)[:5].upper(); fs.append(d[['ts','Open','Close','Volume','Contract']])
    d=pd.concat(fs).drop_duplicates(['Contract','ts'])
    d['ts']=d.ts+pd.Timedelta(hours=1)                      # CT -> ET
    d['tday']=(d.ts+pd.Timedelta(hours=6)).dt.normalize()   # 18:00 ET starts next trading day
    return d.sort_values('ts')

def daily_from_minutes(mkt):
    d=_minute_frames(mkt)
    v=d.groupby(['tday','Contract']).Volume.sum().reset_index().sort_values('Volume').drop_duplicates('tday',keep='last')
    d=d.merge(v[['tday','Contract']],on=['tday','Contract'])
    g=d.groupby('tday')
    day=pd.DataFrame({'open':g.Open.first(),'close':g.Close.last(),'ctr':g.Contract.first(),'nbars':g.size()})
    return day[day.nbars>=300]                              # drop stub sessions

def weekly_from_minutes(mkt):
    day=daily_from_minutes(mkt)
    # split into contiguous blocks so data gaps never become fake returns
    blk=(day.index.to_series().diff().dt.days>5).cumsum()
    out=[]
    for _,b in day.groupby(blk):
        a=adjusted(b); a['wk']=a.index.to_period('W-FRI'); g=a.groupby('wk')
        w=pd.DataFrame({'P_open':g.P_open.first(),'P_close':g.P_close.last(),'ndays':g.size(),
                        'close_raw':g.close.last()})
        w['ret']=w.P_close/w.P_open-1
        out.append(w.iloc[1:])                               # first week of a block has no prior close
    w=pd.concat(out); return w[w.ndays>=4][['ret','ndays','close_raw']]

def weekly_from_barchart(path):
    d=pd.read_csv(path); d=d[d.iloc[:,0].astype(str).str.match(r'^\d{4}-')]
    t=pd.to_datetime(d.iloc[:,0].astype(str).str[:10])
    c='Latest' if 'Latest' in d else 'Close'
    w=pd.DataFrame({'open':d.Open.astype(float).values,'close':d[c].astype(float).values},index=(t+pd.Timedelta(days=4)).dt.to_period('W-FRI'))
    w=w.sort_index(); w['ret']=w.close/w.open-1; w['close_raw']=w.close; w['ndays']=5
    return w[['ret','ndays','close_raw']]

def weekly(mkt):
    for pat in [f'{UP}/*{mkt.lower()}*weekly*.csv',f'{UP}/*{mkt.upper()}*weekly*.csv']:
        hits=[f for f in glob.glob(pat) if not re.search(r'nq[hmuz]2[0-9]_weekly',os.path.basename(f))]
        if hits: return weekly_from_barchart(sorted(hits)[-1]),'barchart'
    if glob.glob(f'{UP}/{mkt}_*1min_continuous.csv'): return weekly_from_minutes(mkt),'1min'
    return None,None

FED=lambda y:[pd.Timestamp(x) for x in USFederalHolidayCalendar().holidays(f'{y}-01-01',f'{y}-12-31')]
def cot(mkt):
    c=pd.read_csv(COT,parse_dates=['report_date']); c=c[c.market==mkt].sort_values('report_date').copy()
    c['am_net']=(c.am_long-c.am_short)/c.open_interest*100
    c['lev_net']=(c.lev_long-c.lev_short)/c.open_interest*100
    hol=set(sum([FED(y) for y in range(2014,2028)],[]))
    rel=[]
    for r in c.report_date:
        fri=r+pd.Timedelta(days=3)
        delayed=any((r+pd.Timedelta(days=k)) in hol for k in range(-1,4))
        shut=pd.Timestamp('2025-09-30')<=r<=pd.Timestamp('2025-12-31')
        rel.append(pd.NaT if shut else (fri+pd.Timedelta(days=3) if delayed else fri))
    c['release']=rel
    c['first_week']=[None if pd.isna(x) else ((x+pd.Timedelta(days=2)).to_period('W-FRI') if x.weekday()==4
                      else x.to_period('W-FRI')+1) for x in c.release]   # first week that opens after the release
    return c

if __name__=='__main__':
    for m in ['NQ','ES','YM','RTY']:
        w,src=weekly(m)
        if w is None: print(m,'no price data'); continue
        print(m,src,len(w),w.index.min(),w.index.max(),'mean %.3f%% up %.1f%%'%(100*w.ret.mean(),100*(w.ret>0).mean()))
    print(cot('NQ').tail(3)[['report_date','release','first_week','am_net','lev_net']])
