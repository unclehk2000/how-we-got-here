"""Shikai / Bankai re-test (NQ 1-min, 2018 + 2022-Aug 2026). Train 2018-24, test 2025-26.
Overnight range = 18:00 -> 09:29 ET; midpoint target; 'meaningful' = |open - mid| >= 0.15% of open.
Placebo = mirror level: same distance from the 09:30 open on the opposite side (pure volatility baseline)."""
import pandas as pd, numpy as np, sys
sys.path.insert(0,'/home/claude/twin')
b=pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
S=pd.read_pickle('/home/claude/twin/states_NQ.pkl')
G={d:x for d,x in b.groupby('tday')}
def seg(x,a,z): return x[(x.hm>=a)&(x.hm<=z)]
def first_touch(x,lvl,above):  # above: level is above price -> touch when High>=lvl
    m=(x.High.values>=lvl) if above else (x.Low.values<=lvl)
    return int(np.argmax(m)) if m.any() else None
rows=[]
for d,x in G.items():
    on=x[(x.hm>=1800)|(x.hm<=929)]; rth=seg(x,930,1614)
    if len(on)<500 or len(rth)<300 or rth.hm.iloc[0]!=930: continue
    H,L=on.High.max(),on.Low.min(); mid=(H+L)/2; O=rth.Open.iloc[0]
    dist=abs(O-mid); up=mid>O
    rec=dict(day=d,year=d.year,dist_pct=100*dist/O,mean=dist/O>=0.0015,
             net_ratio=abs(on.Close.iloc[-1]-on.Open.iloc[0])/(H-L))
    # midpoint (and mirror) touch times within RTH; i = minutes after 09:30
    i=first_touch(rth,mid,up); j=first_touch(rth,O-(mid-O),not up)
    rec['t_mid']=i; rec['t_mir']=j
    # open-print itself counted? record whether the 09:30 bar touched
    # ladder: eighths of overnight range counted from the extreme on the open's side
    ext=H if not up else L   # near extreme (open side) ... if mid above open, open is nearer the low
    far=L if not up else H
    for k in range(1,8):
        lvl=ext+(far-ext)*k/8
        if (up and lvl<=O) or ((not up) and lvl>=O): rec[f'lad{k}']=np.nan; continue
        t=first_touch(rth,lvl,up); rec[f'lad{k}']=float(t is not None)
    # post-touch: after first mid touch, does price go +0.25*dist through first or back 0.25*dist?
    if i is not None:
        h,l=rth.High.values[i+1:],rth.Low.values[i+1:]; k=0.5*dist
        thr= mid+k if up else mid-k; back= mid-k if up else mid+k
        a=np.argmax(h>=thr) if up and (h>=thr).any() else (np.argmax(l<=thr) if (not up) and (l<=thr).any() else 10**6)
        c=np.argmax(l<=back) if up and (l<=back).any() else (np.argmax(h>=back) if (not up) and (h>=back).any() else 10**6)
        rec['through']=np.nan if a==c==10**6 else float(a<c)
    rows.append(rec)
D=pd.DataFrame(rows).set_index('day')
D=D.join(S[['state','prev_state','rng','avg20']])
D['prev_big']=(D.rng/D.avg20).shift()>1.15
D['split']=np.where(D.year>=2025,'test','train')
M=D[D['mean']]
def r(s): return f"{100*s.mean():.1f}% (n {s.notna().sum()})"
print('days',len(D),'meaningful',len(M))
for nm,lim in [('RTH (to 16:14)',10**6),('by 11:00',90),('by 10:00',30)]:
    for sp in ['train','test']:
        Z=M[M.split==sp]
        print(f"{nm:14s} {sp:5s} mid {r(Z.t_mid.notna()&(Z.t_mid<lim))}  mirror {r(Z.t_mir.notna()&(Z.t_mir<lim))}")
T=M[M.t_mid.notna()&(M.t_mid<90)]
print('\nBankai timing (touches by 11:00), share by minutes after 09:30:')
print(pd.cut(T.t_mid,[-1,0,10,11,20,30,60,90],right=False).value_counts(normalize=True).sort_index().round(3).to_dict())
print('touch on the 09:30 bar itself:',round((T.t_mid==0).mean(),3),' 09:31-09:41 (idx 1-11):',round(T.t_mid.between(1,11).mean(),3),
      ' median min',T.t_mid.median())
TM=M[M.t_mir.notna()&(M.t_mir<90)]
print('mirror timing median',TM.t_mir.median(),' share 0-10',round((TM.t_mir<=10).mean(),3))
print('\nby prev_state, mid touched by 11:00 (train | test) vs mirror:')
for s_ in ['Consolidation','Retracement','Reversal','Expansion']:
    out=[]
    for sp in ['train','test']:
        Z=M[(M.prev_state==s_)&(M.split==sp)]
        out.append(f"{sp} mid {r(Z.t_mid.notna()&(Z.t_mid<90))} mir {100*(Z.t_mir.notna()&(Z.t_mir<90)).mean():.1f}%")
    print(f"{s_:14s}",' | '.join(out))
print('\nStage 3 (prev RTH >115% avg & overnight |net|/range<0.35), mid by 11:00:')
for sp in ['train','test']:
    Z=M[M.split==sp]; c=Z.prev_big&(Z.net_ratio<0.35)
    print(sp,'setup',r(Z[c].t_mid.notna()&(Z[c].t_mid<90)),'mirror',f"{100*(Z[c].t_mir.notna()&(Z[c].t_mir<90)).mean():.1f}%",' rest',r(Z[~c].t_mid.notna()&(Z[~c].t_mid<90)))
print('\nladder (RTH):',{k:f"{100*M[f'lad{k}'].mean():.1f}% n{M[f'lad{k}'].notna().sum()}" for k in range(1,8)})
print('post-touch through first (+/-0.5x dist):',r(M.through.dropna()))
D.to_pickle('/home/claude/sb/D.pkl')
