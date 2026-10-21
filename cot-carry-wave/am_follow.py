"""Asset-manager follow-up: does the released COT predict the trading week(s) that follow?"""
import pandas as pd, numpy as np, sys
from scipy.stats import binomtest
def fwd(y,k): return sum(y.shift(-j) for j in range(k))       # return over this week + next k-1
RULES={
 'AM Δ1w (follow)':      lambda F: np.sign(F.am_d1),
 'AM Δ4w (follow)':      lambda F: np.sign(F.am_d4),
 'LEV Δ1w (fade)':       lambda F: -np.sign(F.lev_d1),
 'AM idx52 ≥80 long / ≤20 short': lambda F: np.where(F.am_i52>=80,1,np.where(F.am_i52<=20,-1,0)),
 'LEV idx52 ≤20 long / ≥80 short':lambda F: np.where(F.lev_i52<=20,1,np.where(F.lev_i52>=80,-1,0)),
 'AM & LEV Δ1w opposite (follow AM)': lambda F: np.where(np.sign(F.am_d1)==-np.sign(F.lev_d1),np.sign(F.am_d1),0),
 'RTY AM Δ1w (follow)':  lambda F: np.sign(F.rty_am_d1) if 'rty_am_d1' in F else np.nan*F.y,
 'AM Δ1w, only above 10w SMA': lambda F: np.where(F.above_sma10==1,np.sign(F.am_d1),0),
 'AM Δ1w, long side only': lambda F: np.where(F.am_d1>0,1,0),
}
def table(F,k=1):
    y=fwd(F.y,k); rows=[]
    for name,f in RULES.items():
        s=pd.Series(np.asarray(f(F),float),index=F.index)
        m=y.notna()&s.notna()&(s!=0)
        if m.sum()<10: continue
        hit=(np.sign(y[m])==s[m]).mean(); n=int(m.sum())
        up=(y[m]>0).mean()
        p=binomtest(int(round(hit*n)),n,0.5).pvalue
        pl=(s[m]*y[m]).sum(); bh=y[m].sum() if k==1 else np.nan
        rows.append([name,n,100*hit,100*up,p,100*pl,100*y[m].sum()])
    return pd.DataFrame(rows,columns=['rule','n','hit%','long hit%','p(hit≠50)','rule P&L %','always-long P&L %'])
if __name__=='__main__':
    pd.set_option('display.width',200)
    for m in sys.argv[1:] or ['NQ','ES']:
        F=pd.read_pickle(f'F_{m}.pkl')
        for k in (1,4):
            print(f'\n{m}  horizon {k}w'); print(table(F,k).round(2).to_string(index=False))
