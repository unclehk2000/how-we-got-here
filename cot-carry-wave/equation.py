"""Sparse logistic 'forecasting equation' fitted on pre-2024 weeks, scored on 2024-26."""
import pandas as pd, numpy as np, sys
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from ml_search import load, G, score
mkts=sys.argv[1].split(',') if len(sys.argv)>1 else ['NQ','ES','YM','RTY']
D=load(mkts); D=D[D.y.notna()]
cols=[c for g in ['cot_level','cot_change','cot_wave','px_wave','px_mom'] for c in G[g] if c in D and D[c].notna().mean()>0.3]
D[cols]=D[cols].replace([np.inf,-np.inf],np.nan)
tr=D[D.year<2024]; te=D[D.year>=2024]
med=tr[cols].median().fillna(0); sc=StandardScaler().fit(tr[cols].fillna(med))
best=None
for C in [0.005,0.01,0.02,0.05,0.1]:
    # choose C by last pre-test year
    a=tr[tr.year<2023]; b=tr[tr.year==2023]
    if len(a)<60: continue
    m=LogisticRegression(penalty='l1',solver='liblinear',C=C).fit(sc.transform(a[cols].fillna(med)),(a.y>0))
    acc=((m.predict_proba(sc.transform(b[cols].fillna(med)))[:,1]>0.5)==(b.y>0)).mean()
    if best is None or acc>best[1]: best=(C,acc)
C=best[0] if best else 0.02
m=LogisticRegression(penalty='l1',solver='liblinear',C=C).fit(sc.transform(tr[cols].fillna(med)),(tr.y>0))
coef=pd.Series(m.coef_[0],index=cols); nz=coef[coef!=0].sort_values(key=abs,ascending=False)
print('C',C,'| intercept %.3f'%m.intercept_[0]); print(nz.round(3).to_string())
p=pd.Series(m.predict_proba(sc.transform(te[cols].fillna(med)))[:,1],index=te.index)
Dt=te.copy()
for band,mode in [(0,'longshort'),(0,'longflat'),(0.05,'longshort')]:
    print(band,mode,{k:round(v,3) if isinstance(v,float) else v for k,v in score(Dt,p,band,mode).items()})
pd.DataFrame({'feature':nz.index,'beta_per_sd':nz.values,'train_mean':tr[nz.index].mean().values,'train_sd':tr[nz.index].std().values}).to_csv('equation_coefs.csv',index=False)
