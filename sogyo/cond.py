import pandas as pd, numpy as np, pickle, sys
from summary import wil
def rate(b):
    b=b.dropna().astype(float); k=b.sum(); n=len(b)
    if n==0: return 'n 0'
    lo,hi=wil(k,n); return f'{100*k/n:.1f}% (n {n}, {lo:.0f}–{hi:.0f})'
def build(m):
    rth,paths=pickle.load(open(f'twin_{m}.pkl','rb')); out=[]
    for d,r in rth.iterrows():
        x=paths[d]; hm=x.index.values; n=(hm<=1614).sum(); h=x.High.values; l=x.Low.values; c=x.Close.values; O=r.O
        g=np.sign(O-r.C1)
        if g==0: continue
        zlo,zhi=sorted([r.CE1,r.CE2]); near=r.CE1 if abs(O-r.CE1)<abs(O-r.CE2) else r.CE2; far=r.CE2 if near==r.CE1 else r.CE1
        def t_touch(L,lim=n):
            mm=np.where((l[:lim]<=L)&(h[:lim]>=L))[0]; return mm[0] if len(mm) else -1
        i10=np.searchsorted(hm,1000)                        # first bar at/after 10:00
        rec=dict(day=d,O=O,g=g,gap=100*(O-r.C1)/O,settle=100*(r.C2-r.C1)/O,width=100*(zhi-zlo)/O,
                 t_near=t_touch(near),t_far=t_touch(far),t_c1=t_touch(r.C1),
                 p10=c[i10-1],close=c[n-1],close2=c[-1])
        rec['toward']=abs(r.C2-O)<abs(r.C1-O)               # settlement window moved toward today's open
        rec['split']=np.sign(O-r.C1)!=np.sign(O-r.C2)
        out.append(rec)
    S=pd.DataFrame(out).set_index('day')
    S['go']=(np.sign(S.close-S.O)==S.g)                     # RTH closes beyond the open in the gap's direction
    S['r_10_close']=100*(S.close-S.p10)/S.O*S.g             # 10:00 -> 16:14, signed in gap direction
    S['r_10_close_long']=100*(S.close-S.p10)/S.O
    return S
if __name__=='__main__':
    for m in sys.argv[1:] or ['NQ','ES']:
        S=build(m); S.to_pickle(f'cond_{m}.pkl'); A=S[~S.split]
        print(f'\n===== {m} (aligned days {len(A)}) =====')
        q=A.width.quantile(.75)
        for lab,sub in [('all aligned',A),(f'wide zone (width ≥ {q:.3f}%, top quartile)',A[A.width>=q]),('narrow zone',A[A.width<q])]:
            tn=sub.t_near>=0; tf=sub.t_far>=0
            print(f' {lab:40s} near touched {rate(tn)} | far | near {rate(tf[tn])} | full RTH fill {rate(sub.t_c1>=0)}')
        for lab,sub in [('settlement moved TOWARD today\'s open',A[A.toward]),('settlement moved AWAY from today\'s open',A[~A.toward])]:
            print(f' {lab:40s} near touched {rate(sub.t_near>=0)} | full RTH fill {rate(sub.t_c1>=0)} | RTH closes gap-direction {rate(sub.go)}')
        print(' -- the 10:00 test --')
        z10=A.t_near.between(0,29)
        for lab,sub in [('zone touched 09:30–09:59',A[z10]),('zone NOT touched by 10:00',A[~z10])]:
            print(f' {lab:30s} n {len(sub)} | RTH close in gap direction {rate(sub.go)} | 10:00→16:14 in gap dir {sub.r_10_close.mean():+.3f}% (up-days long {100*(sub.r_10_close_long>0).mean():.1f}%)')
        print(' unconditional 10:00→16:14 long: mean %+.3f%%, up %.1f%%'%(A.r_10_close_long.mean(),100*(A.r_10_close_long>0).mean()))
