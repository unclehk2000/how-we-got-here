import pandas as pd, numpy as np
from statsmodels.tsa.stattools import grangercausalitytests
import statsmodels.api as sm
c=pd.read_csv('/mnt/user-data/outputs/COT_TFF_NQ_ES_RTY_YM_2015_2026.csv',parse_dates=['report_date'])
for g in ['am','lev']: c[g]=(c[g+'_long']-c[g+'_short'])/c.open_interest*100
P={g:c.pivot(index='report_date',columns='market',values=g) for g in ['am','lev']}
am=P['am'].dropna(); lev=P['lev'].dropna()
print('weeks with all four',len(am),am.index.min().date(),am.index.max().date())
print('\nCorrelation of weekly CHANGES in asset-manager net % OI'); print(am.diff().corr().round(2))
print('\nCorrelation of weekly CHANGES in leveraged-fund net % OI'); print(lev.diff().corr().round(2))
print('\nLevels: mean / sd of AM net % OI'); print(am.agg(['mean','std']).round(1))
d=am.diff().dropna()
for a,b in [('RTY','NQ'),('NQ','RTY')]:
    r=grangercausalitytests(d[[b,a]],maxlag=4)
    print(f'Granger: {a} AM change -> {b} AM change, p by lag 1..4:',[round(r[k][0]['ssr_ftest'][1],3) for k in range(1,5)])
# relative positioning spread
sp=(am.NQ-am.RTY); print('\nAM net NQ minus RTY: now %.1f pts, 52w range %.1f..%.1f, 2017-26 mean %.1f'%(sp.iloc[-1],sp.iloc[-52:].min(),sp.iloc[-52:].max(),sp.mean()))
# persistence of the spread
x=sp.diff().dropna(); X=sm.add_constant(sp.shift().loc[x.index]); b=sm.OLS(x,X).fit()
print('spread mean-reversion beta %.3f (t %.2f) -> half-life %.1f weeks'%(b.params.iloc[1],b.tvalues.iloc[1],np.log(0.5)/np.log(1+b.params.iloc[1])))
