import pandas as pd, numpy as np
from scipy import stats
rng=np.random.default_rng(7)
M=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
for s in ['NQ','ES','RTY']:
    D=pd.read_pickle(f'F_{s}.pkl')
    # roll-free monthly return from back-adjusted closes, as % of the prior month's actual close
    me=D.groupby(D.index.to_period('M')).agg(ac=('ac','last'),c=('c','last'))
    me['ret']=(me.ac.diff())/me.c.shift(1)*100
    me=me.dropna(); me=me[me.index<pd.Period('2026-10','M')]   # completed months only
    me['m']=me.index.month; me['y']=me.index.year
    print(f'\n== {s} monthly net % ({me.y.min()}-{me.y.max()}, n per month {me.groupby("m").size().min()}-{me.groupby("m").size().max()}) ==')
    g=me.groupby('m').ret
    tab=pd.DataFrame({'mean':g.mean(),'median':g.median(),'up%':g.apply(lambda x:(x>0).mean()*100)}).round(2)
    tab.index=M; print(tab.T.to_string())
    # dispersion of monthly means vs a null where returns are shuffled across months
    obs=g.mean().std()
    null=[]
    r=me.ret.values
    for _ in range(5000):
        p=rng.permutation(r); null.append(pd.Series(p).groupby(me.m.values).mean().std())
    print(f'  spread of month means {obs:.2f}pp; null p={np.mean(np.array(null)>=obs):.3f}')
    # split-half stability
    a=me[me.y<=2017].groupby('m').ret.mean(); b=me[me.y>=2018].groupby('m').ret.mean()
    rho=stats.spearmanr(a,b)[0]; print(f'  rank corr of month means 2010-17 vs 2018-26: {rho:+.2f}')
    # rule test: long only in months with positive train mean (2010-17) vs always long, in 2018-26
    good=a[a>0].index
    te=me[me.y>=2018]
    rule=te.ret.where(te.m.isin(good),0.0)
    print(f'  2018-26: always-long {te.ret.sum():.1f}% (sum of monthly %), seasonal-long {rule.sum():.1f}% in {te.m.isin(good).mean()*100:.0f}% of months; '
          f'Sharpe {te.ret.mean()/te.ret.std()*np.sqrt(12):.2f} vs {rule.mean()/rule.std()*np.sqrt(12):.2f}')
    # months significantly different from the all-month mean (t-test, Bonferroni 12)
    sig=[(M[m-1],round(stats.ttest_1samp(x,me.ret.mean()).pvalue*12,3)) for m,x in g if stats.ttest_1samp(x,me.ret.mean()).pvalue*12<0.10]
    print('  months with Bonferroni p<0.10 vs all-month mean:',sig if sig else 'none')

    # range seasonality: monthly median daily range relative to the trailing 60-day median range before the month
    D2=D[(D.rvol>0.4)|D.rvol.isna()].copy()
    D2['base']=D2.rng.rolling(60).median().shift(1)
    first=D2.groupby(D2.index.to_period('M')).base.transform('first')
    D2['rel']=D2.rng/first
    mr=D2.groupby([D2.index.year,D2.index.month]).rel.median().unstack()
    A=mr.loc[2010:2017].median(); B=mr.loc[2018:2026].median()
    print('  range vs trailing 60d (median) 2010-17:', dict(zip(M,A.round(2))))
    print('                                 2018-26:', dict(zip(M,B.round(2))))
    print(f'  rank corr {stats.spearmanr(A,B)[0]:+.2f}')
