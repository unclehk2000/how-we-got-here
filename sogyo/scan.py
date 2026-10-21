import pandas as pd, numpy as np, sys
from scipy.stats import norm
FEATS=['gap_atr','zone_w_atr','settle_toward','open_vs_tdo','tdo_between','zone_tdo_dist','cbdr_atr','zone_in_cbdr','zone_cbdr_sd',
       'asia_atr','on_atr','ldn_swept_asia_hi','ldn_swept_asia_lo','on_swept_pdh','on_swept_pdl','zone_in_prev_range','open_in_prev_range',
       'zone_traded_0700','on_mid_dist','on_trend','b79_atr','b79_dir','ndog_atr','zone_ndog_ce_dist','nwog_atr','zone_nwog_ce_dist',
       'nwog_unfilled','prev_day_with_gap','news830','dow','touch_min']
def two(a,b):
    a=a.dropna(); b=b.dropna(); p1,p2=a.mean(),b.mean(); n1,n2=len(a),len(b)
    p=(a.sum()+b.sum())/(n1+n2); se=np.sqrt(p*(1-p)*(1/n1+1/n2)); z=(p1-p2)/se if se>0 else 0
    return p1,p2,n1,n2,z,2*norm.sf(abs(z))
def scan(F,label):
    T=F[F.z_touch==1]; rows=[]
    for f in FEATS:
        x=T[f]
        if x.dropna().nunique()<=2: lo,hi=(x==0),(x==1); labs=('0','1')
        elif f=='dow': lo,hi=x.isin([0,1]),x.isin([3,4]); labs=('Mon-Tue','Thu-Fri')
        else: q1,q2=x.quantile([1/3,2/3]); lo,hi=x<=q1,x>=q2; labs=(f'≤{q1:.2f}',f'≥{q2:.2f}')
        p_hi,p_lo,nh,nl,z,p=two(T.z_hold[hi],T.z_hold[lo])
        # same split on the decoy levels (touched days for each decoy)
        dh=np.nanmean([F.loc[hi.index[hi]].d375_hold.mean(),F.loc[hi.index[hi]].d625_hold.mean()])
        dl=np.nanmean([F.loc[lo.index[lo]].d375_hold.mean(),F.loc[lo.index[lo]].d625_hold.mean()])
        rows.append(dict(feature=f,low=labs[0],hold_low=100*p_lo,n_low=nl,high=labs[1],hold_high=100*p_hi,n_high=nh,
                         diff=100*(p_hi-p_lo),z=z,p=p,decoy_diff=100*(dh-dl),ce_specific=100*(p_hi-p_lo)-100*(dh-dl)))
    R=pd.DataFrame(rows).sort_values('p'); print(f'\n{label}: wall hold rate, high vs low group (touched days n={len(T)}, base {100*T.z_hold.mean():.1f}%) — Bonferroni p<{0.05/len(FEATS):.4f}')
    print(R.round(3).to_string(index=False)); return R
pd.set_option('display.width',250)
if __name__=='__main__':
  for m in sys.argv[1:] or ['NQ','ES']:
      F=pd.read_pickle(f'nyam_{m}.pkl')
      R=scan(F,m); R.to_csv(f'scan_{m}.csv',index=False)
      T=F[F.z_touch==1]
      for g,lab in [(1,'gap UP: zone BELOW price = support / foothold'),(-1,'gap DOWN: zone ABOVE price = resistance vs buyside')]:
          s=T[T.g==g]
          print(f'  {lab}: hold {100*s.z_hold.mean():.1f}% (n {len(s)}), decoy .375 {100*F[F.g==g].d375_hold.mean():.1f}% .625 {100*F[F.g==g].d625_hold.mean():.1f}%, 5-min wall {100*s.wall5.mean():.1f}%, trade mean R {s.trade_R.mean():+.3f}, mean % {s.trade_ret.mean():+.3f}')
