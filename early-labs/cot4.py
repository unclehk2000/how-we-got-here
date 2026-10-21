import sys, glob, math, numpy as np, pandas as pd, statsmodels.api as sm, warnings; warnings.filterwarnings('ignore')
from datetime import time as T
from scipy import stats
sys.argv=['x']; exec(open('hydra.py').read().split("# ---------------------------------------------------------------- cli")[0])
# ---- combined verified dataset
allx=pd.read_pickle('cot/cot_es_rty_ym.pkl'); nq=pd.read_csv('COT_NQ_TFF_2015_2026.csv',parse_dates=['report_date']).set_index('report_date')
rows=[]
for m,X in [('NQ',None),('ES',allx['ES']),('RTY',allx['RTY']),('YM',allx['YM'])]:
    if m=='NQ': d=nq.copy()
    else: d=pd.DataFrame({'open_interest':X.open_interest_all,'am_long':X.asset_mgr_positions_long,'am_short':X.asset_mgr_positions_short,'lev_long':X.lev_money_positions_long,'lev_short':X.lev_money_positions_short})
    d=d.reset_index().rename(columns={'index':'report_date','id':'report_date'}); d.insert(1,'market',m); rows.append(d)
ALL=pd.concat(rows); ALL['report_date']=pd.to_datetime(ALL.report_date).dt.date
ALL[['report_date','market','open_interest','am_long','am_short','lev_long','lev_short']].sort_values(['report_date','market']).to_csv('/mnt/user-data/outputs/COT_TFF_NQ_ES_RTY_YM_2015_2026.csv',index=False)
print('combined rows',len(ALL))
# ---- per-market net % OI and weekly change
P={}
for m,g in ALL.groupby('market'):
    g=g.set_index(pd.to_datetime(g.report_date)).sort_index()
    P[m]=pd.DataFrame({'am':(g.am_long-g.am_short)/g.open_interest*100,'lev':(g.lev_long-g.lev_short)/g.open_interest*100})
C=pd.concat({m:P[m] for m in P},axis=1)
for m in P:
    C[(m,'dam')]=C[(m,'am')].diff(); C[(m,'dlev')]=C[(m,'lev')].diff()
C['breadth_am']=sum((C[(m,'dam')]>0).astype(int) for m in ['NQ','ES','RTY','YM']).where(C[('RTY','dam')].notna())
C['net_dam_sign']=sum(np.sign(C[(m,'dam')]) for m in ['NQ','ES','RTY','YM'])
# ---- prices: NQ and ES weekly returns, post-release (Mon open -> next Mon open) and Tue->Tue
def daily(pats):
    df=load(pats); S=pick_active(sessions(df,T(9,25))); S=S[S.n_rth>=200].copy()
    prev=S.shift(1); gap=S.index.to_series().diff().dt.days
    S['r_oo']=pd.Series(np.where(S.k==prev.k,np.log(S.ro/prev.ro),np.log(prev.rc/prev.ro)),index=S.index).where(gap<=4)
    S['r_cc']=pd.Series(np.where(S.k==prev.k,np.log(S.rc/prev.rc),np.log(S.rc/S.ro)),index=S.index).where(gap<=4)
    return S
U='/mnt/user-data/uploads/'
SN=daily(glob.glob(U+'NQ_*_1min_continuous.csv')+glob.glob(U+'nq?26_intraday-1min*.csv'))
SE=daily([U+'ES_2023_2026_1min_continuous.csv'])
rep=C.index
def rel(S,i):
    if i+1>=len(rep): return np.nan
    a=rep[i]+pd.Timedelta(days=4); b=rep[i+1]+pd.Timedelta(days=4); d=S.index
    seg=S.loc[(d>a)&(d<=b+pd.Timedelta(days=2)),'r_oo']
    if len(seg)<4 or seg.isna().any() or (seg.index[0]-a).days>3: return np.nan
    return 100*seg.sum()
def tue(S,i):
    if i==0: return np.nan
    a,b=rep[i-1],rep[i]; d=S.index; seg=S.loc[(d>a)&(d<=b),'r_cc']
    if len(seg)<3 or seg.isna().any() or (b-seg.index[-1]).days>3: return np.nan
    return 100*seg.sum()
