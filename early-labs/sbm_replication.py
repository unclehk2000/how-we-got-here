# Sanders, Boris & Manfredo (2004) methodology applied to NQ, TFF asset managers + leveraged funds
import sys, glob, math, numpy as np, pandas as pd, statsmodels.api as sm, warnings; warnings.filterwarnings('ignore')
from datetime import time as T
sys.argv=['x']; exec(open('hydra.py').read().split("# ---------------------------------------------------------------- cli")[0])
U='/mnt/user-data/uploads/'
df=load(glob.glob(U+'NQ_*_1min_continuous.csv')+glob.glob(U+'nq?26_intraday-1min*.csv'))
S=pick_active(sessions(df,T(9,25))); S=S[S.n_rth>=200].copy()
prev=S.shift(1); gap=S.index.to_series().diff().dt.days
S['r_cc']=pd.Series(np.where(S.k==prev.k,np.log(S.rc/prev.rc),np.log(S.rc/S.ro)),index=S.index).where(gap<=4)
S['r_oo']=pd.Series(np.where(S.k==prev.k,np.log(S.ro/prev.ro),np.log(prev.rc/prev.ro)),index=S.index).where(gap<=4)
C=pd.read_csv('COT_NQ_TFF_2015_2026.csv',parse_dates=['report_date']).set_index('report_date')
C['PNL_AM']=(C.am_long-C.am_short)/(C.am_long+C.am_short)*100      # eq (3)
C['PNL_LEV']=(C.lev_long-C.lev_short)/(C.lev_long+C.lev_short)*100
days=S.index
def window_ret(a,b,col):   # sum of daily log returns for sessions in (a,b]; nan if any missing or no session near b
    seg=S.loc[(days>a)&(days<=b),col]
    if len(seg)<3 or seg.isna().any(): return np.nan
    last=seg.index[-1]
    if (b-last).days>3: return np.nan
    first=S.index[S.index.searchsorted(a)-1] if S.index.searchsorted(a)>0 else None
    if first is None or (a-first).days>3: return np.nan
    return 100*seg.sum()
rep=C.index
C['R_tue']=[window_ret(rep[i-1],rep[i],'r_cc') if i>0 else np.nan for i in range(len(rep))]          # paper: Tue close -> Tue close
# realistic: entry first RTH open after Friday release, exit first RTH open after next release
def rel_ret(i):
    if i+1>=len(rep): return np.nan
    a=rep[i]+pd.Timedelta(days=4); b=rep[i+1]+pd.Timedelta(days=4)  # Saturdays after releases
    seg=S.loc[(days>a)&(days<=b+pd.Timedelta(days=2)),'r_oo']          # opens Mon..next Mon
    if len(seg)<4 or seg.isna().any() or (seg.index[0]-a).days>3: return np.nan
    return 100*seg.sum()
C['R_rel']=[rel_ret(i) for i in range(len(rep))]    # return earned AFTER report i is public
C.loc[(C.index>='2025-09-30')&(C.index<='2025-12-31'),'R_rel']=np.nan   # shutdown-delayed releases
print('weeks with Tue-Tue return',C.R_tue.notna().sum(),' with post-release return',C.R_rel.notna().sum())
out={}
print('\n[Table 3] contemporaneous correlation (Tue-Tue), PNL level and weekly change')
for g in ['AM','LEV']:
    m=C[[f'PNL_{g}','R_tue']].dropna(); d=C[f'PNL_{g}'].diff()
    mm=pd.concat([d,C.R_tue],axis=1).dropna()
    r1=m.iloc[:,0].corr(m.R_tue); r2=mm.iloc[:,0].corr(mm.R_tue); n=len(m)
    print(f'  {g:3s} n={n}  corr(PNL,R) {r1:+.3f}   corr(dPNL,R) {r2:+.3f}   (|r|>{1.96/math.sqrt(n):.3f} sig at 5%)')
def build(y,x_own,x_other,m,n):
    X=pd.DataFrame({f'own{i}':C[x_own].shift(i) for i in range(1,m+1)})
    for j in range(1,n+1): X[f'oth{j}']=C[x_other].shift(j)
    Z=pd.concat([C[y],X],axis=1).dropna(); return Z[y],sm.add_constant(Z.drop(columns=y))
