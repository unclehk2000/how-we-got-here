"""Mechanical trades around the RTH / RTH2 gap midpoints, with ladder placebos (same rules at other gap fractions).
Fills: limit at the level on first touch (touch bar), stop/target checked from the NEXT bar; same-bar stop+target = stop.
Exit at 16:14 close if neither hit. Returns in % of the open, before costs (NQ ~0.01% round trip)."""
import pandas as pd, numpy as np, pickle, sys
def walk(h,l,c,i,entry,side,stop,tgt,n):
    for j in range(i+1,n):
        hs=(l[j]<=stop) if side>0 else (h[j]>=stop); ht=(h[j]>=tgt) if side>0 else (l[j]<=tgt)
        if hs: return side*(stop-entry)
        if ht: return side*(tgt-entry)
    return side*(c[n-1]-entry)
def trades(m,frac_pairs,rule):
    rth,paths=pickle.load(open(f'twin_{m}.pkl','rb')); out=[]
    for d,r in rth.iterrows():
        x=paths[d]; hm=x.index.values; n=(hm<=1614).sum(); h=x.High.values; l=x.Low.values; c=x.Close.values; O=r.O
        gap1=O-r.C1; gap2=O-r.C2
        if np.sign(gap1)!=np.sign(gap2) or abs(gap1)/O<0.001: continue      # aligned days, gap ≥ 0.10%
        g=np.sign(gap1)
        for tag,(f1,f2) in frac_pairs.items():
            A=O-f1*gap1; B=O-f2*gap2                                          # level pair from each gap
            near,far=(A,B) if abs(O-A)<=abs(O-B) else (B,A)
            zone_w=abs(far-near); G=abs(gap1)
            if rule=='fade_far':      # buy (gap up) / sell (gap down) at the far level, target the open, stop 0.25 gap beyond far
                side=g; entry=far; stop=far-g*0.25*G; tgt=O
            elif rule=='break_far':   # first 1-min CLOSE beyond far level -> go with the fill, target prior RTH close, stop back at near level
                side=-g; entry=None; stop=near+g*0.0; tgt=r.C1
            mm=np.where((l[:n]<=far)&(h[:n]>=far))[0]
            if not len(mm): continue
            i=mm[0]
            if rule=='break_far':
                cl=np.where((-g*(c[i:n]-far))>0)[0]
                if not len(cl): continue
                i=i+cl[0]; entry=c[i]
                if -g*(tgt-entry)<=0: continue
            res=walk(h,l,c,i,entry,side,stop,tgt,n)
            out.append(dict(day=d,tag=tag,ret=100*res/O,risk=100*abs(entry-stop)/O,year=d.year,minute=i))
    return pd.DataFrame(out)
PAIRS={'0.5 RTH + 0.5 RTH2 (the model)':(0.5,0.5),'0.375 pair':(0.375,0.375),'0.625 pair':(0.625,0.625),'0.5 RTH only (both = CE1)':(0.5,0.5001)}
if __name__=='__main__':
    for m in sys.argv[1:] or ['NQ','ES']:
        for rule in ['fade_far','break_far']:
            T=trades(m,PAIRS,rule)
            g=T.groupby('tag').agg(n=('ret','size'),win=('ret',lambda r:100*(r>0).mean()),mean=('ret','mean'),
                                   R=('ret',lambda r:(r/T.loc[r.index,'risk']).mean()),sum=('ret','sum'))
            g['t']=T.groupby('tag').ret.apply(lambda r:r.mean()/r.std()*np.sqrt(len(r)))
            print(f'\n{m} {rule}'); print(g.round(3).to_string())
            T.to_pickle(f'bt_{m}_{rule}.pkl')
