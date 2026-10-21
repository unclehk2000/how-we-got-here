import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
from sklearn.tree import DecisionTreeClassifier, export_text
from scan import FEATS
for mk in ['NQ','ES']:
    F=pd.read_pickle(f'nyam_{mk}.pkl'); T=F[F.z_touch==1].copy()
    feats=[f for f in FEATS if f!='touch_min']+['g']
    years=sorted(T.index.year.unique()); sel=pd.Series(np.nan,index=T.index,dtype=float)
    for Y in years[2:]:
        tr=T[T.index.year<Y]; med=tr[feats].median()
        m=DecisionTreeClassifier(max_depth=2,min_samples_leaf=40).fit(tr[feats].fillna(med),tr.z_hold>0.5)
        te=T.index.year==Y; sel[te]=(m.predict_proba(T.loc[te,feats].fillna(med))[:,1]>=0.55).astype(float)
    s=sel.dropna().astype(bool); ix=s.index
    print(mk,'OOS tree-selected days',int(s.sum()),'of',len(s),'| CE hold %.1f%% vs not selected %.1f%% | decoy .375 %.1f%% .625 %.1f%% on selected days'%(
        100*T.loc[ix[s],'z_hold'].mean(),100*T.loc[ix[~s],'z_hold'].mean(),100*F.loc[ix[s]].d375_hold.mean(),100*F.loc[ix[s]].d625_hold.mean()))
    full=DecisionTreeClassifier(max_depth=2,min_samples_leaf=40).fit(T[feats].fillna(T[feats].median()),T.z_hold>0.5)
    print(export_text(full,feature_names=feats,decimals=2,show_weights=True))
    q=T[(T.gap_atr<=T.gap_atr.quantile(1/3))&(T.on_atr<=T.on_atr.quantile(1/2))]
    print('  small gap & quiet overnight: CE hold %.1f%% (n %d) | decoys same days .375 %.1f%% .625 %.1f%%'%(100*q.z_hold.mean(),len(q),100*F.loc[q.index].d375_hold.mean(),100*F.loc[q.index].d625_hold.mean()))
