# Su, Bao, Li, Xu, Cui (2022) FRL 47:102702 - functional logit prediction of next-day price gap, replicated on NQ / ES
import sys, glob, math, numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
from datetime import time as T
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, accuracy_score
sys.argv=['x']; exec(open('hydra.py').read().split("# ---------------------------------------------------------------- cli")[0])
U='/mnt/user-data/uploads/'
GRID=pd.date_range('2000-01-01 09:35','2000-01-01 16:00',freq='5min').time   # 78 points
def build(pats):
    df=load(pats); vk=df.groupby(['td','k']).v.sum().reset_index().sort_values('v').drop_duplicates('td',keep='last')
    df=df.merge(vk[['td','k']],on=['td','k']); r=df[(df.t>=RTH0)&(df.t<T(16,0))].sort_values('dt')
    rows,curves=[],[]
    for (td,k),g in r.groupby(['td','k']):
        if len(g)<370: continue
        o=g.o.iloc[0]; s=g.set_index('t').c
        idx=[x for x in GRID]; px=[]
        for x in idx:
            m=s[s.index<x]                       # last close before grid time (bar stamped x-1min closes at x)
            px.append(m.iloc[-1] if len(m) else np.nan)
        px=np.array(px)
        if np.isnan(px).any(): continue
        rows.append(dict(td=td,k=k,ro=o,rh=g.h.max(),rl=g.l.min(),rc=px[-1])); curves.append(np.log(px/o))
    D=pd.DataFrame(rows).set_index('td'); X=np.array(curves)
    nxt=D.shift(-1); gap=(D.index.to_series().shift(-1)-D.index.to_series()).dt.days
    ok=(nxt.k==D.k)&(gap<=4)
    D['HO']=(nxt.ro>=D.rh).astype(float).where(ok); D['LO']=(nxt.ro<=D.rl).astype(float).where(ok)
    D['PG']=((D.HO==1)|(D.LO==1)).astype(float).where(ok)
    D['on_ret']=(100*np.log(nxt.ro/D.rc)).where(ok)            # 16:00 close -> next 09:30 open
    D['f_ret']=100*X[:,-1]; D['f_last']=100*(X[:,-1]-X[:,-13]); D['f_clv']=(D.rc-D.rl)/(D.rh-D.rl); D['f_rng']=np.log(D.rh/D.rl)
    return D,X
def fpca(X,lr):
    Xc=X-X.mean(0); N=len(Xc)
    if lr:   # truncation-free Bartlett long-run covariance (Kiefer-Vogelsang), eq. (7)
        G=Xc.T@Xc/N
        for h in range(1,N):
            Gh=Xc[h:].T@Xc[:-h]/N; G+=(1-h/N)*(Gh+Gh.T)
    else: G=Xc.T@Xc/N
    w,v=np.linalg.eigh(G); o=np.argsort(w)[::-1]; return X.mean(0),v[:,o],w[o]
