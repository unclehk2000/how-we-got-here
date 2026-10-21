"""Asset-manager follow-up across horizons: regression of the k-week return after release on COT terms,
Newey-West t (lag k), plus non-overlapping hit rates."""
import pandas as pd, numpy as np, sys
import statsmodels.api as sm
def fwd(y,k): return sum(y.shift(-j) for j in range(k))
rows=[]
for m in sys.argv[1:] or ['NQ','ES']:
    F=pd.read_pickle(f'F_{m}.pkl')
    for k in (1,2,4,8,13):
        yk=fwd(F.y,k)
        for x in ['am_d1','am_d4','am_z52','am_i52','lev_d1','lev_z52','rty_am_d1','am_minus_rty_d1','am_w52_proj','lev_w52_proj']:
            if x not in F: continue
            d=pd.DataFrame({'y':yk,'x':F[x]}).replace([np.inf,-np.inf],np.nan).dropna()
            if len(d)<60: continue
            z=(d.x-d.x.mean())/d.x.std()
            r=sm.OLS(d.y*100,sm.add_constant(z)).fit(cov_type='HAC',cov_kwds={'maxlags':k})
            nz=d.iloc[::k]; hit=(np.sign(nz.y)==np.sign(nz.x-nz.x.median() if 'z52' in x or 'i52' in x else nz.x)).mean()
            rows.append([m,k,x,len(d),r.params.iloc[1],r.tvalues.iloc[1],100*hit,100*(nz.y>0).mean(),len(nz)])
R=pd.DataFrame(rows,columns=['mkt','k','feature','n','beta %/sd','NW t','hit% (non-overlap)','long% (non-overlap)','n_no'])
pd.set_option('display.width',200); print(R.round(2).to_string(index=False))
print('\ntests',len(R),'| Bonferroni |t| for p<0.05/%d ≈ %.2f'%(len(R),abs(__import__('scipy.stats',fromlist=['norm']).norm.ppf(0.025/len(R)))))
print('max |t|',R['NW t'].abs().max().round(2))
R.to_csv('am_horizon.csv',index=False)
