"""COT vs NQ/ES on 1-min data, truncated to weeks the 1-min files fully cover.
Entry = close of the 15:30 ET bar on release Friday (report Tuesday + 3 days); exit = same bar on the next release Friday.
Weeks are kept only if both bars exist in the SAME contract and no session gap > 4 days lies between them."""
import sys, glob, math, numpy as np, pandas as pd, statsmodels.api as sm, warnings; warnings.filterwarnings('ignore')
from datetime import time as T, timedelta
from scipy import stats
sys.argv=['x']; exec(open('hydra.py').read().split("# ---------------------------------------------------------------- cli")[0])
U='/mnt/user-data/uploads/'
def minute(pats):
    df=load(pats); vk=df.groupby(['td','k']).v.sum().reset_index().sort_values('v').drop_duplicates('td',keep='last')
    df=df.merge(vk[['td','k']],on=['td','k']).sort_values('dt').set_index('dt'); return df
M={'NQ':minute(glob.glob(U+'NQ_*_1min_continuous.csv')+glob.glob(U+'nq?26_intraday-1min*.csv')),
   'ES':minute([U+'ES_2023_2026_1min_continuous.csv'])}
for m,d in M.items(): print(m,'1-min bars',len(d),d.index.min(),'->',d.index.max(),'sessions',d.td.nunique())
ALL=pd.read_csv('/mnt/user-data/outputs/COT_TFF_NQ_ES_RTY_YM_2015_2026.csv',parse_dates=['report_date'])
P={}
for mk,g in ALL.groupby('market'):
    g=g.set_index('report_date').sort_index()
    P[mk]=pd.DataFrame({'am':(g.am_long-g.am_short)/g.open_interest*100,'lev':(g.lev_long-g.lev_short)/g.open_interest*100})
    P[mk]['dam']=P[mk].am.diff(); P[mk]['dlev']=P[mk].lev.diff()
    for w in (52,):
        for x in ('am','lev'):
            lo,hi=P[mk][x].rolling(w).min(),P[mk][x].rolling(w).max(); P[mk][f'{x}_idx{w}']=100*(P[mk][x]-lo)/(hi-lo)
rep=P['NQ'].index
breadth=sum((P[m].dam>0).astype(float) for m in ['NQ','ES','RTY','YM']).where(P['RTY'].dam.notna())
def bar(d,ts):     # close of the bar stamped at ts (allow up to 4 min later if missing)
    for k in range(5):
        t=ts+pd.Timedelta(minutes=k)
        if t in d.index: return d.loc[t]
    return None
def window(d,a,b,intraday=False):
    A,B=bar(d,a),bar(d,b)
    if A is None or B is None or A.k!=B.k: return np.nan
    if intraday: return 100*math.log(B.c/A.c)
    tds=pd.Series(sorted(d.loc[a:b,'td'].unique()))
    if len(tds)<2 or tds.diff().dt.days.max()>4: return np.nan
    return 100*math.log(B.c/A.c)
rows=[]
for i,t in enumerate(rep):
    fri=t+pd.Timedelta(days=3); nfri=rep[i+1]+pd.Timedelta(days=3) if i+1<len(rep) else None
    r={'report':t}
    for m,d in M.items():
        e=fri+pd.Timedelta(hours=15,minutes=30)
        r[f'{m}_rel']=window(d,e,nfri+pd.Timedelta(hours=15,minutes=30)) if nfri is not None else np.nan       # release -> next release
        r[f'{m}_tue']=window(d,(t-pd.Timedelta(days=7))+pd.Timedelta(hours=15,minutes=59),t+pd.Timedelta(hours=15,minutes=59))  # report week
        r[f'{m}_react']=window(d,e,fri+pd.Timedelta(hours=15,minutes=59),True)       # 15:30 -> 16:00 on release Friday
        sun=fri+pd.Timedelta(days=2,hours=18); A=bar(d,fri+pd.Timedelta(hours=16,minutes=14))
        B=d.loc[sun:sun+pd.Timedelta(minutes=30)].head(1)
        r[f'{m}_gap']=100*math.log(B.c.iloc[0]/A.c) if A is not None and len(B) and B.k.iloc[0]==A.k else np.nan
    rows.append(r)
R=pd.DataFrame(rows).set_index('report')
shut=(R.index>='2025-09-30')&(R.index<='2025-12-31'); R.loc[shut,['NQ_rel','ES_rel','NQ_react','ES_react','NQ_gap','ES_gap']]=np.nan
for m in ['NQ','ES']:
    for c in ['am','lev','dam','dlev','am_idx52','lev_idx52']: R[f'{m}_{c}']=P[m][c].reindex(R.index)
