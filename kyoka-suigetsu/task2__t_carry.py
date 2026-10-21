import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np
from scipy import stats
for s in ['NQ','ES','RTY']:
    D=pd.read_pickle(f'F_{s}.pkl')
    D['wk']=D.index.to_period('W-FRI')
    g=D.groupby('wk')
    W=pd.DataFrame({'carry':g.carry.last(),'ctr':g.contract.last(),'ctr0':g.contract.first(),
                    'rng_mean':g.rng.mean(),'hi':g.ah.max(),'lo':g.al.min(),'o':g.ao.first(),'c':g.ac.last(),'c_act':g.c.last(),'n':g.size()})
    W=W[W.n>=3]
    W['wrng']=(W.hi-W.lo)/W.c_act*100
    W['wret']=W.c.diff()/W.c_act.shift(1)*100
    W['dcarry']=W.carry.diff()
    same=(W.ctr==W.ctr.shift(1))&(W.ctr0==W.ctr)      # no roll inside or between the two weeks
    W['dcarry']=W.dcarry.where(same)
    W['next_rng']=W.rng_mean.shift(-1)
    W['rel_next']=np.log(W.next_rng/W.rng_mean.rolling(4).mean())   # next week vs the trailing 4 weeks
    W['next_ret']=W.wret.shift(-1)
    d=W.dropna(subset=['dcarry','rel_next'])
    print(f'\n== {s}: weekly carry change vs next week ({len(d)} weeks without a roll) ==')
    for a,b in [(2010,2017),(2018,2026),(2010,2026)]:
        x=d[(d.index.year>=a)&(d.index.year<=b)]
        r1=stats.spearmanr(x.dcarry.abs(),x.rel_next); r2=stats.spearmanr(x.dcarry,x.rel_next); r3=stats.spearmanr(x.dcarry,x.next_ret)
        print(f'  {a}-{b} n={len(x)}: |Δcarry|→next-week range rho {r1[0]:+.3f} (p {r1[1]:.2f}) · Δcarry→next-week range {r2[0]:+.3f} (p {r2[1]:.2f}) · Δcarry→next-week return {r3[0]:+.3f} (p {r3[1]:.2f})')
    # carry level vs next-month return, vs always long
    D['mo']=D.index.to_period('M')
    M=D.groupby('mo').agg(carry=('carry','last'),ac=('ac','last'),c=('c','last'))
    M['ret']=M.ac.diff()/M.c.shift(1)*100; M['next']=M.ret.shift(-1)
    M=M.dropna()
    r=stats.spearmanr(M.carry,M.next); print(f'  carry level → next-month return: rho {r[0]:+.3f} (p {r[1]:.2f}), n={len(M)}')
    # abnormal carry: deviation from its own 26-week median, i.e. what the rate path alone doesn't explain
    W['cdev']=W.carry-W.carry.rolling(26).median()
    x=W.dropna(subset=['cdev','rel_next'])
    r=stats.spearmanr(x.cdev,x.rel_next); print(f'  carry vs its 26-wk median → next-week range: rho {r[0]:+.3f} (p {r[1]:.2f})')

print('\n\n== controlled test: next-week log range vs Δcarry, controlling for this week\'s return and range ==')
import statsmodels.api as sm
for s in ['NQ','ES','RTY']:
    D=pd.read_pickle(f'F_{s}.pkl'); D['wk']=D.index.to_period('W-FRI'); g=D.groupby('wk')
    W=pd.DataFrame({'carry':g.carry.last(),'ctr':g.contract.last(),'ctr0':g.contract.first(),'rng_mean':g.rng.mean(),'ac':g.ac.last(),'c':g.c.last(),'n':g.size()})
    W=W[W.n>=3]
    W['wret']=W.ac.diff()/W.c.shift(1)*100
    same=(W.ctr==W.ctr.shift(1))&(W.ctr0==W.ctr)
    W['dcarry']=W.carry.diff().where(same)
    W['lr']=np.log(W.rng_mean); W['lr_next']=W.lr.shift(-1)
    W['lr4']=W.lr.rolling(4).mean(); W['lr12']=W.lr.rolling(12).mean()
    W['neg']=np.minimum(W.wret,0); W['absr']=W.wret.abs()
    d=W.dropna(subset=['dcarry','lr_next','lr4','lr12'])
    for a,b in [(2010,2017),(2018,2026)]:
        x=d[(d.index.year>=a)&(d.index.year<=b)]
        X=sm.add_constant(x[['lr','lr4','lr12','neg','absr','dcarry']])
        m=sm.OLS(x.lr_next,X).fit(cov_type='HAC',cov_kwds={'maxlags':4})
        print(f'  {s} {a}-{b}: Δcarry coef {m.params.dcarry:+.3f} (t {m.tvalues.dcarry:+.2f}); corr(Δcarry, this-week return) {stats.spearmanr(x.dcarry,x.wret)[0]:+.2f}')
