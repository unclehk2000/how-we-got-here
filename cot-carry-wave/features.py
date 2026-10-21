import pandas as pd, numpy as np
from panel import weekly, cot
from wave import fit
MKTS=['NQ','ES','YM','RTY']
WAVE_SPECS=[(26,range(6,27)),(52,range(8,53)),(104,range(13,79))]

def price_frame(mkt):
    w,src=weekly(mkt)
    if w is None: return None
    full=pd.period_range(w.index.min(),w.index.max(),freq='W-FRI')
    w=w.reindex(full)
    lp=np.log1p(w.ret).cumsum()                       # open->close chain; weekend gaps ignored
    lp=lp.where(w.ret.notna())
    gap=lp.isna().groupby(lp.notna().cumsum()).transform('sum')      # length of the NaN run each row sits in
    w['lp_fit']=lp.interpolate(limit_area='inside').where(lp.notna()|(gap<=8))
    w.attrs['src']=src
    return w

def idx(s,n): lo=s.rolling(n,min_periods=n).min(); hi=s.rolling(n,min_periods=n).max(); return 100*(s-lo)/(hi-lo)

def cot_frame(mkt,pref):
    c=cot(mkt).set_index('report_date')
    f=pd.DataFrame(index=c.index)
    for g in ['am','lev']:
        x=c[g+'_net']; f[g]=x; f[g+'_d1']=x.diff(); f[g+'_d4']=x.diff(4)
        for n in (26,52,156): f[f'{g}_i{n}']=idx(x,n)
        f[g+'_z52']=(x-x.rolling(52).mean())/x.rolling(52).std()
        for W,T in WAVE_SPECS[:2]:
            o=fit(x.values,W=W,Tgrid=T)
            for k in ['osc','vel','T','r2','proj']: f[f'{g}_w{W}_{k}']=o[k]
    f['first_week']=c.first_week.values
    f=f[f.first_week.notna()].copy()
    f['wk']=pd.PeriodIndex(f.first_week,freq='W-FRI')
    f=f.drop(columns='first_week').drop_duplicates('wk',keep='last').set_index('wk')
    f.columns=[pref+c for c in f.columns]
    return f

def build(mkt):
    w=price_frame(mkt)
    if w is None: return None
    F=pd.DataFrame(index=w.index)
    F['y']=w.ret                                      # this week's open->close: the thing we forecast
    r=w.ret.shift()                                   # everything below uses data to last Friday only
    F['r1']=r; F['r4']=r.rolling(4).sum(); F['r13']=r.rolling(13).sum()
    F['vol8']=r.abs().rolling(8).mean()
    lp=w.lp_fit.shift()
    F['dd26']=lp-lp.rolling(26).max(); F['du26']=lp-lp.rolling(26).min()
    F['above_sma10']=(lp>lp.rolling(10).mean()).astype(float)
    for W,T in WAVE_SPECS:
        o=fit(w.lp_fit.values,W=W,Tgrid=T)
        for k in ['osc','vel','T','r2','proj']:
            F[f'px_w{W}_{k}']=pd.Series(o[k],index=w.index).shift()
    # own COT, carried forward to every trading week until the next report is out
    own=cot_frame(mkt,'')
    F=F.join(own.reindex(F.index.union(own.index)).ffill().reindex(F.index))
    if mkt!='RTY':
        x=cot_frame('RTY','rty_')[['rty_am','rty_am_d1','rty_am_i52','rty_lev','rty_lev_d1']]
        F=F.join(x.reindex(F.index.union(x.index)).ffill().reindex(F.index))
        F['am_minus_rty_d1']=F.am_d1-F.rty_am_d1
    F['month']=F.index.start_time.month
    F.attrs['src']=w.attrs['src']
    return F

if __name__=='__main__':
    for m in MKTS:
        F=build(m)
        if F is None: print(m,'no price'); continue
        print(m,F.attrs['src'],F.shape,F.y.notna().sum(),'rows with y and am:',(F.y.notna()&F.am.notna()).sum())
        F.to_pickle(f'F_{m}.pkl')
