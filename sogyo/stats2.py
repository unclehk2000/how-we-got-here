"""Ladder test: is the 0.5 of the gap special?  Levels at fractions f of each gap, measured from the open.
Race starts on the bar AFTER the touch (the touch bar itself is excluded to avoid crediting its pre-touch extreme)."""
import pandas as pd, numpy as np, pickle, sys
FR=[0.25,0.375,0.5,0.625,0.75]; K=[0.05,0.10,0.20]
def first_touch(h,l,L):
    m=np.where((l<=L)&(h>=L))[0]; return m[0] if len(m) else -1
def race(h,l,i,L,O,k,horizon=60):
    s=np.sign(O-L); hold_lvl=L*(1+s*k/100); thr_lvl=L*(1-s*k/100)
    for j in range(i+1,min(i+1+horizon,len(h))):
        hold=(h[j]>=hold_lvl) if s>0 else (l[j]<=hold_lvl); thr=(l[j]<=thr_lvl) if s>0 else (h[j]>=thr_lvl)
        if hold and thr: return 0.5
        if hold: return 1.0
        if thr: return 0.0
    return np.nan
def run(m):
    rth,paths=pickle.load(open(f'twin_{m}.pkl','rb')); out=[]
    for d,r in rth.iterrows():
        x=paths[d]; hm=x.index.values; n=(hm<=1614).sum(); h=x.High.values[:n]; l=x.Low.values[:n]; O=r.O
        rec=dict(day=d,O=O,gap1=100*(O-r.C1)/O,gap2=100*(O-r.C2)/O,settle=100*(r.C2-r.C1)/O)
        for g,C in [('g1',r.C1),('g2',r.C2)]:
            if abs(O-C)/O<0.0004: continue                         # gap under 0.04%: no ladder
            for f in FR:
                L=O+f*(C-O); t=first_touch(h,l,L); rec[f'{g}_{f}_t']=t
                if t>=0:
                    for k in K: rec[f'{g}_{f}_h{k}']=race(h,l,t,L,O,k)
        out.append(rec)
    return pd.DataFrame(out).set_index('day')
if __name__=='__main__':
    for m in sys.argv[1:] or ['NQ','ES']:
        S=run(m); S.to_pickle(f'ladder_{m}.pkl')
        print(f'\n{m}: hold rate after first touch (k% back toward open before k% beyond) — fraction of gap measured from the open')
        for g in ['g1','g2']:
            for k in K:
                row=[f'{f}: {100*S[f"{g}_{f}_h{k}"].mean():.1f}' for f in FR]
                print(f'  {"RTH " if g=="g1" else "RTH2"} gap, ±{k}%:  '+'  '.join(row))
            print('   touch rate:   '+'  '.join([f'{f}: {100*(S[f"{g}_{f}_t"]>=0).mean():.1f}' for f in FR]),' n',S[f'{g}_0.5_t'].notna().sum())
