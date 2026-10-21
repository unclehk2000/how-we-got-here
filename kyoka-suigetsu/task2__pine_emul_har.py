import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np, json
from pine_emul import isHol, dayStep, nextTD
import har2
from prod_har import design3, COLS
C=json.load(open('har_coef.json'))
for s in ['NQ','ES','RTY']:
    D=pd.read_pickle(f'F_{s}.pkl')
    cf=C[s]['coef']; CF=[cf[k] for k in ['const','d1','d5','d22','dn1','up1','inside','tue','wed','thu','fri','opex_day','tom','pre_hol','post_hol']]
    # --- Pine mirror: arrays of completed days only
    lrA=[]; out=[]
    rng=((D.h-D.l)/D.o*100).values; ah=D.ah.values; al=D.al.values; ac=D.ac.values
    td=0; prevm=None
    for t,(d,row) in enumerate(D.iterrows()):
        td = 1 if (prevm is None or d.month!=prevm) else td+1; prevm=d.month
        if t>0 and rng[t-1]>0: lrA.append(np.log(rng[t-1])); lrA=lrA[-250:]
        if len(lrA)<120 or t<2: out.append(np.nan); continue
        L=np.mean(lrA); d1=lrA[-1]-L; d5=np.mean(lrA[-5:])-L; d22=np.mean(lrA[-22:])-L
        r1=100*(ac[t-1]-ac[t-2])/ac[t-2]; ins=int(ah[t-1]<=ah[t-2] and al[t-1]>=al[t-2])
        dw=d.weekday()+2   # Pine dow: Mon=2 … Fri=6
        dd=d.date(); pre=isHol(dayStep(dd,1)); post=isHol(dayStep(dd,-1)); last=nextTD(dd).month!=dd.month; tom=last or td<=3
        opex=d.weekday()==4 and 15<=d.day<=21
        x=L+CF[0]+CF[1]*d1+CF[2]*d5+CF[3]*d22+CF[4]*max(-r1,0)+CF[5]*max(r1,0)+CF[6]*ins+CF[7]*(dw==3)+CF[8]*(dw==4)+CF[9]*(dw==5)+CF[10]*(dw==6)+CF[11]*opex+CF[12]*tom+CF[13]*pre+CF[14]*post
        out.append(x)
    pine=pd.Series(out,index=D.index)
    # --- research model prediction with the same coefficients
    X=design3(D); res=X['L']+cf['const']+sum(cf[k]*X[k] for k in COLS)
    ok=pine.notna()&res.notna()
    diff=(pine-res)[ok]
    print(f'{s}: Pine mirror vs research forecast (log): mean |diff| {diff.abs().mean():.4f}, max {diff.abs().max():.3f}, share within 0.01 {(diff.abs()<0.01).mean():.3f}')
    # accuracy of the Pine mirror vs Kyōka typical, 2021–2026 (in-sample coefs, sanity only)
    base=np.log(D.rng.rolling(30).median().shift(1)); te=ok&(D.year>=2021)&((D.rvol>0.4)|D.rvol.isna())
    q50=C[s]['q']['50']
    print(f'   MAE 2021–26: Pine mirror {(D.lr-pine-q50)[te].abs().mean():.4f} vs typical {(D.lr-base)[te].abs().mean():.4f}')
