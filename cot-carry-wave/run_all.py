import pandas as pd, numpy as np, sys, json
from ml_search import load, search, null_best, test_variant, VAL, TEST, score, walk, G
mkts=sys.argv[1].split(',') if len(sys.argv)>1 else ['NQ','ES','YM','RTY']
runs=int(sys.argv[2]) if len(sys.argv)>2 else 30
TGT=sys.argv[3] if len(sys.argv)>3 else 'y'
KW=dict(target=TGT,purge=3 if TGT=='y4' else 0,step=4 if TGT=='y4' else 1)
MIN=12 if TGT=='y4' else 30
D=load(mkts); D=D[D.y.notna()]
R,_=search(D,VAL,min_n=MIN,**KW); R=R.sort_values('edge',ascending=False)
R.to_csv(f'search_val_{TGT}.csv',index=False)
N=null_best(D,runs,min_n=MIN,**KW); N.to_csv(f'search_null_{TGT}.csv',index=False)
print('variants',len(R),'| real best edge %.3f, best hit %.3f, #hit>=70%%: %d'%(R.edge.max(),R.hit.max(),(R.hit>=.7).sum()))
print('null (shifted target) best edge: median %.3f, 95th %.3f | best hit median %.3f 95th %.3f | #hit>=70%% median %d'%(
      N.best_edge.median(),N.best_edge.quantile(.95),N.best_hit.median(),N.best_hit.quantile(.95),N.n70.median()))
print('p(best edge by chance) = %.2f'%((N.best_edge>=R.edge.max()).mean()))
top=R.iloc[0]; s,p=test_variant(D,top,**KW)
print('\nSELECTED on validation:',dict(top[['groups','model','band','mode','n','hit','edge']]))
print('TEST',TEST,':',{k:(round(v,3) if isinstance(v,float) else v) for k,v in s.items()})
# best long-short variant too
ls=R[R['mode']=='longshort'].iloc[0]; s2,_=test_variant(D,ls,**KW)
print('\nBest long/short on validation:',dict(ls[['groups','model','band','n','hit','edge']]))
print('TEST:',{k:(round(v,3) if isinstance(v,float) else v) for k,v in s2.items()})
json.dump({'selected':dict(top.astype(str)),'test':s,'ls_selected':dict(ls.astype(str)),'ls_test':s2},open(f'search_result_{TGT}.json','w'),indent=1,default=str)
