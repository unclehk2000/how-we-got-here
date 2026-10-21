"""CE1/CE2 as a barrier: after price first reaches the twin zone, does it trade AWAY (back to the open)
before it trades THROUGH (to the full gap fill)?  The zone sits exactly halfway, so a driftless market gives 50%.
Split by the four price-delivery states (Expansion / Consolidation / Reversal / Retracement), same day and prior day."""
import pandas as pd, numpy as np, pickle, sys
FR=[0.375,0.5,0.625]
def states(rth,paths):
    rows=[]
    for d,r in rth.iterrows():
        x=paths[d]; x=x[x.index<=1614]
        rows.append(dict(day=d,o=x.Open.iloc[0],h=x.High.max(),l=x.Low.min(),c=x.Close.iloc[-1]))
    S=pd.DataFrame(rows).set_index('day'); S['rng']=S.h-S.l; S['net']=S.c-S.o
    blk=(S.index.to_series().diff().dt.days>10).cumsum()
    S['avg20']=S.groupby(blk).rng.transform(lambda r:r.shift().rolling(20).mean())
    rel=S.rng/S.avg20; dirn=S.net.abs()/S.rng
    st=np.where(rel.isna(),None,np.where((rel>1.25)&(dirn>0.55),'Expansion',np.where(rel<0.75,'Consolidation',
          np.where((np.sign(S.net)!=np.sign(S.net.shift()))&(rel>=1.0),'Reversal','Retracement'))))
    S['state']=st; S['prev_state']=S.state.shift().where(S.index.to_series().diff().dt.days<=4)
    return S
def race(h,l,c,i,O,T,Z,n):
    up=O>T                                        # open above the zone (gap up)
    for j in range(i+1,n):
        away=(h[j]>=O) if up else (l[j]<=O); thr=(l[j]<=T) if up else (h[j]>=T)
        if away and thr: return 0.5,'both'
        if away: return 1.0,'away'
        if thr: return 0.0,'through'
    return (1.0 if (c[n-1]-Z)*(O-Z)>0 else 0.0),'close'   # neither: which side of the zone RTH closed
def tight(h,l,i,Z,O,k,n,hz=60):
    s=np.sign(O-Z); a=Z*(1+s*k/100); t=Z*(1-s*k/100)
    for j in range(i+1,min(n,i+1+hz)):
        A=(h[j]>=a) if s>0 else (l[j]<=a); B=(l[j]<=t) if s>0 else (h[j]>=t)
        if A and B: return 0.5
        if A: return 1.0
        if B: return 0.0
    return np.nan
def run(m):
    rth,paths=pickle.load(open(f'twin_{m}.pkl','rb')); S=states(rth,paths); out=[]
    for d,r in rth.iterrows():
        x=paths[d]; hm=x.index.values; n=(hm<=1614).sum(); h=x.High.values; l=x.Low.values; c=x.Close.values; O=r.O
        Cm=(r.C1+r.C2)/2
        if np.sign(O-r.C1)!=np.sign(O-r.C2) or abs(O-Cm)/O<0.0010: continue     # aligned days, gap >= 0.10%
        rec=dict(day=d,gap=100*(O-Cm)/O,state=S.state.get(d),prev_state=S.prev_state.get(d))
        for f in FR:
            L=O+f*(Cm-O); T=O+2*f*(Cm-O)
            mm=np.where((l[:n]<=L)&(h[:n]>=L))[0]
            rec[f'touch_{f}']=len(mm)>0
            if len(mm):
                v,how=race(h,l,c,mm[0],O,T,L,n); rec[f'away_{f}']=v; rec[f'how_{f}']=how; rec[f'min_{f}']=mm[0]
                if f==0.5:
                    for k in (0.05,0.10,0.20): rec[f'tight{k}']=tight(h,l,mm[0],L,O,k,n)
        out.append(rec)
    return pd.DataFrame(out).set_index('day'),S
if __name__=='__main__':
    for m in sys.argv[1:] or ['NQ','ES']:
        B,S=run(m); B.to_pickle(f'barrier_{m}.pkl'); S.to_pickle(f'states_{m}.pkl')
        print(m,len(B),'aligned days with gap >= 0.10%'); print(S.state.value_counts(normalize=True).round(3).to_dict())
