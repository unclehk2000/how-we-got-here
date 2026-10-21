"""ES 1-min 2018–2022 (Barchart, Central Time, one file per front-month window) -> ET bars with trading day."""
import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np, glob, os
SRC=str(ES_1822_DIR)
fs=[]
for f in sorted(glob.glob(f'{SRC}/ES*.csv')):
    d=pd.read_csv(f); d=d[d.Time.astype(str).str.match(r'^\d{4}-')]
    d['ts']=pd.to_datetime(d.Time); d['Close']=d.Latest.astype(float); d['Contract']=os.path.basename(f)[:5].upper()
    for c in ['Open','High','Low']: d[c]=d[c].astype(float)
    d['Volume']=pd.to_numeric(d.Volume,errors='coerce').fillna(0).astype(int)
    fs.append(d[['ts','Open','High','Low','Close','Volume','Contract']])
    print(os.path.basename(f), len(d), d.ts.min(), d.ts.max())
d=pd.concat(fs)
print('dup ts across files:', d.ts.duplicated().sum())
d=d.sort_values(['ts','Volume']).drop_duplicates('ts',keep='last')
d['ts']=d.ts+pd.Timedelta(hours=1)                       # CT -> ET
d['tday']=(d.ts+pd.Timedelta(hours=6)).dt.normalize()
d['hm']=d.ts.dt.hour*100+d.ts.dt.minute
d=d.sort_values('ts').reset_index(drop=True)
d.to_pickle('bars_ES_1822_raw.pkl')
