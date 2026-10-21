import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np, statsmodels.api as sm
CAL=['tue','wed','thu','fri','opex_day','roll_week','tom','pre_hol','post_hol']
def design2(D):
    X=pd.DataFrame(index=D.index); lr=D.lr
    L=lr.shift(1).rolling(250,min_periods=120).mean()          # slow anchor: last year's typical log range
    X['L']=L
    X['d1']=lr.shift(1)-L
    X['d5']=lr.shift(1).rolling(5).mean()-L
    X['d22']=lr.shift(1).rolling(22).mean()-L
    X['dn1']=np.maximum(-D.ret.shift(1),0)                    # size of yesterday's down move, %
    X['up1']=np.maximum(D.ret.shift(1),0)                     # size of yesterday's up move, %
    for i,n in enumerate(['tue','wed','thu','fri']): X[n]=(D.dow==i+1).astype(int)
    for f in ['opex_day','roll_week','tom','pre_hol','post_hol']: X[f]=D[f]
    return X
def fit(D,cols,mask):
    X=design2(D)[cols]; y=D.lr-design2(D)['L']                 # target: today's log range relative to the anchor
    ok=X.notna().all(axis=1)&y.notna()&((D.rvol>0.4)|D.rvol.isna())
    m=sm.OLS(y[ok&mask],sm.add_constant(X[ok&mask])).fit(cov_type='HAC',cov_kwds={'maxlags':5})
    return m,ok
def predict(D,m,cols):
    X=design2(D); return X['L']+m.predict(sm.add_constant(X[cols],has_constant='add'))
if __name__=='__main__':
    COLS=['d1','d5','d22','dn1','up1']+CAL
    for s in ['NQ','ES','RTY']:
        D=pd.read_pickle(f'F_{s}.pkl')
        print(f'\n== {s}: anchored HAR (relative to last-250-day typical) ==')
        for (a,b),(c,d) in [((2010,2017),(2025,2026)),((2010,2020),(2021,2026)),((2018,2024),(2025,2026)),((2010,2017),(2018,2026))]:
            tr=(D.year>=a)&(D.year<=b); te=(D.year>=c)&(D.year<=d)
            m,ok=fit(D,COLS,tr); p=predict(D,m,COLS); e=(D.lr-p)[ok&te]
            base=np.log(D.rng.rolling(30).median().shift(1)); c0=(D.lr-base)[ok&tr].median(); eb=(D.lr-base-c0)[ok&te]
            q25,q75,q10,q90=np.percentile(m.resid,[25,75,10,90])
            print(f'  train {a}-{b} → test {c}-{d}: MAE {e.abs().mean():.4f} (bias {e.mean():+.3f}) vs Kyōka typical {eb.abs().mean():.4f} → {100*(1-e.abs().mean()/eb.abs().mean()):.1f}% better; P25–P75 cover {((e>=q25)&(e<=q75)).mean()*100:.0f}%, P10–P90 {((e>=q10)&(e<=q90)).mean()*100:.0f}%')
        m,ok=fit(D,COLS,(D.year>=2010)&(D.year<=2024))
        print('  coefficients fit 2010–2024:'); print(pd.DataFrame({'coef':m.params,'t':m.tvalues}).round(3).T.to_string())
        q=np.percentile(m.resid,[10,25,50,75,90]); print('  residual quantiles (log):',q.round(3))
