"""Replays Benihime's 15-minute gap engine on NQ data (ETH bars, and RTH-only bars) and compares with the research rows."""
import numpy as np, pandas as pd
b = pd.read_pickle('/home/claude/kyw/bars_NQ_all.pkl')
b = b[(b.ts >= '2026-08-01')].set_index('ts')
R = pd.read_pickle('rg_rows2.pkl'); R = R[(R.sym == 'NQ') & (R.tday >= '2026-08-10')].set_index('tday')

def run(x):
    gK, gO, gC, gT, gCE, gFL = [], [], [], [], [], []
    c16 = None
    prev = None
    for t, r in x.iterrows():
        if prev is not None:
            tp, rp = prev
            mp = tp.hour * 60 + tp.minute
            if mp <= 974 < mp + 15:
                c16 = rp.Close
            for j in range(len(gK)):
                if gFL[j] == 0 and tp >= gT[j]:
                    o, c = gO[j], gC[j]; up = o > c
                    if gCE[j] == 0 and (rp.Low <= (o + c) / 2 if up else rp.High >= (o + c) / 2):
                        gCE[j] = tp
                    if (rp.Low <= c if up else rp.High >= c):
                        gFL[j] = tp
        if t.hour * 60 + t.minute == 570 and c16 is not None:
            gK.append(r.tday); gT.append(t); gO.append(r.Open); gC.append(c16)
            gCE.append(t if r.Open == c16 else 0); gFL.append(t if r.Open == c16 else 0); c16 = None
        prev = (t, r)
    return pd.DataFrame(dict(day=gK, O=gO, C=gC, ce=gCE, fl=gFL)).set_index('day')

agg = dict(Open='first', High='max', Low='min', Close='last', tday='first')
eth = b.resample('15min').agg(agg).dropna()
rth = b[(b.hm >= 930) & (b.hm < 1615)].resample('15min').agg(agg).dropna()
E, Rr = run(eth), run(rth)
cmp = R[['O', 'C', 'fill_min', 'ce_min']].join(E[['O', 'C', 'ce', 'fl']], rsuffix='_eth').join(Rr[['O', 'C', 'fl']], rsuffix='_rth')
cmp['okO'] = (cmp.O == cmp.O_eth) & (cmp.O == cmp.O_rth); cmp['okC'] = (cmp.C == cmp.C_eth) & (cmp.C == cmp.C_rth)
print(cmp[['O', 'C', 'O_eth', 'C_eth', 'okO', 'okC', 'fill_min', 'fl', 'fl_rth']].tail(15).to_string())
print('all equal O/C:', cmp.okO.all(), cmp.okC.all(), 'n', len(cmp))
