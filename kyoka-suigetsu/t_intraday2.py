import pandas as pd, numpy as np, statsmodels.api as sm
from har2 import fit, predict, CAL
COLS=['d1','d5','d22','dn1','up1']+CAL
D=pd.read_pickle('F_NQ.pkl')
har=pd.Series(np.nan,index=D.index)
for y in range(2013,2027):
    m,ok=fit(D,COLS,D.year<y); p=predict(D,m,COLS); har[D.year==y]=p[D.year==y]
D['har']=har; D['base30']=np.log(D.rng.rolling(30).median().shift(1))
F=pd.read_pickle('/home/claude/byk/dow_full.pkl'); F['tday']=pd.to_datetime(F.tday); F=F.set_index('tday')
F=F.join(D[['har','base30']],how='inner'); F=F[F.rng>0]; F['lf']=np.log(F.rng)
slots={'20:00':'r20','00:00':'r0','02:00':'r2','05:00':'r5','08:00':'r8','09:00':'r9','10:00':'r10','11:00':'r11','12:00':'r12','14:00':'r14'}
trn=F.year<=2024; tst=F.year>=2025
print('NQ · projecting the final full-day range from what is known at the end of each hour · test 2025–26 · MAE of log range\n')
print(f"{'known at':>8} | {'typical':>7} | {'HAR':>5} | {'so far, scaled by typical share':>31} | {'so far + share + HAR':>20} | {'P25–P75 cover':>13} | {'gain vs typical share':>10}")
rows=[]
for lab,c in slots.items():
    f=F.dropna(subset=['har','base30',c]).copy(); f=f[f[c]>0]
    f['lrun']=np.log(f[c]); f['fmed']=np.log((f[c]/f.rng).rolling(30).median().shift(1)); f['proj']=f.lrun-f.fmed
    f=f.dropna(subset=['fmed'])
    a=f[trn.reindex(f.index,fill_value=False)]; b=f[tst.reindex(f.index,fill_value=False)]
    def e_shift(col):
        c0=(a.lf-a[col]).median(); return (b.lf-b[col]-c0).abs().mean()
    e_typ=e_shift('base30'); e_har=e_shift('har'); e_kyo=e_shift('proj')
    m2=sm.OLS(a.lf,sm.add_constant(a[['proj','har']])).fit(); p2=m2.predict(sm.add_constant(b[['proj','har']])); e2=(b.lf-p2)
    q25,q75=np.percentile(m2.resid,[25,75]); cov=((e2>=q25)&(e2<=q75)).mean()
    rows.append(dict(slot=lab,typical=e_typ,HAR=e_har,share=e_kyo,combo=e2.abs().mean(),cov=cov,w_proj=m2.params.proj,w_har=m2.params.har,const=m2.params.const,q25=q25,q75=q75))
    print(f"{lab:>8} | {e_typ:7.3f} | {e_har:5.3f} | {e_kyo:31.3f} | {e2.abs().mean():20.3f} | {cov*100:12.0f}% | {100*(1-e2.abs().mean()/e_kyo):9.1f}%   weights so-far {m2.params.proj:.2f} · HAR {m2.params.har:.2f}")
pd.DataFrame(rows).to_pickle('intraday_weights.pkl')
