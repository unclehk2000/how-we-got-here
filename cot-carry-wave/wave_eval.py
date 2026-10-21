import pandas as pd, numpy as np, sys
from scipy.stats import binomtest
def pivots(lp,k=3):
    hi=lp.eq(lp.rolling(2*k+1,center=True).max()); lo=lp.eq(lp.rolling(2*k+1,center=True).min()); return hi,lo
def evaluate(F,name):
    lp=np.log1p(F.y).cumsum().where(F.y.notna())
    hi,lo=pivots(lp)
    rows=[]
    for pre,sgn in [('px_w26',1),('px_w52',1),('px_w104',1),('am_w26',1),('am_w52',1),('lev_w26',-1),('lev_w52',-1)]:
        if pre+'_proj' not in F: continue
        s=sgn*np.sign(F[pre+'_proj']); m=s.notna()&F.y.notna()&(s!=0)
        hit=(np.sign(F.y[m])==s[m]).mean(); n=m.sum()
        th=np.arctan2(F[pre+'_osc'],F[pre+'_vel'])%(2*np.pi)       # theta from sin/cos
        # predicted peak this week: phase within [pi/2 - w, pi/2) i.e. about to crest; use vel just turning
        near_pk=(F[pre+'_osc']>0.92)&m; near_tr=(F[pre+'_osc']<-0.92)&m
        pk_hit=(hi|hi.shift(1)|hi.shift(-1))[near_pk].mean(); tr_hit=(lo|lo.shift(1)|lo.shift(-1))[near_tr].mean()
        base_pk=(hi|hi.shift(1)|hi.shift(-1))[m].mean(); base_tr=(lo|lo.shift(1)|lo.shift(-1))[m].mean()
        rows.append([pre,('fade' if sgn<0 else 'follow'),n,100*hit,binomtest(int(round(hit*n)),int(n)).pvalue,
                     100*(F.y[m]>0).mean(),near_pk.sum(),100*pk_hit,100*base_pk,near_tr.sum(),100*tr_hit,100*base_tr])
    print(f'\n{name}: sign of projected one-week wave move vs actual week; and pivot hits when the wave sits at a crest/trough')
    print(pd.DataFrame(rows,columns=['wave','use','n','hit%','p','long%','n@crest','pivotHigh%','base','n@trough','pivotLow%','base']).round(2).to_string(index=False))
    # phase octants of the price wave
    for pre in ['px_w52','am_w52']:
        th=np.arctan2(F[pre+'_osc'],F[pre+'_vel'])%(2*np.pi); oc=(th//(np.pi/4)).astype('Int64')
        g=pd.DataFrame({'oc':oc,'y':F.y}).dropna().groupby('oc').y
        print(pre,'octant (0 = rising through zero, 2 = crest, 4 = falling through zero, 6 = trough):')
        print((g.agg(['count','mean',lambda v:(v>0).mean()]).rename(columns={'<lambda_0>':'up'})*[1,100,100]).round(2).T.to_string())
for m in sys.argv[1:] or ['NQ','ES']:
    evaluate(pd.read_pickle(f'F_{m}.pkl'),m)
