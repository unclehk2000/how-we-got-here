"""Render one RTH day of NQ (chart) vs ES with Genjutsu Kai v2's drawing rules: trendline, ghost, lag bracket, tag
with collision offsets, OR lines and the compact card. Engine = the validated port (grace 2), plus extreme times."""
import pandas as pd, numpy as np, math, sys
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
DAY=sys.argv[1] if len(sys.argv)>1 else None
A=pd.read_pickle('/home/claude/t3/bars_NQ_all.pkl'); B=pd.read_pickle('/home/claude/t3/bars_ES_all.pkl')
A=A[(A.ts>='2025-01-01')&(A.ts<'2026-01-01')]; B=B[(B.ts>='2025-01-01')&(B.ts<'2026-01-01')]
m=A[['ts','Open','High','Low','Close']].merge(B[['ts','High','Low','Close','Open']],on='ts',how='left',suffixes=('A','B'))
m['mod']=m.ts.dt.hour*60+m.ts.dt.minute; m['dk']=m.ts.dt.year*10000+m.ts.dt.month*100+m.ts.dt.day
GR=2
ML=float(sys.argv[2]) if len(sys.argv)>2 else 0.0
def blockOf(k,mm): return mm//30 if k=='30m' else (mm-30)//60 if k=='60m' else (-1 if mm<570 else 0 if mm<600 else 1 if mm<960 else 2)
def blockStart(k,b): return b*30 if k=='30m' else b*60+30 if k=='60m' else (570 if b==0 else 600 if b==1 else 960)
def isWindow(k,b): return b==1 if k=='OR' else 570<=blockStart(k,b)<960
class Side:
    def __init__(s): s.st=0; s.lead=0; s.tLead=None; s.mA=None; s.tmA=None; s.mB=None; s.tmB=None; s.lagP=None; s.tSync=None
class Track:
    def __init__(t,k,tag,cH,cL,w): t.k=k; t.tag=tag; t.cH=cH; t.cL=cL; t.w=w; t.blk=-999; t.day=0; t.cN=0; t.live=False; t.hi=Side(); t.lo=Side(); t.ev=[]
def run(day_df):
    T=[Track('30m','30','#f23645','#089981',2),Track('OR','OR','#ab47bc','#42a5f5',2)]
    for r in day_df.itertuples(index=False):
        ti=r.ts
        for t in T:
            b=blockOf(t.k,r.mod)
            if b!=t.blk or r.dk!=t.day:
                if t.live:
                    for s,ih in ((t.hi,True),(t.lo,False)):
                        if s.st in (1,2):
                            if s.st==1 and (s.lagP or 0)<ML: s.st=6; continue
                            if s.st==1: t.ev.append((s,ih,t.ref.copy(),t.wb))
                            s.st=4
                    t.live=False
                if isWindow(t.k,b) and r.dk==t.day and b==t.blk+1 and t.cN>0 and not np.isnan(t.c['Hb']):
                    t.ref=t.c.copy(); t.live=True; t.wb=b; t.hi=Side(); t.lo=Side()
                t.blk=b; t.day=r.dk; t.c={'Ha':r.HighA,'HaT':ti,'La':r.LowA,'LaT':ti,'Hb':r.HighB,'HbT':ti,'Lb':r.LowB,'LbT':ti}; t.cN=1
            else:
                c=t.c
                if r.HighA>c['Ha']: c['Ha'],c['HaT']=r.HighA,ti
                if r.LowA<c['La']: c['La'],c['LaT']=r.LowA,ti
                if not np.isnan(r.HighB) and (np.isnan(c['Hb']) or r.HighB>c['Hb']): c['Hb'],c['HbT']=r.HighB,ti
                if not np.isnan(r.LowB) and (np.isnan(c['Lb']) or r.LowB<c['Lb']): c['Lb'],c['LbT']=r.LowB,ti
                t.cN+=1
            if t.live and r.mod<960:
                for s,ih in ((t.hi,True),(t.lo,False)):
                    refA=t.ref['Ha'] if ih else t.ref['La']; refB=t.ref['Hb'] if ih else t.ref['Lb']
                    if s.st<=2:
                        vA=r.HighA if ih else r.LowA; vB=r.HighB if ih else r.LowB
                        if s.mA is None or (vA>s.mA if ih else vA<s.mA): s.mA,s.tmA=vA,ti
                        if not np.isnan(vB) and (s.mB is None or (vB>s.mB if ih else vB<s.mB)): s.mB,s.tmB=vB,ti
                    tA=s.mA is not None and (s.mA>refA if ih else s.mA<refA)
                    tB=s.mB is not None and (s.mB>refB if ih else s.mB<refB)
                    if s.st==0:
                        if tA and tB: s.st=5
                        elif tA or tB: s.st=1; s.lead=1 if tA else 2; s.tLead=ti
                    if s.st in (1,2) and s.mB is not None: s.lagP=100*abs(s.mB/refB-s.mA/refA)
                    sis=tB if s.lead==1 else tA
                    if s.st==1:
                        if sis: s.st=5
                        elif (ti+pd.Timedelta(minutes=1)-s.tLead)>pd.Timedelta(minutes=GR) and (s.lagP or 0)>=ML: s.st=2; t.ev.append((s,ih,t.ref.copy(),t.wb))
                    elif s.st==2 and sis: s.st=3; s.tSync=ti
    return T