def granger(y,x_own,x_other,label):
    # AIC over m,n in 1..12 on a common sample (max lags), then Wald test on x_other lags, White HC errors
    best=None; base=pd.concat([C[y]]+[C[x_own].shift(i) for i in range(1,13)]+[C[x_other].shift(j) for j in range(1,13)],axis=1).dropna().index
    for m in range(1,13):
        for n in range(1,13):
            yy,X=build(y,x_own,x_other,m,n); yy,X=yy.loc[yy.index.isin(base)],X.loc[X.index.isin(base)]
            a=sm.OLS(yy,X).fit().aic
            if best is None or a<best[0]: best=(a,m,n)
    _,m,n=best; yy,X=build(y,x_own,x_other,m,n); r=sm.OLS(yy,X).fit(cov_type='HC0')
    cols=[c for c in X if c.startswith('oth')]; R=np.zeros((len(cols),X.shape[1]))
    for k,c in enumerate(cols): R[k,list(X.columns).index(c)]=1
    w=r.wald_test(R,scalar=True); s=r.params[cols].sum(); ws=r.wald_test(R.sum(0,keepdims=True),scalar=True)
    print(f'  {label:32s} (m,n)=({m},{n}) N={int(r.nobs)}  Wald p={float(w.pvalue):.4f}  impact {"+" if s>0 else "-"}{"*" if float(ws.pvalue)<0.05 else ""} (sum {s:+.4f}, p {float(ws.pvalue):.3f})')
print('\n[Table 4] do returns lead positions?  PNL_t on own lags + lagged R (Tue-Tue)')
for g in ['AM','LEV']: granger(f'PNL_{g}',f'PNL_{g}','R_tue',f'{g}: R -> PNL')
print('\n[Table 6] do positions lead returns?  R_t on own lags + lagged PNL')
for g in ['AM','LEV']:
    granger('R_tue','R_tue',f'PNL_{g}',f'{g}: PNL -> R (Tue-Tue, paper timing)')
print('\n[Table 8] extreme positions: R_t = a0 + a1 LO_t-1 + a2 HI_t-1  (LO/HI = bottom/top 20% of prior 156-week range)')
for g in ['AM','LEV']:
    p=C[f'PNL_{g}']; lo=p.rolling(156).min().shift(1); hi=p.rolling(156).max().shift(1); rng=hi-lo
    C[f'LO_{g}']=((p<=lo+0.2*rng)&rng.notna()).astype(float).where(rng.notna()); C[f'HI_{g}']=((p>=hi-0.2*rng)&rng.notna()).astype(float).where(rng.notna())
    for tgt,lab in [('R_tue','Tue-Tue, next week (paper)'),('R_rel','post-release (tradable)')]:
        yv=C[tgt] if tgt=='R_rel' else C[tgt].shift(-1)          # R_rel row i already = return after report i
        Z=pd.concat([yv.rename('y'),C[f'LO_{g}'],C[f'HI_{g}']],axis=1).dropna()
        r=sm.OLS(Z.y,sm.add_constant(Z.iloc[:,1:])).fit(cov_type='HC0'); f=r.f_test(np.eye(3)[1:])
        print(f'  {g:3s} {lab:28s} N={int(r.nobs)}  const {r.params.const:+.3f}%  LO {r.params.iloc[1]:+.3f}% (n={int(Z.iloc[:,1].sum())}, t {r.tvalues.iloc[1]:+.2f})  HI {r.params.iloc[2]:+.3f}% (n={int(Z.iloc[:,2].sum())}, t {r.tvalues.iloc[2]:+.2f})  F p={float(f.pvalue):.3f}')
print('\n[Extension] positions -> post-release return (tradable timing), simple regressions')
for g in ['AM','LEV']:
    for x in [f'PNL_{g}']:
        Z=pd.concat([C.R_rel.rename('y'),C[x],C[x].diff().rename('d')],axis=1).dropna()
        for c in [x,'d']:
            r=sm.OLS(Z.y,sm.add_constant(Z[[c]])).fit(cov_type='HAC',cov_kwds={'maxlags':2})
            print(f'  {g:3s} {"level" if c==x else "weekly change":13s} N={int(r.nobs)}  coef {r.params.iloc[1]:+.4f}  t {r.tvalues.iloc[1]:+.2f}  p {r.pvalues.iloc[1]:.3f}')
C.to_pickle('cot/sbm.pkl')