def scores(X,mu,V,K): return (X-mu)@V[:,:K]
def run(name,D,X,test_from):
    print(f'\n===== {name}: {len(D)} sessions {D.index.min().date()} -> {D.index.max().date()}  OOS from {test_from}')
    res={}
    for lab in ['PG','HO','LO']:
        m=D[lab].notna().values; Dm=D[m]; Xm=X[m]; yrs=sorted(set(Dm.index.year[Dm.index>=test_from]))
        P={k:[] for k in ['flogit_sr','flogit_lr','svm','gbdt','scalar']}; Y=[]; IDX=[]
        for yr in yrs:
            tr=Dm.index.year<yr; te=Dm.index.year==yr
            if tr.sum()<150 or te.sum()==0: continue
            ytr=Dm[lab].values[tr]; Y+=list(Dm[lab].values[te]); IDX+=list(Dm.index[te])
            for key,lr in [('flogit_sr',False),('flogit_lr',True)]:
                mu,V,w=fpca(Xm[tr],lr); K=int(np.searchsorted(np.cumsum(w)/w.sum(),0.95)+1); K=min(max(K,2),8)
                Str,Ste=scores(Xm[tr],mu,V,K),scores(Xm[te],mu,V,K); sd=Str.std(0)
                P[key]+=list(LogisticRegression(max_iter=1000).fit(Str/sd,ytr).predict_proba(Ste/sd)[:,1])
            mu,V,w=fpca(Xm[tr],False); Str,Ste=scores(Xm[tr],mu,V,8),scores(Xm[te],mu,V,8); sd=Str.std(0)
            P['svm']+=list(SVC(kernel='rbf',probability=True,random_state=0).fit(Str/sd,ytr).predict_proba(Ste/sd)[:,1])
            P['gbdt']+=list(GradientBoostingClassifier(random_state=0).fit(Str,ytr).predict_proba(Ste)[:,1])
            F=['f_ret','f_last','f_clv','f_rng']; ftr=Dm.loc[tr,F]; m_,s_=ftr.mean(),ftr.std()
            P['scalar']+=list(LogisticRegression(max_iter=1000).fit((ftr-m_)/s_,ytr).predict_proba((Dm.loc[te,F]-m_)/s_)[:,1])
        Y=np.array(Y); base=Y.mean(); maj=max(base,1-base)
        print(f'  {lab}: OOS n={len(Y)} event rate {100*base:.1f}%  majority-class accuracy {100*maj:.1f}%')
        rng=np.random.default_rng(1)
        for k,p in P.items():
            p=np.array(p); auc=roc_auc_score(Y,p); acc=accuracy_score(Y,p>=0.5)
            bs=np.mean((p-Y)**2); bss=1-bs/np.mean((base-Y)**2)
            boot=[roc_auc_score(Y[i],p[i]) for i in (rng.integers(0,len(Y),len(Y)) for _ in range(500)) if 0<Y[i].sum()<len(i)]
            print(f'     {k:10s} AUC {auc:.3f} [{np.percentile(boot,2.5):.3f}-{np.percentile(boot,97.5):.3f}]  acc {100*acc:.1f}%  Brier skill {bss:+.3f}')
        res[lab]=(pd.Series(P['flogit_lr'],index=IDX),pd.Series(P['scalar'],index=IDX))
    # trading: overnight hold 16:00 -> 09:30 in direction of P(HO)-P(LO), vs always long overnight
    ho,lo=res['HO'][0],res['LO'][0]; idx=ho.index.intersection(lo.index)
    s=np.sign(ho[idx]-lo[idx]); r=D.loc[idx,'on_ret']; ok=r.notna()&(s!=0); s,r=s[ok],r[ok]
    hit=(np.sign(r)==s).mean(); L=r
    print(f'  overnight trade (sign of P(HO)-P(LO)): n={len(r)} hit {100*hit:.1f}% (p {stats.binomtest(int((np.sign(r)==s).sum()),len(r)).pvalue:.3f})  mean {np.mean(s*r):+.4f}%/night  sum {np.sum(s*r):+.1f}%'
          f'  | always long overnight: up {100*(L>0).mean():.1f}% mean {L.mean():+.4f}% sum {L.sum():+.1f}%')
    top=(ho[idx]-lo[idx]).abs(); q=top[ok].quantile(0.8); sel=top[ok]>=q
    print(f'  top-20% conviction nights: n={sel.sum()} hit {100*(np.sign(r[sel])==s[sel]).mean():.1f}%  mean {np.mean(s[sel]*r[sel]):+.4f}%  | long same nights {r[sel].mean():+.4f}%')
D,X=build(glob.glob(U+'NQ_*_1min_continuous.csv')+glob.glob(U+'nq?26_intraday-1min*.csv')); run('NQ',D,X,'2023-01-01')
D2,X2=build([U+'ES_2023_2026_1min_continuous.csv']); run('ES',D2,X2,'2024-01-01')
