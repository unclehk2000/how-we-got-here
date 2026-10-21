import pandas as pd, numpy as np, sys
from scipy import stats
from shapes import TYPES, BUCKETS, BNAMES
out=[]
def P(*a):
    s=' '.join(str(x) for x in a); print(s, flush=True); out.append(s)
for root in ('NQ','ES'):
    D=pd.read_pickle(f'days_{root}.pkl'); D=D[np.isfinite(D.R)]
    tr=D.year<=2024; te=D.year>=2025
    P('='*110); P(f'{root}: days by anchor', D.groupby('anchor').size().to_dict(), '| train 2018–24, test 2025–26')
    for an in ('TD','MID','RTH'):
        A=D[D.anchor==an]; Atr=A[A.year<=2024]; Ate=A[A.year>=2025]
        P(f'\n{root} · {an}: median range ÷ ADR20 (train → test) · up-close % (train → test) · MW p vs normal (train)')
        base_tr=Atr[Atr.type=='NORMAL'].R
        for t in TYPES:
            a=Atr[Atr.type==t]; b=Ate[Ate.type==t]
            p=stats.mannwhitneyu(a.R,base_tr).pvalue if t!='NORMAL' and len(a)>5 else np.nan
            P(f'   {t:7s} n {len(a):4d}/{len(b):3d} · R {a.R.median():.2f} → {b.R.median() if len(b) else np.nan:.2f} · up {a.up.mean()*100:4.0f}% → {b.up.mean()*100 if len(b) else np.nan:4.0f}% · p {p:.4f}')
        # projection skill: type-specific vs pooled medians (fit train, score test)
        P(f'   projection of the high/low reach on 2025–26 (MAE in ADR units; type-specific vs one-size-fits-all):')
        pool={k:Atr[k].median() for k in ('u','v','R')}
        tot=[]
        for t in TYPES:
            a=Atr[Atr.type==t]; b=Ate[Ate.type==t]
            if len(b)<5: continue
            r=[]
            for k in ('u','v','R'):
                e1=(b[k]-a[k].median()).abs().mean(); e0=(b[k]-pool[k]).abs().mean(); r.append((e1,e0))
                lo,hi=a[k].quantile(.25),a[k].quantile(.75); cov=((b[k]>=lo)&(b[k]<=hi)).mean()
                r[-1]=(e1,e0,cov)
            tot.append((t,len(b),r))
            P(f'      {t:7s} n {len(b):3d} · u {r[0][0]:.3f} vs {r[0][1]:.3f} · v {r[1][0]:.3f} vs {r[1][1]:.3f} · R {r[2][0]:.3f} vs {r[2][1]:.3f} · P25–75 cover u {r[0][2]*100:.0f}% v {r[1][2]*100:.0f}% R {r[2][2]*100:.0f}%')
        # timing: chi-square of high/low bucket vs normal in train, and the biggest-lift bucket checked in test
        for col,lab in (('tH','high'),('tL','low')):
            bk=BUCKETS[an]
            def cat(s): 
                c=np.full(len(s),-1)
                for i,(a0,z0) in enumerate(bk): c[((s>=a0)&(s<z0)).values]=i
                return c
            for t in ('FOMC','NFP','CPI','POST','PRE','HOLLOW'):
                a=cat(Atr[Atr.type==t][col]); n0=cat(Atr[Atr.type=='NORMAL'][col]); b=cat(Ate[Ate.type==t][col]); n1=cat(Ate[Ate.type=='NORMAL'][col])
                ct=np.array([[ (a==i).sum() for i in range(len(bk))],[ (n0==i).sum() for i in range(len(bk))]])
                ct=ct[:,ct.sum(0)>0]
                p=stats.chi2_contingency(ct)[1]
                sh=np.array([(a==i).mean() for i in range(len(bk))]); sn=np.array([(n0==i).mean() for i in range(len(bk))])
                i=int(np.argmax(sh-sn)); shb=(b==i).mean() if len(b) else np.nan; snb=(n1==i).mean()
                if p<0.05: P(f'      time of {lab} {t:6s}: χ² p {p:.4f} · most over-represented {BNAMES[an][i]}: train {sh[i]*100:.0f}% vs normal {sn[i]*100:.0f}% · test {shb*100:.0f}% vs {snb*100:.0f}% (n {len(b)})')
open('validate_out.txt','w').write('\n'.join(out))
