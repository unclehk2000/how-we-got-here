"""NY AM foothold trade at the twin zone vs a random-entry placebo with identical stop/target distances.
Trade: on first NY AM touch of Z, enter in the gap direction (long on gap-up = zone as support), stop at the 0.75 level
(0.25 gap beyond the zone), target the 09:30 open (0.5 gap = 2R), exit 10:59 close. R before costs."""
import pandas as pd, numpy as np, pickle, sys
rng=np.random.default_rng(7)
def sim(h,l,c,i,side,ent,stop,tgt,n):
    for j in range(i+1,n):
        hs=(l[j]<=stop) if side>0 else (h[j]>=stop); ht=(h[j]>=tgt) if side>0 else (l[j]<=tgt)
        if hs: return (stop-ent)*side
        if ht: return (tgt-ent)*side
    return (c[n-1]-ent)*side
for m in sys.argv[1:] or ['NQ','ES']:
    F=pd.read_pickle(f'nyam_{m}.pkl'); rth,paths=pickle.load(open(f'twin_{m}.pkl','rb'))
    T=F[F.z_touch==1]; rows=[]
    for d,r in T.iterrows():
        x=paths[d]; hm=x.index.values; n=(hm<=1059).sum(); h,l,c=x.High.values,x.Low.values,x.Close.values
        g=r.g; sd=abs(r.Z-(r.O+0.75*(r.Cm-r.O))); td=abs(r.O-r.Z)
        pr=[]
        for _ in range(40):
            i=rng.integers(0,n-6); e=c[i]
            pr.append(sim(h,l,c,i,g,e,e-g*sd,e+g*td,n)/sd)
        i0=int(r.touch_min); after=(h[i0+1:n].max() if g>0 else l[i0+1:n].min()) if i0+1<n else np.nan
        rows.append(dict(day=d,g=g,R=r.trade_R,placebo_R=np.mean(pr),
                         beyond_open=float((after>r.O) if g>0 else (after<r.O)) if i0+1<n else np.nan,
                         touch_to_1059=100*g*(c[n-1]-r.Z)/r.O))
    Q=pd.DataFrame(rows).set_index('day')
    def line(s,lab):
        t=s.R.mean()/s.R.std()*np.sqrt(len(s)); tp=(s.R-s.placebo_R).mean()/(s.R-s.placebo_R).std()*np.sqrt(len(s))
        print(f'  {lab:44s} n {len(s):4d} | zone trade {s.R.mean():+.3f}R (t {t:+.2f}) | random entry {s.placebo_R.mean():+.3f}R | difference t {tp:+.2f} | price beyond the open after touch {100*s.beyond_open.mean():.1f}%')
    print(f'\n{m}')
    line(Q,'all touched days')
    line(Q[Q.g>0],'gap UP: long off the zone (foothold)')
    line(Q[Q.g<0],'gap DOWN: short off the zone (vs buyside)')
    for y,s in Q.groupby(Q.index.year): line(s,f'  {y}')
    F2=F[F.z_touch==1]
    print('  NY AM always-long (09:30->10:59) on the same days: mean %+.3f%%, gap-up days %+.3f%%, gap-down days %+.3f%%'%(F2.nyam_long.mean(),F2[F2.g>0].nyam_long.mean(),F2[F2.g<0].nyam_long.mean()))
    Q.to_pickle(f'foothold_{m}.pkl')
