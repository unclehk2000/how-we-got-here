import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
from ml_search import load, test_variant
import sys
mkts=sys.argv[1].split(',')
D=load(mkts); D=D[D.y.notna()]
for tgt in ['y','y4']:
    R=pd.read_csv(f'search_val_{tgt}.csv'); V=R[R.hit>=0.70]
    kw=dict(target=tgt,purge=3 if tgt=='y4' else 0,step=4 if tgt=='y4' else 1)
    out=[]
    for _,r in V.iterrows():
        s,_=test_variant(D,r,**kw); out.append(dict(val_hit=r.hit,val_n=r.n,**{'test_'+k:v for k,v in s.items()}))
    O=pd.DataFrame(out)
    print(f'\n{tgt}: {len(V)} of {len(R)} variants hit >=70% on validation')
    print(' on test: median hit %.3f, hit>=70%%: %d, median edge %+.3f, beat always-long Sharpe: %d, median test n %d'%(
        O.test_hit.median(),(O.test_hit>=0.7).sum(),O.test_edge.median(),(O.test_sharpe>O.test_sharpe_bh).sum(),O.test_n.median()))
    print(' test base up-rate %.3f'%O.test_base_up.iloc[0])
    O.to_csv(f'survivors_{tgt}.csv',index=False)
