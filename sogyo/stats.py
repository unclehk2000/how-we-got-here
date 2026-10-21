import pandas as pd, numpy as np, pickle, sys
K=[0.05,0.10,0.20]       # race thresholds, % of open
def first_touch(h,l,L,start=0):
    m=np.where((l[start:]<=L)&(h[start:]>=L))[0]
    return start+m[0] if len(m) else -1
def race(h,l,i,L,O,k,horizon=60):
    """after touching L at bar i: which comes first, k% back toward the open (hold) or k% beyond L (through)"""
    s=np.sign(O-L)                      # +1 if open is above L
    up=L*(1+s*k/100); dn=L*(1-s*k/100)    # 'hold' target toward open, 'through' target away
    for j in range(i,min(i+horizon,len(h))):
        hold=(h[j]>=up) if s>0 else (l[j]<=up)
        thr=(l[j]<=dn) if s>0 else (h[j]>=dn)
        if hold and thr: return 0.5
        if hold: return 1.0
        if thr: return 0.0
    return np.nan
def day_stats(mkt):
    rth,paths=pickle.load(open(f'twin_{mkt}.pkl','rb'))
    out=[]
    for d,r in rth.iterrows():
        x=paths[d]; hm=x.index.values; h=x.High.values; l=x.Low.values; c=x.Close.values
        n_rth=(hm<=1614).sum()
        O=r.O; rec=dict(day=d,O=O,C1=r.C1,C2=r.C2,CE1=r.CE1,CE2=r.CE2)
        rec['gap1']=100*(O-r.C1)/O; rec['gap2']=100*(O-r.C2)/O; rec['settle']=100*(r.C2-r.C1)/O
        rec['rth_close']=c[n_rth-1]; rec['rth2_close']=c[-1]
        for name,L in [('CE1',r.CE1),('CE2',r.CE2),('M1',2*O-r.CE1),('M2',2*O-r.CE2),('C1',r.C1),('C2',r.C2)]:
            if abs(L-O)/O<0.0002: rec[name+'_t']=np.nan; continue      # level within 0.02% of the open: no test
            t=first_touch(h,l,L)
            rec[name+'_t']=t if 0<=t<n_rth else (-1 if t<0 else 10000+t)   # 10000+ = touched only in 16:15-16:59
            if 0<=t<n_rth:
                for k in K: rec[f'{name}_hold{k}']=race(h,l,t,L,O,k)
        out.append(rec)
    return pd.DataFrame(out).set_index('day')
if __name__=='__main__':
    for m in sys.argv[1:] or ['NQ','ES']:
        S=day_stats(m); S.to_pickle(f'stats_{m}.pkl'); print(m,len(S))
