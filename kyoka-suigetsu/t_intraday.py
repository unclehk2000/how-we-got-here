import pandas as pd, numpy as np, statsmodels.api as sm
from t_har import design
D=pd.read_pickle('F_NQ.pkl')
cols=['l1','l5','l22','neg1','absr1','tue','wed','thu','fri','opex_day','qopex_day','roll_week','tom','pre_hol','post_hol']
X=design(D)[cols]; ok=X.notna().all(axis=1)&((D.rvol>0.4)|D.rvol.isna())
tr=ok&(D.year<=2017)
m=sm.OLS(D.lr[tr],sm.add_constant(X[tr])).fit()
D['har']=m.predict(sm.add_constant(X,has_constant='add'))
D['base30']=np.log(D.rng.rolling(30).median().shift(1))
F=pd.read_pickle('/home/claude/byk/dow_full.pkl'); F['tday']=pd.to_datetime(F.tday); F=F.set_index('tday')
F=F.join(D[['har','base30']],how='inner')
F=F[(F.rng>0)]
F['lf']=np.log(F.rng)
slots={'20:00':'r20','02:00':'r2','05:00':'r5','08:00':'r8','09:00':'r9','10:00':'r10','12:00':'r12','14:00':'r14'}
trn=F.year<=2024; tst=F.year>=2025
print('NQ · projecting the final full-day range from what is known at the end of each hour (test 2025–26, MAE of log range; lower is better)\n')
print(f"{'known at':>9} | {'typical day (Kyōka)':>19} | {'HAR only':>8} | {'range so far only':>17} | {'so far + HAR':>12} | {'cov P25–P75':>11}")
for lab,c in slots.items():
    f=F.dropna(subset=['har','base30',c]).copy(); f=f[f[c]>0]
    f['lrun']=np.log(f[c])
    # frac of final range achieved by this slot on the last 30 days (Kyōka-style projection run / typical fraction)
    frac=(f[c]/f.rng)
    f['fmed']=np.log(frac.rolling(30).median().shift(1))
    a=f[trn.reindex(f.index,fill_value=False)]; b=f[tst.reindex(f.index,fill_value=False)]
    def mae(pred_tr,pred_te):
        c0=(a.lf-pred_tr).median(); return (b.lf-pred_te-c0).abs().mean()
    e_typ=mae(a.base30,b.base30)
    e_har=mae(a.har,b.har)
    e_kyo=mae(a.lrun-a.fmed,b.lrun-b.fmed)   # running range scaled up by the typical share of the day done
    m1=sm.OLS(a.lf,sm.add_constant(a[['lrun']])).fit(); e_run=(b.lf-m1.predict(sm.add_constant(b[['lrun']]))).abs().mean()
    m2=sm.OLS(a.lf,sm.add_constant(a[['lrun','har']])).fit(); p2=m2.predict(sm.add_constant(b[['lrun','har']])); e2=(b.lf-p2).abs().mean()
    q25,q75=np.percentile(m2.resid,[25,75]); cov=(((b.lf-p2)>=q25)&((b.lf-p2)<=q75)).mean()
    print(f"{lab:>9} | {e_typ:19.3f} | {e_har:8.3f} | {e_run:8.3f} ({e_kyo:.3f}) | {e2:12.3f} | {cov*100:10.0f}%   coefs so-far {m2.params.lrun:.2f} HAR {m2.params.har:.2f}")
