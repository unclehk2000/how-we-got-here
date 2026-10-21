import pandas as pd, numpy as np, json, glob, os
BASE='/mnt/user-data/uploads/nq_es_rty_daily_task2_1'
PRE={'NQ':'nq','ES':'es','RTY':'qr'}
MCODE={'h':3,'m':6,'u':9,'z':12}

def third_friday(y,m):
    d=pd.Timestamp(y,m,1)
    off=(4-d.weekday())%7
    return d+pd.Timedelta(days=off+14)

def contracts(sym):
    out={}
    for f in sorted(glob.glob(f'{BASE}/per_contract/{sym}/*.csv')):
        code=os.path.basename(f)[:-4]
        m=MCODE[code[2]]; y=2000+int(code[3:])
        df=pd.read_csv(f,parse_dates=['Date']).set_index('Date').sort_index()
        df.attrs['exp']=third_friday(y,m)
        out[code]=df
    return out

def build(sym):
    C=contracts(sym)
    cont=pd.read_csv(f'{BASE}/continuous/{sym}_continuous.csv',parse_dates=['Date']).set_index('Date')
    codes=sorted(C,key=lambda c:C[c].attrs['exp'])
    exps=[C[c].attrs['exp'] for c in codes]
    rows=[]
    allv=pd.concat({c:C[c]['Volume'] for c in codes},axis=1)
    allo=pd.concat({c:C[c]['OpenInterest'] for c in codes},axis=1)
    allc=pd.concat({c:C[c]['Close'] for c in codes},axis=1)
    for dt,r in cont.iterrows():
        f=r['Contract']; i=codes.index(f)
        nx=codes[i+1] if i+1<len(codes) else None
        rows.append(dict(date=dt,contract=f,o=r.Open,h=r.High,l=r.Low,c=r.Close,
            ao=r.AdjOpen,ah=r.AdjHigh,al=r.AdjLow,ac=r.AdjClose,roll=r.IsRollDate,
            vol_front=r.Volume,oi_front=r.OpenInterest,
            next_c=allc.at[dt,nx] if (nx and dt in allc.index) else np.nan,
            exp_front=C[f].attrs['exp'], exp_next=C[nx].attrs['exp'] if nx else pd.NaT))
    D=pd.DataFrame(rows).set_index('date')
    if sym=='NQ':
        # Barchart switched to whole-market totals for contracts from H25 on: those files carry the aggregate,
        # older files carry genuine per-contract figures. Total = the larger of the two readings each day.
        agg=[c for c in codes if C[c].attrs['exp']>=pd.Timestamp('2025-03-01')]
        per=[c for c in codes if c not in agg]
        V=allv.reindex(D.index); O=allo.reindex(D.index)
        D['vol_tot']=np.fmax(V[per].sum(axis=1,min_count=1), V[agg].max(axis=1))
        D['oi_tot']=np.fmax(O[per].sum(axis=1,min_count=1), O[agg].max(axis=1))
    else:
        D['vol_tot']=D['vol_front']; D['oi_tot']=D['oi_front']
    return D

if __name__=='__main__':
    for s in ['NQ','ES','RTY']:
        D=build(s); D.to_pickle(f'/home/claude/t2/D_{s}.pkl')
        print(s,D.index.min().date(),D.index.max().date(),len(D))
