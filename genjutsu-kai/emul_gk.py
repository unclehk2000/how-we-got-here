"""Genjutsu Kai default settings on NQ (chart) vs ES (pair), 1-minute, 2018–2026.
Reference = 09:00–09:30 high/low; SMTs form 09:30–09:59; outcome tracked to 10:59; 1 tick = 0.25.
Control = the side where both markets took the level on the same first bar (no SMT)."""
import pandas as pd, numpy as np
T=0.25
A=pd.read_pickle('/home/claude/t3/bars_NQ_all.pkl'); B=pd.read_pickle('/home/claude/t3/bars_ES_all.pkl')
m=A[['ts','tday','High','Low','Close']].merge(B[['ts','High','Low','Close']],on='ts',suffixes=('A','B'))
m['tod']=m.ts.dt.hour*60+m.ts.dt.minute
m=m[(m.tod>=540)&(m.tod<960)]
rows=[]
for td,d in m.groupby('tday'):
    pre=d[(d.tod>=540)&(d.tod<570)]; w=d[(d.tod>=570)&(d.tod<960)]
    if len(pre)<25 or len(w)<300: continue
    ref={'A':(pre.HighA.max(),pre.LowA.min()),'B':(pre.HighB.max(),pre.LowB.min())}
    hA,lA,cA,hB,lB,cB,tod=[w[c].values for c in ['HighA','LowA','CloseA','HighB','LowB','CloseB','tod']]
    for hi in (True,False):
        rA=ref['A'][0] if hi else ref['A'][1]; rB=ref['B'][0] if hi else ref['B'][1]
        pA=ref['A'][1] if hi else ref['A'][0]; pB=ref['B'][1] if hi else ref['B'][0]
        ceA=(ref['A'][0]+ref['A'][1])/2; ceB=(ref['B'][0]+ref['B'][1])/2
        brA=(hA>rA+T) if hi else (lA<rA-T); brB=(hB>rB+T) if hi else (lB<rB-T)
        win=tod<600
        idx=np.where((brA|brB)&win)[0]
        if len(idx)==0:
            rows.append(dict(day=td,hi=hi,kind='none')); continue
        i=idx[0]
        if brA[i] and brB[i]:
            kind='both'; sw='both'
        else:
            kind='smt'; sw='A' if brA[i] else 'B'
        r=dict(day=td,hi=hi,kind=kind,swept=sw,t=tod[i])
        # outcome to 10:59: synced (held takes its level) vs Kai (swept closes back through its level)
        if kind=='smt':
            st=0; j=i
            for j in range(i,len(tod)):
                if tod[j]>=660: st=3; break
                held_took = (brB[j] if sw=='A' else brA[j])
                back = ((cA[j]<rA) if hi else (cA[j]>rA)) if sw=='A' else ((cB[j]<rB) if hi else (cB[j]>rB))
                if held_took: st=2; break
                if back: st=1; break
            r.update(status=st,tRes=tod[j])
            if st==1:
                # theoretical execution at the Kai close, both markets; stop = sweep extreme (swept) / untaken level (held)
                for X,h,l,c,ref_,ce,opp in (('A',hA,lA,cA,rA,ceA,pA),('B',hB,lB,cB,rB,ceB,pB)):
                    ent=c[j]
                    stop=(h[i:j+1].max() if hi else l[i:j+1].min()) if sw==X else ref_
                    risk=(stop-ent) if hi else (ent-stop)
                    res={}
                    for nm,tg in (('ce',ce),('opp',opp)):
                        rew=(ent-tg) if hi else (tg-ent)
                        out='na'
                        if risk>0 and rew>0:
                            out='open'
                            for k in range(j+1,len(tod)):
                                hitS=(h[k]>=stop) if hi else (l[k]<=stop)
                                hitT=(l[k]<=tg) if hi else (h[k]>=tg)
                                if hitS: out='stop'; break
                                if hitT: out='target'; break
                        res[nm]=(out,rew/risk if risk>0 and rew>0 else np.nan)
                    r[f'{X}_risk']=risk; r[f'{X}_ce']=res['ce'][0]; r[f'{X}_ceR']=res['ce'][1]; r[f'{X}_opp']=res['opp'][0]; r[f'{X}_oppR']=res['opp'][1]
        # retrace-through for the chart market (A) by 10:59, for SMT-where-A-swept vs control (both took it): Model 3's claim
        if kind=='both' or (kind=='smt' and sw=='A'):
            back=np.where(((cA<rA) if hi else (cA>rA)) & (np.arange(len(tod))>=i) & (tod<660))[0]
            r['A_back']=len(back)>0
        rows.append(r)
R=pd.DataFrame(rows); R.to_pickle('gk_events.pkl')
R['yr']=pd.DatetimeIndex(R.day).year
n_days=R.day.nunique()
print(f'paired days {n_days} (2018–2026)\n')
for hi,lab in ((True,'high side (bearish SMT)'),(False,'low side (bullish SMT)')):
    x=R[R.hi==hi]
    print(f'{lab}: no break {(x.kind=="none").mean()*100:.0f}% · both took it together {(x.kind=="both").mean()*100:.0f}% · SMT {(x.kind=="smt").mean()*100:.0f}% of days')
S=R[R.kind=='smt']
print(f'\nSMTs: {len(S)} ({len(S)/n_days:.2f} per day) · NQ took {(S.swept=="A").mean()*100:.0f}% / ES took {(S.swept=="B").mean()*100:.0f}% · median time {int(S.t.median()//60):02d}:{int(S.t.median()%60):02d}')
st=S.status.value_counts(normalize=True).reindex([1,2,3]).fillna(0)
print(f'outcome by 11:00: Kai {st[1]*100:.0f}% · Synced {st[2]*100:.0f}% · no outcome {st[3]*100:.0f}%')
for p,(a,b) in {'2018–24':(2018,2024),'2025–26':(2025,2026)}.items():
    s=S[(S.yr>=a)&(S.yr<=b)].status.value_counts(normalize=True).reindex([1,2,3]).fillna(0)
    print(f'   {p}: Kai {s[1]*100:.0f}% · Synced {s[2]*100:.0f}% · none {s[3]*100:.0f}%  (n={((S.yr>=a)&(S.yr<=b)).sum()})')
# Model 3 claim vs control: NQ closes back through the level it took, by 11:00
a=R[(R.kind=='smt')&(R.swept=='A')]; c=R[R.kind=='both']
print(f'\nNQ closes back through the level it took, by 11:00 · NQ took it and ES did not (SMT): {a.A_back.mean()*100:.0f}% (n={len(a)}) · both took it together (control): {c.A_back.mean()*100:.0f}% (n={len(c)})')
K=S[S.status==1]
print(f'\nTheoretical execution at Kai (n={len(K)}), outcome by 16:00, target before invalidation:')
for X,nm in (('A','NQ'),('B','ES')):
    for tg in ('ce','opp'):
        o=K[f'{X}_{tg}']; v=o.isin(['target','stop'])
        wr=(o=='target')[v].mean(); rm=K.loc[v,f'{X}_{tg}R'].median()
        exp=((o=='target')*K[f'{X}_{tg}R']-(o=='stop')*1)[v].mean()
        print(f'   {nm} → {"C.E." if tg=="ce" else "opposite"}: valid {v.mean()*100:.0f}% of Kais · hit {wr*100:.0f}% · median R {rm:.2f} · average result {exp:+.2f}R per trade')
    print(f'   {nm} median risk {K[f"{X}_risk"].median():.2f} pts')
