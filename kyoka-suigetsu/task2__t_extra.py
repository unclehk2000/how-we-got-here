import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np, statsmodels.api as sm
from har2 import fit, predict, design2, CAL
COLS=['d1','d5','d22','dn1','up1']+CAL
FS={s:pd.read_pickle(f'F_{s}.pkl') for s in ['NQ','ES','RTY']}
for s,D in FS.items():
    D=D.copy()
    D['nr7']=(D.rng.shift(1)<=D.rng.shift(1).rolling(7).min()).astype(int)
    D['inside']=((D.h.shift(1)<=D.h.shift(2))&(D.l.shift(1)>=D.l.shift(2))).astype(int)
    D['lrvol']=np.log(D.rvol.shift(1)); D['doi5']=D.doi.shift(1).clip(-30,30)
    if s=='RTY': D.loc[D.index<'2017-08-01',['lrvol','doi5']]=np.nan   # pre-CME RTY volume/OI not usable
    others=[o for o in FS if o!=s]
    for o in others:
        X=design2(FS[o]); D[f'{o}_d1']=X['d1']
    X=design2(D); y=D.lr-X['L']
    print(f'\n== {s}: does anything add to the anchored HAR? (HAC t, train 2010–2020; OOS MAE change 2021–26) ==')
    base_m,ok=fit(D,COLS,D.year<=2020)
    for extra in [['nr7'],['inside'],['lrvol'],['doi5'],[f'{o}_d1' for o in others],['lrvol','doi5']]:
        Z=pd.concat([X[COLS],D[extra]],axis=1); okz=Z.notna().all(axis=1)&y.notna()&((D.rvol>0.4)|D.rvol.isna())
        tr=okz&(D.year<=2020); te=okz&(D.year>=2021)
        m=sm.OLS(y[tr],sm.add_constant(Z[tr])).fit(cov_type='HAC',cov_kwds={'maxlags':5})
        m0=sm.OLS(y[tr],sm.add_constant(X[COLS][tr])).fit()
        e=(y-m.predict(sm.add_constant(Z,has_constant='add')))[te]; e0=(y-m0.predict(sm.add_constant(X[COLS],has_constant='add')))[te]
        ts=', '.join(f'{c} {m.params[c]:+.3f} (t {m.tvalues[c]:+.1f})' for c in extra)
        print(f'  + {"/".join(extra):<14} {ts:<60} OOS MAE {e0.abs().mean():.4f} → {e.abs().mean():.4f} ({100*(e.abs().mean()/e0.abs().mean()-1):+.2f}%)')