days=m[(m['mod']>=570)&(m['mod']<960)].dk.unique()
if DAY is None:
    best=None
    for d in days[::3]:
        x=m[m.dk==d]; x=x[(x['mod']>=480)&(x['mod']<1000)]
        T=run(x); n=sum(len(t.ev) for t in T); nor=len(T[1].ev)
        if nor>=1 and n>=9: best=d; break
    DAY=best
x=m[m.dk==int(DAY)]; x=x[(x['mod']>=480)&(x['mod']<1000)].reset_index(drop=True)
T=run(x)
# ── render
bg='#131722'; fg='#d1d4dc'
fig,ax=plt.subplots(figsize=(19.2,10.0),dpi=100); fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
xr=x[(x['mod']>=540)&(x['mod']<990)]
tnum=lambda ts: (ts - xr.ts.iloc[0]).total_seconds()/60
for r in xr.itertuples():
    xi=tnum(r.ts); up=r.CloseA>=r.OpenA; col='#089981' if up else '#f23645'
    ax.plot([xi,xi],[r.LowA,r.HighA],color=col,lw=0.6); ax.add_patch(Rectangle((xi-0.35,min(r.OpenA,r.CloseA)),0.7,max(abs(r.CloseA-r.OpenA),0.25),color=col,lw=0))
sep=1.6*(xr.HighA-xr.LowA).rolling(50,min_periods=5).mean().iloc[-1]
o=T[1]
if hasattr(o,'ref'):
    for y in (o.ref['Ha'],o.ref['La']): ax.plot([tnum(xr.ts.iloc[0]+pd.Timedelta(minutes=30)),tnum(xr.ts.iloc[0]+pd.Timedelta(minutes=420))],[y,y],color='#ffb300',alpha=0.55,lw=1,ls=':')
tags=[]
gl={3:'◐',4:'■',2:'●'}
for t in T:
    for s,ih,ref,wb in t.ev:
        c=t.cH if ih else t.cL; alpha=0.35 if s.st==3 else 1.0
        refA=ref['Ha'] if ih else ref['La']; refB=ref['Hb'] if ih else ref['Lb']; tRA=ref['HaT'] if ih else ref['LaT']; tRB=ref['HbT'] if ih else ref['LbT']
        gEnd=refA*s.mB/refB
        ax.plot([tnum(tRA),tnum(s.tmA)],[refA,s.mA],color=c,lw=t.w,alpha=alpha)
        ax.plot([tnum(tRB),tnum(s.tmB)],[refA,gEnd],color=c,lw=1,ls=':',alpha=alpha*0.8)
        xb=max(tnum(s.tmA),tnum(s.tmB)); ax.plot([xb,xb],[s.mA,gEnd],color=c,lw=1,ls=':',alpha=alpha)
        ym=(s.mA+gEnd)/2; off=0
        for _ in range(7):
            if not any(abs(px-xb)<25 and abs(py-(ym+off))<sep for px,py in tags): break
            off+= sep if ih else -sep
        tags.append((xb,ym+off))
        sisA=s.lead==2; sisN='NQ' if sisA else 'ES'; pL=s.lagP/100*(refA if sisA else refB)
        txt=f"{'▼' if ih else '▲'}{t.tag} {gl.get(s.st,'●')}  {sisN} Δ{pL:,.2f} · {s.lagP:.2f}%"
        ax.text(xb+1.2,ym+off,txt,color=c,alpha=max(alpha,0.6),fontsize=8.5,va='center',family='DejaVu Sans Mono',bbox=dict(fc=bg,ec='none',alpha=0.85,pad=1.5))
        ax.plot([tnum(tRA),tnum(s.tmA)],[refA,s.mA],'o',color=c,ms=4,alpha=alpha)
