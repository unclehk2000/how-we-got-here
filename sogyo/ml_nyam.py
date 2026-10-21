"""Walk-forward ML on NY AM wall hold (touched days). Test years refit on all earlier years.
Also: same model aimed at the DECOY levels, and permutation importance on the pooled OOS predictions."""
import pandas as pd, numpy as np, sys, warnings; warnings.filterwarnings('ignore')
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
from scan import FEATS
def wf(T,target,model,feats):
    years=sorted(T.index.year.unique()); p=pd.Series(np.nan,index=T.index)
    for Y in years[2:]:
        tr=T[(T.index.year<Y)&T[target].notna()]; te=T.index.year==Y
        X=tr[feats]; med=X.median()
        if model=='gbm':
            m=HistGradientBoostingClassifier(max_depth=2,learning_rate=0.05,max_iter=150,min_samples_leaf=25).fit(X,(tr[target]>0.5))
            p[te]=m.predict_proba(T.loc[te,feats])[:,1]
        else:
            sc=StandardScaler().fit(X.fillna(med)); m=LogisticRegression(penalty='l1',solver='liblinear',C=0.05).fit(sc.transform(X.fillna(med)),(tr[target]>0.5))
            p[te]=m.predict_proba(sc.transform(T.loc[te,feats].fillna(med)))[:,1]
    return p
for mk in sys.argv[1:] or ['NQ','ES']:
    F=pd.read_pickle(f'nyam_{mk}.pkl'); F['ps']=F.prev_state.map({'Expansion':0,'Retracement':1,'Reversal':2,'Consolidation':3})
    feats=FEATS+['ps','g']
    print(f'\n===== {mk} =====  OOS years:',sorted(F.index.year.unique())[2:])
    for target,touch in [('z_hold','z_touch'),('d375_hold','d375_touch'),('d625_hold','d625_touch')]:
        T=F[F[touch]==1].copy()
        feats_t=[f for f in feats if not (f=='touch_min' and target!='z_hold')]
        for model in ['gbm','logit']:
            p=wf(T,target,model,feats_t); m=p.notna()&T[target].notna()
            y=(T[target][m]>0.5).astype(int); auc=roc_auc_score(y,p[m]) if y.nunique()>1 else np.nan
            top=p[m]>=p[m].quantile(2/3); bot=p[m]<=p[m].quantile(1/3)
            print(f'  {target:9s} {model:5s} n {m.sum():4d} AUC {auc:.3f} | hold in top third {100*T[target][m][top].mean():.1f}% vs bottom third {100*T[target][m][bot].mean():.1f}% (base {100*T[target][m].mean():.1f}%)')
            if target=='z_hold' and model=='gbm': T['p']=p; T[['p']].to_pickle(f'p_{mk}.pkl')
    # do the CE's top-third days also lift the decoys on those same days?
    T=F[F.z_touch==1].join(pd.read_pickle(f'p_{mk}.pkl')); m=T.p.notna(); top=T.p>=T.p[m].quantile(2/3)
    D=F.loc[T.index[m&top]]
    print(f'  model top-third days: CE hold {100*T[m&top].z_hold.mean():.1f}% | decoy .375 {100*D.d375_hold.mean():.1f}% .625 {100*D.d625_hold.mean():.1f}% on the same days')
