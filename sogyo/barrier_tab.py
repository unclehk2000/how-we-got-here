import pandas as pd, numpy as np, sys
from scipy.stats import binomtest
from summary import wil
ORDER=['Expansion','Retracement','Reversal','Consolidation']
def cell(s):
    s=s.dropna(); n=len(s)
    if n<8: return dict(n=n)
    k=s.sum(); lo,hi=wil(k,n); p=binomtest(int(round(k)),n,0.5).pvalue
    return dict(n=n,rate=100*k/n,lo=lo,hi=hi,p=p)
def table(B,by):
    rows=[]
    for st in ORDER+['ALL']:
        sub=B if st=='ALL' else B[B[by]==st]
        if len(sub)==0: continue
        c=cell(sub['away_0.5']); r=dict(state=st,days=len(sub),touch=100*sub['touch_0.5'].mean(),**{'n':c.get('n'),'away%':c.get('rate'),'CI':f"{c.get('lo',np.nan):.0f}–{c.get('hi',np.nan):.0f}",'p':c.get('p')})
        r['resolved%']=100*sub['how_0.5'].isin(['away','through','both']).mean()/max(sub['touch_0.5'].mean(),1e-9)
        for f in (0.375,0.625): r[f'placebo{f}']=100*sub[f'away_{f}'].mean()
        r['tight±0.10']=100*sub['tight0.1'].mean()
        r['gap↑ away%']=100*sub[sub.gap>0]['away_0.5'].mean(); r['gap↓ away%']=100*sub[sub.gap<0]['away_0.5'].mean()
        rows.append(r)
    return pd.DataFrame(rows)
pd.set_option('display.width',250)
for m in sys.argv[1:] or ['NQ','ES']:
    B=pd.read_pickle(f'barrier_{m}.pkl')
    for by,lab in [('state','SAME-DAY state (known after the close)'),('prev_state','PRIOR-DAY state (known before the open)')]:
        print(f'\n{m} — {lab}'); print(table(B,by).round(3).to_string(index=False))