for nm,S in [('NQ',SN),('ES',SE)]:
    C[(nm,'R_rel')]=[rel(S,i) for i in range(len(rep))]; C[(nm,'R_tue')]=[tue(S,i) for i in range(len(rep))]
shut=(C.index>='2025-09-30')&(C.index<='2025-12-31')
for nm in ['NQ','ES']: C.loc[shut,(nm,'R_rel')]=np.nan
C.to_pickle('cot/cot4.pkl')
def binom(h,n): return stats.binomtest(int(h),int(n)).pvalue
print('\n[1] Cross-market breadth of asset-manager WoW change -> NQ and ES')
for nm in ['NQ','ES']:
    for lab,col in [('same week (Tue-Tue)',(nm,'R_tue')),('week after release',(nm,'R_rel'))]:
        G=pd.concat([C['breadth_am'],C[col].rename('r')],axis=1).dropna()
        out=' | '.join(f'{int(k)}/4 up: n={len(g)} mean {g.r.mean():+.2f}% up {100*(g.r>0).mean():.0f}%' for k,g in G.groupby('breadth_am'))
        rho,p=stats.spearmanr(G.breadth_am,G.r)
        print(f'  {nm} {lab:20s} rho {rho:+.3f} p {p:.4f}  || {out}')
print('\n[2] "All four aligned" rule (4/4 adding = long, 0/4 = short, else flat) vs always long, week after release')
for nm in ['NQ','ES']:
    G=pd.concat([C['breadth_am'],C[(nm,'R_rel')].rename('r')],axis=1).dropna()
    sig=np.where(G.breadth_am==4,1,np.where(G.breadth_am==0,-1,0)); act=G[sig!=0]; s=sig[sig!=0]
    hit=(np.sign(act.r)==s).sum(); n=len(act)
    print(f'  {nm}: trades {n}  hit {100*hit/n:.1f}% (p {binom(hit,n):.3f})  mean {np.mean(s*act.r):+.3f}%  | always long on same weeks: up {100*(act.r>0).mean():.1f}% mean {act.r.mean():+.3f}%')
print('\n[3] Guide checklist proxy: NQ+ES asset managers both adding AND RTY+YM not reducing (bull) / mirror (bear)')
for nm in ['NQ','ES']:
    bull=(C[('NQ','dam')]>0)&(C[('ES','dam')]>0)&(C[('RTY','dam')]>=0)&(C[('YM','dam')]>=0)
    bear=(C[('NQ','dam')]<0)&(C[('ES','dam')]<0)&(C[('RTY','dam')]<=0)&(C[('YM','dam')]<=0)
    for lab,col in [('same week',(nm,'R_tue')),('week after',(nm,'R_rel'))]:
        r=C[col]; b=r[bull].dropna(); e=r[bear].dropna()
        hb=(b>0).sum(); he=(e<0).sum(); n=len(b)+len(e)
        print(f'  {nm} {lab:10s}: bull n={len(b)} up {100*(b>0).mean():.0f}% | bear n={len(e)} down {100*(e<0).mean():.0f}%  combined hit {100*(hb+he)/n:.1f}% (p {binom(hb+he,n):.4f})')
print('\n[4] Paper (SBM 2004) Granger tests pooled NQ+ES: R_t on own lag + lagged net-position change (post-release returns)')
for grp in ['dam','dlev']:
    rows=[]
    for nm in ['NQ','ES']:
        d=pd.DataFrame({'r':C[(nm,'R_rel')],'x':C[(nm,grp)],'rl':C[(nm,'R_rel')].shift(1)}).dropna(); d['mkt']=nm; rows.append(d)
    D=pd.concat(rows); X=sm.add_constant(pd.get_dummies(D[['x','rl','mkt']],drop_first=True).astype(float))
    r=sm.OLS(D.r,X).fit(cov_type='cluster',cov_kwds={'groups':D.index.factorize()[0]})
    print(f'  {grp}: N={int(r.nobs)}  coef {r.params.x:+.4f}  t {r.tvalues.x:+.2f}  p {r.pvalues.x:.3f}')
print('\nlatest report', C.index[-1].date(), {m:(round(C[(m,'am')].iloc[-1],1),round(C[(m,'dam')].iloc[-1],2)) for m in ['NQ','ES','RTY','YM']}, 'breadth', C.breadth_am.iloc[-1])
