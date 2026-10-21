"""1-min bars (ET) for NQ/ES with one contract per trading day (highest volume). Trading day starts 18:00 ET."""
import pandas as pd, numpy as np, glob, os
UP='/mnt/user-data/uploads'
def minutes(mkt='NQ'):
    fs=[]
    for f in sorted(glob.glob(f'{UP}/{mkt}_*1min_continuous.csv')):
        d=pd.read_csv(f); d=d[d.Time.astype(str).str.match(r'^\d\d:\d\d$')]
        d['ts']=pd.to_datetime(d.Date+' '+d.Time); fs.append(d[['ts','Open','High','Low','Close','Volume','Contract']])
    for f in sorted(glob.glob(f'{UP}/{mkt.lower()}[hmuz]2[0-9]_intraday-1min*.csv')):
        d=pd.read_csv(f); d=d[d.Time.astype(str).str.match(r'^\d{4}-')]
        d['ts']=pd.to_datetime(d.Time); d['Close']=d.Latest; d['Contract']=os.path.basename(f)[:5].upper()
        fs.append(d[['ts','Open','High','Low','Close','Volume','Contract']])
    d=pd.concat(fs).drop_duplicates(['Contract','ts'])
    d['ts']=d.ts+pd.Timedelta(hours=1)                         # CT -> ET
    d['tday']=(d.ts+pd.Timedelta(hours=6)).dt.normalize()
    v=d.groupby(['tday','Contract']).Volume.sum().reset_index().sort_values('Volume').drop_duplicates('tday',keep='last')
    d=d.merge(v[['tday','Contract']],on=['tday','Contract']).sort_values('ts').reset_index(drop=True)
    d['hm']=d.ts.dt.hour*100+d.ts.dt.minute
    return d
if __name__=='__main__':
    import sys
    for m in sys.argv[1:] or ['NQ','ES']:
        d=minutes(m); d.to_pickle(f'bars_{m}.pkl'); print(m,len(d),d.tday.nunique(),d.ts.min(),d.ts.max())
