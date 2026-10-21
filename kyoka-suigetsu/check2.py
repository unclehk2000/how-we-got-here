import pandas as pd, numpy as np
PC='/mnt/user-data/uploads/nq_es_rty_daily_task2_1/per_contract/ES'
b=pd.read_pickle('bars_ES_all.pkl')
cache={}
def daily(c):
    if c not in cache: cache[c]=pd.read_csv(f'{PC}/{c.lower()}.csv',parse_dates=['Date']).set_index('Date')
    return cache[c]
g=b.groupby('tday').agg(H=('High','max'),L=('Low','min'),con=('Contract','last'),n=('ts','size'))
rows=[]
for td,r in g.iterrows():
    dd=daily(r.con)
    if td in dd.index: rows.append((td,r.H-dd.High[td],r.L-dd.Low[td],(r.H-r.L)/(dd.High[td]-dd.Low[td])-1,r.n))
c=pd.DataFrame(rows,columns=['tday','dH','dL','rr','n']).set_index('tday')
print('matched',len(c),'of',len(g))
for p,cc in [('2018–22',c[c.index.year<=2022]),('2023–26',c[c.index.year>=2023])]:
    print(p,'days',len(cc),'H exact %.3f'%(cc.dH.abs()<1e-9).mean(),'L exact %.3f'%(cc.dL.abs()<1e-9).mean(),'range off >2%:',(cc.rr.abs()>0.02).sum(),' median |range err| %.4f'%cc.rr.abs().median())
print(c[c.rr.abs()>0.02].round(3).to_string())
