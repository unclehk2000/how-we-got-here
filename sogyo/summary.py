import pandas as pd, numpy as np, sys
from scipy.stats import binomtest
def wil(k,n,z=1.96):
    if n==0: return (np.nan,np.nan)
    p=k/n; den=1+z*z/n; c=(p+z*z/(2*n))/den; h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den; return (100*(c-h),100*(c+h))
def rate(s):
    s=s.dropna(); k=s.sum(); n=len(s); lo,hi=wil(k,n); return f'{100*k/n:5.1f}% (n {n}, CI {lo:.1f}–{hi:.1f})' if n else 'n 0'
def summarize(m):
    S=pd.read_pickle(f'stats_{m}.pkl')
    S['split']=np.sign(S.gap1)!=np.sign(S.gap2)
    print(f'\n===== {m}: {len(S)} days {S.index.min().date()} – {S.index.max().date()} =====')
    print('|RTH gap| median %.3f%%, |RTH2 gap| median %.3f%%, |settlement move| median %.3f%% (p90 %.3f%%), |CE2−CE1| median %.3f%%'%(
        S.gap1.abs().median(),S.gap2.abs().median(),S.settle.abs().median(),S.settle.abs().quantile(.9),S.settle.abs().median()/2))
    print('split days (open between the two closes, CEs on opposite sides of the open): %.1f%%'%(100*S.split.mean()))
    T=lambda c: (S[c+'_t']>=0)&(S[c+'_t']<10000)
    print('\nTouch during RTH (09:30–16:14):')
    for c,lab in [('CE1','CE1 (RTH 0.5)'),('CE2','CE2 (RTH2 0.5)'),('M1','mirror of CE1 (placebo)'),('M2','mirror of CE2 (placebo)'),('C1','full RTH gap fill'),('C2','full RTH2 gap fill')]:
        v=S[c+'_t'].notna()
        print(f'  {lab:26s} {rate(T(c)[v])}   median minute {S.loc[T(c),c+"_t"].median():.0f}')
    al=~S.split
    near=np.where(S.gap2.abs()<S.gap1.abs(),'CE2','CE1'); far=np.where(near=='CE2','CE1','CE2')
    S['near']=near; S['far']=far
    tn=pd.Series([T(n)[d] for d,n in zip(S.index,S.near)],index=S.index)
    tf=pd.Series([T(f)[d] for d,f in zip(S.index,S.far)],index=S.index)
    A=S[al]
    print('\nAligned days (%d): near CE touched %s ; far CE touched | near touched %s'%(al.sum(),rate(tn[al]),rate(tf[al&tn])))
    print('  near CE is CE2 (settlement window moved toward today\'s open) on %.1f%% of aligned days'%(100*(A.near=='CE2').mean()))
    for k in [0.05,0.10,0.20]:
        rows=[]
        for c in ['CE1','CE2','M1','M2']:
            rows.append(f'{c} {100*S[f"{c}_hold{k}"].mean():.1f}% (n {S[f"{c}_hold{k}"].notna().sum()})')
        print(f'  hold race ±{k}%: '+' | '.join(rows))
    # hold at near vs far on aligned days
    for k in [0.10]:
        hn=pd.Series([S.loc[d,f'{n}_hold{k}'] for d,n in zip(S.index,S.near)],index=S.index)
        hf=pd.Series([S.loc[d,f'{f}_hold{k}'] for d,f in zip(S.index,S.far)],index=S.index)
        print(f'  aligned, ±{k}%: hold at NEAR CE {100*hn[al].mean():.1f}% (n {hn[al].notna().sum()}), at FAR CE {100*hf[al].mean():.1f}% (n {hf[al].notna().sum()})')
    sp=S[S.split]
    print('\nSplit days (%d): CE1 touched %s, CE2 touched %s, both %s'%(len(sp),rate(T('CE1')[S.split]),rate(T('CE2')[S.split]),rate((T('CE1')&T('CE2'))[S.split])))
    return S
if __name__=='__main__':
    for m in sys.argv[1:] or ['NQ','ES']:
        summarize(m)
