"""Line-by-line Python port of Genjutsu Kai's engine (Track/Side state machine, grace 2 min), run on 1-minute bars."""
import pandas as pd, numpy as np, math
A=pd.read_pickle('/home/claude/t3/bars_NQ_all.pkl'); B=pd.read_pickle('/home/claude/t3/bars_ES_all.pkl')
A=A[(A.ts>='2025-01-01')&(A.ts<'2026-01-01')]; B=B[(B.ts>='2025-01-01')&(B.ts<'2026-01-01')]
m=A[['ts','High','Low']].merge(B[['ts','High','Low']],on='ts',how='left',suffixes=('A','B'))
m['mod']=m.ts.dt.hour*60+m.ts.dt.minute; m['dk']=m.ts.dt.year*10000+m.ts.dt.month*100+m.ts.dt.day
m=m[(m['mod']>=480)&(m['mod']<1020)].reset_index(drop=True)
GR=2
def blockOf(k,mm): return mm//30 if k=='30m' else (mm-30)//60 if k=='60m' else (-1 if mm<570 else 0 if mm<600 else 1 if mm<960 else 2)
def blockStart(k,b): return b*30 if k=='30m' else b*60+30 if k=='60m' else (570 if b==0 else 600 if b==1 else 960)
def isWindow(k,b): return b==1 if k=='OR' else 570<=blockStart(k,b)<960
mx=lambda a,b: b if a is None or (isinstance(a,float) and math.isnan(a)) else a if b is None or math.isnan(b) else max(a,b)
mn=lambda a,b: b if a is None or (isinstance(a,float) and math.isnan(a)) else a if b is None or math.isnan(b) else min(a,b)
class Side:
    def __init__(s): s.st=0; s.lead=0; s.tLead=None; s.mA=None; s.mB=None
class Track:
    def __init__(t,k): t.k=k; t.blk=-999; t.day=0; t.cN=0; t.live=False; t.hi=Side(); t.lo=Side(); t.log=[]
def check(t,s,isHi,ti,hA,lA,hB,lB,day):
    refA=t.rHa if isHi else t.rLa; refB=t.rHb if isHi else t.rLb
    s.mA=mx(s.mA,hA) if isHi else mn(s.mA,lA)
    s.mB=mx(s.mB,hB) if isHi else mn(s.mB,lB)
    tA=s.mA is not None and (s.mA>refA if isHi else s.mA<refA)
    tB=s.mB is not None and not (isinstance(s.mB,float) and math.isnan(s.mB)) and (s.mB>refB if isHi else s.mB<refB)
    if s.st==0:
        if tA and tB: s.st=5
        elif tA or tB: s.st=1; s.lead=1 if tA else 2; s.tLead=ti
    sis=tB if s.lead==1 else tA
    if s.st==1:
        if sis: s.st=5
        elif (ti+1)-s.tLead>GR: s.st=2; t.log.append([day,t.k,'smt'])
    elif s.st==2:
        if sis: s.st=3; t.log[-1 if False else -1]  # counted below
        if sis: t.log.append([day,t.k,'sync'])
def finish(t,s,day):
    if s.st in (1,2):
        if s.st==1: t.log.append([day,t.k,'smt'])
        s.st=4; t.log.append([day,t.k,'held'])
def step(t,mm,dk,ti,hA,lA,hB,lB):
    b=blockOf(t.k,mm)
    if b!=t.blk or dk!=t.day:
        if t.live: finish(t,t.hi,t.day); finish(t,t.lo,t.day); t.live=False
        contig= dk==t.day and b==t.blk+1 and t.cN>0 and not math.isnan(t.cHb) and not math.isnan(t.cLb)
        if isWindow(t.k,b) and contig:
            t.rHa,t.rLa,t.rHb,t.rLb=t.cHa,t.cLa,t.cHb,t.cLb; t.live=True; t.hi=Side(); t.lo=Side()
        t.blk=b; t.day=dk; t.cHa,t.cLa,t.cHb,t.cLb=hA,lA,hB,lB; t.cN=1
    else:
        t.cHa=mx(t.cHa,hA); t.cLa=mn(t.cLa,lA); t.cHb=mx(t.cHb,hB); t.cLb=mn(t.cLb,lB); t.cN+=1
    if t.live and mm<960:
        check(t,t.hi,True,ti,hA,lA,hB,lB,dk); check(t,t.lo,False,ti,hA,lA,hB,lB,dk)
T=[Track('OR'),Track('60m'),Track('30m')]
ti=(m.ts.astype('int64')//60_000_000_000).values if m.ts.dtype.str.endswith('[ns]') else (m.ts.values.astype('datetime64[m]').astype(np.int64))
for r,t_ in zip(m.itertuples(index=False),ti):
    for t in T: step(t,r.mod,r.dk,int(t_),r.HighA,r.LowA,float(r.HighB),float(r.LowB))
L=pd.DataFrame([x for t in T for x in t.log],columns=['dk','kind','ev'])
days=L.dk.nunique()
print('Pine port, 2025:',days,'days with events')
print((L.groupby(['kind','ev']).size().unstack()/days).round(2))
# vectorised reference on the same days
R=pd.read_pickle('smt_events.pkl'); R=R[(R.date>='2025-01-01')&(R.date<'2026-01-01')]
smt=R[R.status.str.startswith('smt')]; keep=smt[(smt.status=='smt held')|(smt.delay>GR)]
nd=R.date.nunique()
print('\nIndependent version, 2025:',nd,'days')
print(pd.DataFrame({'smt':keep.groupby('kind').size()/nd,'sync':keep[keep.status=='smt then synced'].groupby('kind').size()/nd,'held':keep[keep.status=='smt held'].groupby('kind').size()/nd}).round(2))
# same days only, totals
dd=set((R.date.dt.year*10000+R.date.dt.month*100+R.date.dt.day).unique())
Ls=L[L.dk.isin(dd)]
a=Ls.groupby(['kind','ev']).size().unstack()
b=pd.DataFrame({'smt':keep.groupby('kind').size(),'sync':keep[keep.status=='smt then synced'].groupby('kind').size(),'held':keep[keep.status=='smt held'].groupby('kind').size()})
print('\nTotals on the same',len(dd),'days — Pine port vs independent:'); print(pd.concat({'port':a[['smt','sync','held']],'indep':b},axis=1))
