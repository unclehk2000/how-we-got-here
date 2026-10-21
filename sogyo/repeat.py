"""Repeated retests of the flipped wall: after each rejection (0.25 gap move toward the fill), the next return to the
far edge is another retest, raced the same way, until 11:59. Same procedure for equal-width decoy zones."""
import pandas as pd, numpy as np, pickle, sys
def races(h,l,c,n,O,Cm,lo_f,hi_f):
    gap=Cm-O; g=-np.sign(gap); far=O+hi_f*gap; thr=O+(hi_f+0.125)*gap
    beyond=lambda j,L:(l[j]<=L) if g>0 else (h[j]>=L); back=lambda j,L:(h[j]>=L) if g>0 else (l[j]<=L)
    t=next((j for j in range(n) if beyond(j,thr)),None)
    if t is None: return []
    out=[]; j0=t
    while True:
        t2=next((j for j in range(j0+1,n) if back(j,far)),None)
        if t2 is None: return out
        rej=far+0.25*gap; rec=far-0.25*gap; res=None
        for j in range(t2+1,n):
            a,b=beyond(j,rej),back(j,rec)
            if a or b: res=(0.5 if a and b else (1.0 if a else 0.0)); end=j; break
        if res is None: return out            # unresolved by 11:59: stop counting
        out.append(res)
        if res<1: return out                  # wall broken: sequence ends
        j0=end
for m in sys.argv[1:] or ['NQ','ES']:
    rth,paths=pickle.load(open(f'twin_{m}.pkl','rb')); rows=[]
    for d,r in rth.iterrows():
        O=r.O; Cm=(r.C1+r.C2)/2
        if np.sign(O-r.C1)!=np.sign(O-r.C2) or abs(O-Cm)/O<0.0010: continue
        x=paths[d]; n=(x.index.values<=1159).sum(); h,l,c=x.High.values,x.Low.values,x.Close.values
        f1=(r.CE1-O)/(Cm-O); f2=(r.CE2-O)/(Cm-O); lo,hi=min(f1,f2),max(f1,f2); w=hi-lo
        rec={'day':d,'wide':100*abs(r.CE1-r.CE2)/O}
        for tag,(a,b) in {'z':(lo,hi),'d375':(0.375-w/2,0.375+w/2),'d625':(0.625-w/2,0.625+w/2)}.items():
            rs=races(h,l,c,n,O,Cm,a,b)
            for k in range(3): rec[f'{tag}_{k+1}']=rs[k] if len(rs)>k else np.nan
        rows.append(rec)
    R=pd.DataFrame(rows).set_index('day'); q=R.wide.quantile(.75)
    print(f'\n{m}: hold rate at the 1st / 2nd / 3rd retest (each given the previous one held)')
    for lab,S in [('all',R),('wide zone',R[R.wide>=q])]:
        print(f'  {lab:9s} '+' | '.join([f'{t}: '+', '.join([f'{100*S[f"{t}_{k}"].mean():.0f}% (n {S[f"{t}_{k}"].notna().sum()})' for k in (1,2,3)]) for t in ['z','d375','d625']]))
