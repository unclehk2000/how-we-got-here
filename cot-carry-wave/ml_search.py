"""Build-and-rebuild search for a weekly direction model.
Every variant is fitted walk-forward (expanding window, refit each calendar year).
Selection uses VALIDATION years only; the TEST years are scored once, after selection.
A shifted-target null re-runs the whole search to measure how good the best variant looks by chance."""
import pandas as pd, numpy as np, itertools, warnings, sys, json
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings('ignore')
VAL=[2022,2023]; TEST=[2024,2025,2026]

G={
 'cot_level':['am','lev','am_i26','am_i52','am_i156','lev_i26','lev_i52','lev_i156','am_z52','lev_z52'],
 'cot_change':['am_d1','am_d4','lev_d1','lev_d4'],
 'cot_wave':[f'{g}_w{W}_{k}' for g in ['am','lev'] for W in (26,52) for k in ['osc','vel','proj','T','r2']],
 'px_wave':[f'px_w{W}_{k}' for W in (26,52,104) for k in ['osc','vel','proj','T','r2']],
 'px_mom':['r1','r4','r13','vol8','dd26','du26','above_sma10'],
 'rty':['rty_am','rty_am_d1','rty_am_i52','rty_lev','rty_lev_d1','am_minus_rty_d1'],
}
GROUP_SETS=[('cot_change',),('cot_level',),('cot_wave',),('px_wave',),('px_mom',),('rty',),
            ('cot_change','cot_level'),('cot_wave','px_wave'),('cot_level','cot_wave','cot_change'),
            ('px_wave','px_mom'),('cot_level','px_mom'),('cot_level','cot_change','cot_wave','px_wave','px_mom','rty')]
MODELS={'logit':lambda:LogisticRegression(C=0.1,max_iter=500),
        'logit_weak':lambda:LogisticRegression(C=0.01,max_iter=500),
        'gbm':lambda:HistGradientBoostingClassifier(max_depth=2,learning_rate=0.05,max_iter=150,min_samples_leaf=20),
        'gbm_deep':lambda:HistGradientBoostingClassifier(max_depth=4,learning_rate=0.05,max_iter=300,min_samples_leaf=10)}
BANDS=[0.0,0.03,0.06,0.10]          # trade only when |p-0.5| > band
MODES=['longshort','longflat']

def load(mkts):
    out=[]
    for m in mkts:
        try: F=pd.read_pickle(f'F_{m}.pkl')
        except FileNotFoundError: continue
        F=F.copy(); F['y4']=sum(F.y.shift(-j) for j in range(4)); F['mkt']=m; F['year']=F.index.start_time.year; F['wk']=F.index; out.append(F)
    return pd.concat(out,ignore_index=True)

def walk(D,cols,model,years,target='y',purge=0):
    """out-of-sample P(up) for each row in `years`, refitting at each year boundary"""
    p=pd.Series(np.nan,index=D.index)
    for Y in years:
        cut=pd.Period(f'{Y}-01-01',freq='W-FRI')-purge
        tr=D[(D.wk<cut)&D[target].notna()]; te=D.year==Y
        if len(tr)<60 or te.sum()==0: continue
        X=tr[cols].replace([np.inf,-np.inf],np.nan); med=X.median().fillna(0)
        sc=StandardScaler().fit(X.fillna(med)); clf=MODELS[model]()
        clf.fit(sc.transform(X.fillna(med)),(tr[target]>0).astype(int))
        p[te]=clf.predict_proba(sc.transform(D.loc[te,cols].replace([np.inf,-np.inf],np.nan).fillna(med)))[:,1]
    return p

def score(D,p,band,mode,target='y',step=1):
    D=D.assign(y=D[target]); keep=pd.Series(False,index=D.index)
    for _,ix in D.groupby('mkt').groups.items(): keep[ix[::step]]=True
    live=p.notna()&D.y.notna()&keep
    m=live&((p-0.5).abs()>band)
    if mode=='longflat': m&=p>0.5
    s=np.sign(p-0.5).where(m,0.0)
    y=D.y[m]
    if len(y)==0: return dict(n=0)
    strat=(s*D.y)[live]; bh=D.y[live]
    sh=lambda r: float(r.mean()/r.std()*np.sqrt(52/step)) if r.std()>0 else np.nan
    hit=float((np.sign(y)==s[m]).mean()); long_hit=float((y>0).mean()); base=float((bh>0).mean())
    return dict(n=int(len(y)),hit=hit,long_hit=long_hit,base_up=base,
                edge=hit-(long_hit if mode=='longshort' else base),
                pl=float(strat.sum()),bh=float(bh.sum()),sharpe=sh(strat),sharpe_bh=sh(bh),cover=float(m.sum()/live.sum()))

def search(D,years,min_n=30,target='y',purge=0,step=1):
    res=[]; preds={}
    feats=set(D.columns)
    for gs,model in itertools.product(GROUP_SETS,MODELS):
        cols=[c for g in gs for c in G[g] if c in feats and D[c].notna().mean()>0.3]
        if not cols: continue
        p=walk(D,cols,model,years,target,purge); preds[(gs,model)]=p
        for band,mode in itertools.product(BANDS,MODES):
            s=score(D,p,band,mode,target,step)
            if s['n']>=min_n: res.append(dict(groups='+'.join(gs),model=model,band=band,mode=mode,**s))
    return pd.DataFrame(res),preds

if __name__=='__main__':
    mkts=sys.argv[1:] or ['NQ','ES','YM','RTY']
    D=load(mkts)
    D=D[D.y.notna()]
    print('markets',D.mkt.unique().tolist(),'rows',len(D),'years',sorted(D.year.unique()))
    R,P=search(D,VAL)
    R=R.sort_values('edge',ascending=False)
    print(len(R),'variants scored on validation', VAL)
    print(R.head(15).round(3).to_string(index=False))
    R.to_csv('search_val.csv',index=False)

def shifted(D,rng):
    D=D.copy()
    for m,idx in D.groupby('mkt').groups.items():
        k=rng.integers(26,len(idx)-26)
        for c in ['y','y4']:
            if c in D: D.loc[idx,c]=np.roll(D.loc[idx,c].values,k)
    return D

def null_best(D,runs=30,seed=1,**kw):
    rng=np.random.default_rng(seed); out=[]
    for i in range(runs):
        R,_=search(shifted(D,rng),VAL,**kw)
        out.append(dict(best_edge=R.edge.max(),best_hit=R.hit.max(),
                        n70=int((R.hit>=0.70).sum()),best_hit_ls=R[R['mode']=='longshort'].hit.max()))
    return pd.DataFrame(out)

def test_variant(D,row,target='y',purge=0,step=1):
    gs=tuple(row['groups'].split('+')); feats=set(D.columns)
    cols=[c for g in gs for c in G[g] if c in feats and D[c].notna().mean()>0.3]
    p=walk(D,cols,row['model'],TEST,target,purge)
    return score(D,p,row['band'],row['mode'],target,step),p
