"""SMT on NQ vs ES, 1-minute, ET. References: previous 30m block (clock :00/:30), previous 60m block (anchored 9:30),
opening range 9:30-10:00 (window 10:00-16:00). Windows are inside RTH 9:30-16:00. For each window and side, the first
minute each market trades beyond its own reference level; one-sided = SMT, the other later = synced, never = held."""
import pandas as pd, numpy as np
A=pd.read_pickle('/home/claude/t3/bars_NQ_all.pkl'); B=pd.read_pickle('/home/claude/t3/bars_ES_all.pkl')
A=A[A.ts>='2023-01-01']; B=B[B.ts>='2023-01-01']
m=A[['ts','High','Low','Open','Close']].merge(B[['ts','High','Low','Open','Close']],on='ts',suffixes=('A','B'))
m['date']=m.ts.dt.normalize(); m['mod']=m.ts.dt.hour*60+m.ts.dt.minute
m=m[(m['mod']>=480)&(m['mod']<960)]          # 8:00-16:00 ET
TICK=0.25
rows=[]
def windows(day):
    out=[]
    for s in range(570,960,30): out.append(('30m',s-30,s,s,s+30))            # ref block, window block
    for s in range(570,960,60): out.append(('60m',s-60,s,s,min(s+60,960)))
    out.append(('OR',570,600,600,960))
    return out
for d,x in m.groupby('date'):
    if x['mod'].min()>510 or x['mod'].max()<955: continue
    md=x['mod'].values
    for kind,r0,r1,w0,w1 in windows(d):
        rf=(md>=r0)&(md<r1); wn=(md>=w0)&(md<w1)
        if rf.sum()<int(0.8*(r1-r0)) or wn.sum()<3: continue
        for side in ('hi','lo'):
            res={}
            for k in 'AB':
                if side=='hi':
                    ref=x['High'+k].values[rf].max(); ex=x['High'+k].values[wn]; hit=np.where(ex>=ref+TICK)[0]
                else:
                    ref=x['Low'+k].values[rf].min(); ex=x['Low'+k].values[wn]; hit=np.where(ex<=ref-TICK)[0]
                res[k]=hit[0] if len(hit) else None
            a,b=res['A'],res['B']
            if a is None and b is None: st='none'
            elif a is not None and b is not None and a==b: st='both same minute'
            elif a is not None and b is not None: st='smt then synced'
            else: st='smt held'
            lead=None if st in('none','both same minute') else ('NQ' if (b is None or (a is not None and a<b)) else 'ES')
            delay=abs(a-b) if (a is not None and b is not None) else None
            rows.append((d,kind,side,st,lead,delay))
R=pd.DataFrame(rows,columns=['date','kind','side','status','leader','delay'])
nd=R.date.nunique(); print('RTH days',nd, R.date.min().date(), R.date.max().date())
for k,g in R.groupby('kind'):
    c=g.status.value_counts()
    smt=g[g.status.str.startswith('smt')]
    print(f"\n{k}: window-sides {len(g)} | per day: SMT {len(smt)/nd:.2f} (synced {(smt.status=='smt then synced').sum()/nd:.2f}, held {(smt.status=='smt held').sum()/nd:.2f}) | both same minute {c.get('both same minute',0)/nd:.2f} | neither {c.get('none',0)/nd:.2f}")
    s=smt[smt.status=='smt then synced'].delay
    print(f"   sync delay minutes: median {s.median():.0f}, P75 {s.quantile(.75):.0f}, P90 {s.quantile(.9):.0f}; synced within 2 min {((s<=2).sum())/max(1,len(smt))*100:.0f}% of SMTs; leader NQ {(smt.leader=='NQ').mean()*100:.0f}%")
R.to_pickle('smt_events.pkl')
