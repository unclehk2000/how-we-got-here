import pandas as pd, numpy as np, statsmodels.api as sm, itertools, math, warnings
from datetime import date
warnings.filterwarnings('ignore')
S=pd.read_pickle('daily.pkl')
prev=S.shift(1); gapdays=(S.index.to_series().diff().dt.days)
ok_prev=(gapdays<=4)&(S.nq_k==prev.nq_k)          # continuous, same contract
P=lambda a,b:100*(a-b)/b
D=pd.DataFrame(index=S.index)
# dependent: NQ RTH open->close %
D['y']=P(S.nq_rc,S.nq_ro)
# f (flow): NQ overnight move, prior RTH close -> 9:30 open
D['f_on']=np.where(ok_prev,P(S.nq_ro,prev.nq_rc),np.nan)
# rate-differential proxy: DXY. j=0 = overnight DXY move; lags = DXY RTH move
D['dxy_on']=np.where(ok_prev&(S.dx_k==prev.dx_k),P(S.dx_ro,prev.dx_rc),np.nan)
D['dxy_rth']=P(S.dx_rc,S.dx_ro)
# basis proxy: NQ-minus-ES relative move (cross-index basis)
es_on=np.where(ok_prev&(S.es_k==prev.es_k),P(S.es_ro,prev.es_rc),np.nan)
D['cis_on']=D.f_on-es_on
D['cis_rth']=D.y-P(S.es_rc,S.es_ro)
# volatility: log range %
D['sig_rth']=np.log(100*(S.nq_rh-S.nq_rl)/S.nq_ro)
D['sig_on']=np.log(100*(S.nq_oh-S.nq_ol)/S.nq_ro)
D['dsig_on']=D.sig_on-D.sig_on.shift(1)            # j=0: overnight vol change
D['dsig_rth']=D.sig_rth-D.sig_rth.shift(1)
# z_t: calendar controls
nfp=set()
for y in range(2023,2027):
    for m in range(1,13):
        c=[d for d in S.index if d.year==y and d.month==m and d.weekday()==4]
        if c: nfp.add(c[0])
fomc=pd.to_datetime(['2023-02-01','2023-03-22','2023-05-03','2023-06-14','2023-07-26','2023-09-20','2023-11-01','2023-12-13',
 '2024-01-31','2024-03-20','2024-05-01','2024-06-12','2024-07-31','2024-09-18','2024-11-07','2024-12-18',
 '2025-01-29','2025-03-19','2025-05-07','2025-06-18','2025-07-30','2025-09-17','2025-10-29','2025-12-10',
 '2026-01-28','2026-03-18','2026-04-29','2026-06-17','2026-07-29'])
D['z_nfp']=D.index.isin(list(nfp)).astype(float)
D['z_fomc']=D.index.isin(fomc).astype(float)
for i,n in enumerate(['mon','tue','wed','thu']): D['z_'+n]=(D.index.weekday==i).astype(float)
# continuity mask for lags: lag k valid only if all k previous rows are contiguous trading days
cont=(gapdays<=4).astype(int)
def lag(s,k):
    v=s.shift(k); okk=cont.rolling(k).min()==1
    return v.where(okk)
def design(p,q,dep='y',absmode=False):
    X=pd.DataFrame(index=D.index)
    tr=(lambda s:s.abs()) if absmode else (lambda s:s)
    for i in range(1,p+1): X[f'phi_y_l{i}']=lag(D[dep],i) if dep!='y' or not absmode else lag(D.y.abs(),i)
    X['beta_dxy_l0']=tr(D.dxy_on); X['gam_cis_l0']=tr(D.cis_on); X['del_dsig_l0']=D.dsig_on; X['eta_f_l0']=tr(D.f_on)
    for j in range(1,q+1):
        X[f'beta_dxy_l{j}']=tr(lag(D.dxy_rth,j)); X[f'gam_cis_l{j}']=tr(lag(D.cis_rth,j))
        X[f'del_dsig_l{j}']=lag(D.dsig_rth,j);   X[f'eta_f_l{j}']=tr(lag(D.f_on,j))
    for c in [c for c in D if c.startswith('z_')]: X['lam_'+c[2:]]=D[c]
    X=sm.add_constant(X); y=D[dep] if not absmode else D['sig_rth']
    m=X.notna().all(1)&y.notna(); return X[m],y[m]
D.to_pickle('vars.pkl')
# (model.py section above)
def wilson(k,n,z=1.96):
    p=k/n; d=1+z*z/n; c=p+z*z/(2*n); a=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)); return (c-a)/d,(c+a)/d
