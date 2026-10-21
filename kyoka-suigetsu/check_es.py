import pandas as pd, numpy as np
PC='/mnt/user-data/uploads/nq_es_rty_daily_task2_1/per_contract/ES'
d=pd.read_pickle('bars_ES_1822_raw.pkl')
def daily(c):
    x=pd.read_csv(f'{PC}/{c.lower()}.csv',parse_dates=['Date']).set_index('Date'); return x
# roll trading days: tday with two contracts
nc=d.groupby('tday').Contract.nunique(); roll=nc[nc>1].index
print('roll tdays:',len(roll))
adj=[]
for td in roll:
    x=d[d.tday==td]; old,new=x.Contract.iloc[0],x.Contract.iloc[-1]
    prev=d[d.tday<td].tday.max()
    o=daily(old); n=daily(new)
    sp=n.Close.get(prev,np.nan)-o.Close.get(prev,np.nan)
    m=(d.tday==td)&(d.Contract==old)
    for c in ['Open','High','Low','Close']: d.loc[m,c]+=sp
    d.loc[m,'Contract']=new
    adj.append((td.date(),old,new,sp,m.sum()))
print(pd.DataFrame(adj,columns=['tday','old','new','spread','bars_adj']).to_string())
# minutes per day
g=d.groupby('tday').agg(n=('ts','size'),H=('High','max'),L=('Low','min'),O=('Open','first'),C=('Close','last'),con=('Contract','last'),first=('hm','first'),last=('hm','last'))
print('\nminutes/day:',g.n.describe().round(0).to_dict())
print('short days (<1200 bars):',(g.n<1200).sum()); print(g[g.n<1200][['n','first','last']].to_string())
# compare to Barchart daily H/L of the same contract
rows=[]
for td,r in g.iterrows():
    dd=daily(r.con)
    if td in dd.index: rows.append((td,r.H-dd.High[td],r.L-dd.Low[td],r.C-dd.Close[td],r.H-r.L,dd.High[td]-dd.Low[td]))
c=pd.DataFrame(rows,columns=['tday','dH','dL','dC','rng1m','rngD']).set_index('tday')
print('\nmatched days',len(c),'of',len(g))
for k in ['dH','dL']:
    print(k,'exact',(c[k].abs()<1e-9).mean().round(4),'|abs|>1pt',(c[k].abs()>1).sum(),'max',c[k].abs().max())
print('range 1m vs daily: median ratio',(c.rng1m/c.rngD).median().round(4),' days off by >2%:',((c.rng1m/c.rngD-1).abs()>0.02).sum())
print(c[(c.rng1m/c.rngD-1).abs()>0.02].round(2).to_string())
d=d.drop(columns=[]); d.to_pickle('bars_ES_1822.pkl')