R['breadth']=breadth.reindex(R.index)
R.to_pickle('cot/cot_1min.pkl')
# ---- truncated, date-matched COT export
keep=R.NQ_rel.notna()|R.ES_rel.notna()|R.NQ_tue.notna()|R.ES_tue.notna()
T_=ALL[ALL.report_date.isin(R.index[keep])].copy()
cov=R[['NQ_tue','NQ_rel','ES_tue','ES_rel']].notna().astype(int); cov.columns=['nq_report_week','nq_post_release','es_report_week','es_post_release']
T_=T_.merge(cov,left_on='report_date',right_index=True)
T_['report_date']=T_.report_date.dt.date; T_.to_csv('/mnt/user-data/outputs/COT_truncated_to_1min_coverage.csv',index=False)
print(f'\nTruncated COT: {keep.sum()} report weeks ({R.index[keep].min().date()} -> {R.index[keep].max().date()}), {len(T_)} rows across 4 markets')
for m in ['NQ','ES']: print(f'  {m}: report-week windows {R[m+"_tue"].notna().sum()}, post-release windows {R[m+"_rel"].notna().sum()}, release reactions {R[m+"_react"].notna().sum()}')
def hit(sig,ret):
    d=pd.concat([sig.rename('s'),ret.rename('r')],axis=1).dropna(); d=d[d.s!=0]
    h=(np.sign(d.r)==np.sign(d.s)).sum(); n=len(d)
    return n,100*h/n if n else np.nan, stats.binomtest(int(h),n).pvalue if n else np.nan, (np.sign(d.s)*d.r).mean() if n else np.nan, 100*(d.r>0).mean() if n else np.nan
def line(lab,sig,ret):
    n,h,p,mr,up=hit(sig,ret); print(f'  {lab:46s} n={n:3d}  hit {h:5.1f}% (p {p:.4f})  mean {mr:+.3f}%  | long-only same weeks up {up:.1f}%')
print('\n[A] Follow asset-manager WoW change (own market)')
for m in ['NQ','ES']:
    line(f'{m} report week (Tue->Tue, already happened)',R[f'{m}_dam'],R[f'{m}_tue'])
    line(f'{m} release 15:30 -> next release 15:30',R[f'{m}_dam'],R[f'{m}_rel'])
print('\n[B] Fade leveraged-fund WoW change')
for m in ['NQ','ES']:
    line(f'{m} report week',-R[f'{m}_dlev'],R[f'{m}_tue']); line(f'{m} release -> next release',-R[f'{m}_dlev'],R[f'{m}_rel'])
print('\n[C] Four-market breadth: 4/4 adding = long, 0/4 = short')
sig=pd.Series(np.where(R.breadth==4,1,np.where(R.breadth==0,-1,0)),index=R.index)
for m in ['NQ','ES']:
    line(f'{m} report week',sig,R[f'{m}_tue']); line(f'{m} release -> next release',sig,R[f'{m}_rel'])
print('\n[D] Does the release itself move price? 15:30->16:00 Friday and Friday close -> Sunday open, signed by AM change')
for m in ['NQ','ES']:
    line(f'{m} 15:30->16:00 on release Friday',R[f'{m}_dam'],R[f'{m}_react'])
    line(f'{m} Fri 16:14 -> Sun 18:00 open gap',R[f'{m}_dam'],R[f'{m}_gap'])
    d=R[[f'{m}_dam',f'{m}_react']].dropna(); print(f'     corr(AM change, 15:30-16:00 move) {d.iloc[:,0].corr(d.iloc[:,1]):+.3f} n={len(d)}  | mean |15:30-16:00 move| {d.iloc[:,1].abs().mean():.3f}%')
print('\n[E] Extremes (52-week COT index) -> release-to-release return')
for m in ['NQ','ES']:
    for x,lab in [('am_idx52','AM'),('lev_idx52','LEV')]:
        for cond,nm in [(R[f'{m}_{x}']>=80,'>=80'),(R[f'{m}_{x}']<=20,'<=20')]:
            r=R.loc[cond,f'{m}_rel'].dropna(); rest=R.loc[~cond,f'{m}_rel'].dropna()
            if len(r)>=5: print(f'  {m} {lab} {nm}: n={len(r):3d} mean {r.mean():+.3f}% up {100*(r>0).mean():.0f}%  vs rest {rest.mean():+.3f}%  MW p {stats.mannwhitneyu(r,rest).pvalue:.3f}')
print('\n[F] SBM (2004) pooled NQ+ES: release-to-release return on own lag + lagged position change (clustered by week)')
for g in ['dam','dlev']:
    rows=[]
    for m in ['NQ','ES']:
        d=pd.DataFrame({'r':R[f'{m}_rel'],'x':R[f'{m}_{g}'],'rl':R[f'{m}_rel'].shift(1)}).dropna(); d['es']=float(m=='ES'); rows.append(d)
    D=pd.concat(rows); res=sm.OLS(D.r,sm.add_constant(D[['x','rl','es']])).fit(cov_type='cluster',cov_kwds={'groups':D.index.factorize()[0]})
    print(f'  {g}: N={int(res.nobs)} coef {res.params.x:+.4f} t {res.tvalues.x:+.2f} p {res.pvalues.x:.3f}')
print('\n[G] By year, NQ follow-AM rule after release')
d=pd.concat([np.sign(R.NQ_dam).rename('s'),R.NQ_rel.rename('r')],axis=1).dropna(); d=d[d.s!=0]
print('  '+'  '.join(f'{y}: n={len(g)} hit {100*(np.sign(g.r)==g.s).mean():.0f}% long-up {100*(g.r>0).mean():.0f}%' for y,g in d.groupby(d.index.year)))
