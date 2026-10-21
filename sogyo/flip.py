"""The behaviour in the 9 Oct 2026 example: price runs THROUGH the CE1/CE2 zone toward the gap fill, then comes back
and the zone CAPS it (a flipped wall), with price consolidating between the zone and the fill.
Through  = price trades beyond the far edge of the zone by 0.125 x gap (i.e. reaches the 0.625 level).
Retest   = first later return to the far edge from the fill side, before 12:00.
Outcome  = symmetric race from the retest: 0.25 gap further toward the fill (wall rejects) vs 0.25 gap back toward the open
           (wall reclaimed); unresolved by 11:59 -> side of the zone at the 11:59 close.
Containment = share of 1-min closes from retest to 11:59 that sit on the fill side of the zone.
Decoys: the same procedure with a single level at 0.375 or 0.625 of the gap."""
import pandas as pd, numpy as np, pickle, sys
def run_level(h,l,c,n,O,Cm,lo_f,hi_f):
    """lo_f/hi_f: zone edges as gap fractions (near, far). returns dict or None"""
    gap=Cm-O; g=-np.sign(gap)                     # g=+1 gap up (fill is below)
    near=O+lo_f*gap; far=O+hi_f*gap; thr=O+(hi_f+0.125)*gap
    beyond=lambda j,L: (l[j]<=L) if g>0 else (h[j]>=L)          # traded further toward the fill than L
    back=lambda j,L: (h[j]>=L) if g>0 else (l[j]<=L)            # traded back toward the open to L
    t1=next((j for j in range(n) if beyond(j,thr)),None)
    if t1 is None: return dict(through=0)
    t2=next((j for j in range(t1+1,n) if back(j,far)),None)
    if t2 is None: return dict(through=1,retest=0)
    rej=far+(gap*0.25); rec=far-(gap*0.25)        # symmetric +/-0.25 gap around the retest point (the far edge)
    out=None
    for j in range(t2+1,n):
        a=beyond(j,rej); b=back(j,rec)
        if a and b: out=0.5; break
        if a: out=1.0; break
        if b: out=0.0; break
    if out is None: out=1.0 if ((c[n-1]<far) if g>0 else (c[n-1]>far)) else 0.0
    cont=np.mean([(c[j]<far) if g>0 else (c[j]>far) for j in range(t2,n)])
    return dict(through=1,retest=1,wall=out,contain=cont,t_through=t1,t_retest=t2)
def run(m,end=1159):
    rth,paths=pickle.load(open(f'twin_{m}.pkl','rb')); rows=[]
    F=pd.read_pickle(f'nyam_{m}.pkl')
    for d,r in rth.iterrows():
        O=r.O; Cm=(r.C1+r.C2)/2
        if np.sign(O-r.C1)!=np.sign(O-r.C2) or abs(O-Cm)/O<0.0010: continue
        x=paths[d]; hm=x.index.values; n=(hm<=end).sum(); h,l,c=x.High.values,x.Low.values,x.Close.values
        # zone edges as fractions of the twin gap (O->Cm): CE1 and CE2 expressed on that scale
        f1=(r.CE1-O)/(Cm-O); f2=(r.CE2-O)/(Cm-O); lo_f,hi_f=min(f1,f2),max(f1,f2)
        rec=dict(day=d,g=np.sign(O-Cm),gap_pct=100*abs(O-Cm)/O,width_pts=abs(r.CE1-r.CE2),width_pct=100*abs(r.CE1-r.CE2)/O)
        w=hi_f-lo_f
        for tag,(a,b) in {'z':(lo_f,hi_f),'d375':(0.375-w/2,0.375+w/2),'d625':(0.625-w/2,0.625+w/2)}.items():
            for k,v in run_level(h,l,c,n,O,Cm,a,b).items(): rec[f'{tag}_{k}']=v
        if d in F.index:
            for k in ['gap_atr','on_atr','zone_w_atr']: rec[k]=F.loc[d,k]
        rows.append(rec)
    return pd.DataFrame(rows).set_index('day')
if __name__=='__main__':
    from summary import wil
    for m in sys.argv[1:] or ['NQ','ES']:
        R=run(m); R.to_pickle(f'flip_{m}.pkl')
        def line(S,lab):
            out=[]
            for t in ['z','d375','d625']:
                w=S[f'{t}_wall'].dropna(); k,n=w.sum(),len(w); lo,hi=wil(k,n) if n else (np.nan,np.nan)
                out.append(f'{t}: {100*k/max(n,1):.1f}% (n {n}{", "+f"{lo:.0f}–{hi:.0f}" if t=="z" else ""}) contain {100*S[f"{t}_contain"].mean():.0f}%')
            print(f'  {lab:38s} '+' | '.join(out))
        print(f'\n{m}: aligned days {len(R)}; zone traded through by 12:00 {100*R.z_through.mean():.1f}%; retested from the fill side {100*R.z_retest.sum()/R.z_through.sum():.1f}% of those')
        line(R,'all')
        line(R[R.g>0],'gap UP (zone caps a rebound = vs buyside)')
        line(R[R.g<0],'gap DOWN (zone = foothold after rally)')
        q=R.width_pct.quantile(.75)
        line(R[R.width_pct>=q],f'wide zone (top quartile, ≥{q:.3f}%)')
        line(R[R.width_pct<q],'narrow zone')
        if 'gap_atr' in R:
            line(R[(R.gap_atr<=0.68)&(R.on_atr<=0.45)],'quiet context (gap≤0.68, ON≤0.45 ATR)')
            line(R[R.gap_atr>0.68],'big gap (>0.68 ATR)')
        line(R[R.z_t_retest<90],'retest before 11:00')
        line(R[R.z_t_retest>=90],'retest 11:00–11:59')
        print('  by year:',R.groupby(R.index.year).z_wall.agg(lambda v:f'{100*v.mean():.0f}% ({v.notna().sum()})').to_dict())