results={}
for label,dep,absm in [('RETURN  (y = NQ RTH open->close %)','y',False),('VOLATILITY (y = log NQ RTH range %)','sig_rth',True)]:
    print('\n'+'='*96+'\n'+label+'\n'+'='*96)
    train_end=pd.Timestamp('2024-12-31')
    best=None
    for p,q in itertools.product([1,2,3],[0,1,2]):
        X,y=design(p,q,dep,absm); m=X.index<=train_end
        r=sm.OLS(y[m],X[m]).fit()
        if best is None or r.bic<best[0]: best=(r.bic,p,q)
    _,p,q=best; print(f'BIC-selected lags (2023-24 training): p={p}, q={q}')
    X,y=design(p,q,dep,absm)
    full=sm.OLS(y,X).fit(cov_type='HAC',cov_kwds={'maxlags':5})
    print(f'Full-sample fit n={int(full.nobs)}  R2={full.rsquared:.4f}  adjR2={full.rsquared_adj:.4f}')
    tab=pd.DataFrame({'coef':full.params,'t(HAC)':full.tvalues,'p':full.pvalues}).round(4)
    print(tab.to_string())
    print('\nJoint Wald tests by block (HAC):')
    for blk in ['phi','beta','gam','del','eta','lam']:
        cols=[c for c in X if c.startswith(blk)]
        if not cols: continue
        R=np.zeros((len(cols),X.shape[1]))
        for i,c in enumerate(cols): R[i,list(X.columns).index(c)]=1
        w=full.wald_test(R,scalar=True); print(f'  {blk:5s} ({len(cols)} terms): F={float(w.statistic):.2f}  p={float(w.pvalue):.4f}')
    # walk-forward: expanding window, refit monthly, OOS 2025-01 .. 2026-08
    preds=[]; months=pd.period_range('2025-01','2026-08',freq='M')
    for mo in months:
        tr=X.index<mo.start_time; te=(X.index>=mo.start_time)&(X.index<=mo.end_time)
        if te.sum()==0: continue
        r=sm.OLS(y[tr],X[tr]).fit()
        bench=y[tr].mean()
        preds.append(pd.DataFrame({'y':y[te],'yhat':r.predict(X[te]),'bench':bench}))
    O=pd.concat(preds)
    sse=((O.y-O.yhat)**2).sum(); sseb=((O.y-O.bench)**2).sum()
    print(f'\nWalk-forward OOS (2025-01 -> 2026-08), n={len(O)}:  OOS R2 vs expanding-mean benchmark = {1-sse/sseb:.4f}')
    print(f'  Corr(forecast, actual) = {O.y.corr(O.yhat):.3f}')
    if not absm:
        hit=((np.sign(O.yhat)==np.sign(O.y))&(O.y!=0)).sum(); n=(O.y!=0).sum(); lo,hi=wilson(hit,n)
        print(f'  Directional hit rate = {hit}/{n} = {hit/n*100:.1f}%  (CI {lo*100:.1f}-{hi*100:.1f}%)')
        upbase=(O.y>0).mean()*100; print(f'  Naive "always long" hit rate = {upbase:.1f}%')
        strat=(np.sign(O.yhat)*O.y); print(f'  Sign-of-forecast RTH strategy: total {strat.sum():+.1f}%  mean/day {strat.mean():+.3f}%  vs always-long {O.y.sum():+.1f}%')
        q5=pd.qcut(O.yhat,5,labels=False); print('  Actual mean RTH % by forecast quintile:',O.groupby(q5).y.mean().round(3).to_dict())
    else:
        q5=pd.qcut(O.yhat,5,labels=False)
        print('  Actual RTH range % by forecast quintile:',np.exp(O.groupby(q5).y.mean()).round(3).to_dict())
    results[dep]=(full,O)
pd.to_pickle(results,'results.pkl')
# (model.py section above)
def wf(X,y,start='2025-01'):
    out=[]
    for mo in pd.period_range(start,'2026-08',freq='M'):
        tr=X.index<mo.start_time; te=(X.index>=mo.start_time)&(X.index<=mo.end_time)
        if te.sum()==0: continue
        r=sm.OLS(y[tr],X[tr]).fit(); out.append(pd.DataFrame({'y':y[te],'yhat':r.predict(X[te]),'b':y[tr].mean()}))
    return pd.concat(out)
# --- Vol: full equation vs AR(3)-only vs AR(3)+calendar
X,y=design(3,0,'sig_rth',True)
specs={'AR(3) lagged vol only':[c for c in X if c.startswith('phi')]+['const'],
       'AR(3) + calendar z_t':[c for c in X if c.startswith(('phi','lam'))]+['const'],
       'Full equation':list(X.columns)}
print('VOLATILITY model — walk-forward OOS, same 324 days')
base=None
for k,cols in specs.items():
    O=wf(X[cols],y); mse=((O.y-O.yhat)**2).mean()
    if base is None: base=mse
    print(f'  {k:24s} MSE={mse:.4f}  OOS R2 vs mean={1-((O.y-O.yhat)**2).sum()/((O.y-O.b)**2).sum():.3f}  MSE vs AR-only={(1-mse/base)*100:+.1f}%')
# --- Return: does the DXY lag survive alone?
X,y=design(1,2,'y',False)
for cols,name in [(['const','beta_dxy_l1'],'prior-day DXY RTH move only'),(['const','phi_y_l1'],'prior-day NQ RTH return only'),(['const','eta_f_l0'],'overnight NQ move only')]:
    O=wf(X[cols],y); hit=((np.sign(O.yhat)==np.sign(O.y))&(O.y!=0)).mean()*100
    print(f'RETURN  {name:30s} OOS R2={1-((O.y-O.yhat)**2).sum()/((O.y-O.b)**2).sum():+.4f}  hit={hit:.1f}%')
# stability of beta_dxy_l1 by year
print('\nbeta_dxy_l1 coefficient by sub-period (full return spec):')
for a,b in [('2023','2023'),('2024','2024'),('2025','2025'),('2026','2026')]:
    m=(X.index.year>=int(a))&(X.index.year<=int(b)); r=sm.OLS(y[m],X[m]).fit(cov_type='HAC',cov_kwds={'maxlags':5})
    print(f'  {a}: coef={r.params.beta_dxy_l1:+.3f}  t={r.tvalues.beta_dxy_l1:+.2f}  n={int(r.nobs)}')