ticks=[t for t in range(0,450,30)]
ax.set_xticks(ticks); ax.set_xticklabels([f"{(540+t)//60:02d}:{(540+t)%60:02d}" for t in ticks],color=fg,fontsize=9)
ax.tick_params(colors=fg,labelsize=9); [s_.set_color('#2a2e39') for s_ in ax.spines.values()]
ax.grid(color='#1e222d',lw=0.6); ax.yaxis.tick_right()
ax.axvspan(tnum(xr.ts.iloc[0]+pd.Timedelta(minutes=30)),tnum(xr.ts.iloc[0]+pd.Timedelta(minutes=420)),color='#2962ff',alpha=0.04)
# compact card
rows=[("◆ GENJUTSU KAI   NQ × ES   "+str(DAY)[4:6]+"/"+str(DAY)[6:],"",""),("9:30→",f"NQ {100*(xr.CloseA.iloc[-1]/x[x['mod']>=570].OpenA.iloc[0]-1):+.2f}%  ES {100*(xr.CloseB.iloc[-1]/x[x['mod']>=570].OpenB.iloc[0]-1):+.2f}%",""),("","HIGH ▼","LOW ▲")]
def cell(t,s):
    if s.st in (0,1,6): return "○"
    if s.st==5: return "= both"
    sis='ES' if s.lead==1 else 'NQ'
    return {2:'● ',3:'◐ ',4:'■ '}[s.st]+(sis+f" {s.lagP:.2f}%" if s.st!=3 else s.tSync.strftime('%H:%M'))
for t,nm in ((T[0],'30m'),(T[1],'OR')): rows.append((nm,cell(t,t.hi),cell(t,t.lo)))
n=sum(len(t.ev) for t in T); ns=sum(1 for t in T for e in t.ev if e[0].st==3); nh=sum(1 for t in T for e in t.ev if e[0].st==4)
rows.append(("today",f"{n} · {ns} synced · {nh} held",""))
y0=0.975
for i,(a,b_,c_) in enumerate(rows):
    yy=y0-i*0.028
    fig.text(0.70,yy,a,color='#e6e9ef' if i==0 else '#9aa3b5',fontsize=9.5,family='DejaVu Sans Mono',va='top',bbox=dict(fc='#171c28' if i in (0,2) else '#0e1117',ec='#262c3a',pad=2) if True else None)
    fig.text(0.765,yy,b_,color='#e6e9ef',fontsize=9.5,family='DejaVu Sans Mono',va='top')
    fig.text(0.86,yy,c_,color='#e6e9ef',fontsize=9.5,family='DejaVu Sans Mono',va='top')
ax.set_title(f"Genjutsu Kai v2 mock · NQ 1m vs ES · {DAY} · 30m + OR · grace 2m · min lag {ML:.2f}%",color=fg,fontsize=11,loc='left')
plt.tight_layout(); plt.savefig(f'mock_v2_{DAY}_ml{int(ML*100):02d}.png',facecolor=bg)
print(DAY, [(t.k,len(t.ev),[(e[0].st,round(e[0].lagP,3)) for e in t.ev]) for t in T])
