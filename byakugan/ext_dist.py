import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl')
recs = []
closer = []
for d, g in b.groupby('tday'):
    r = g[(g.hm >= 700) & (g.hm < 900)]
    w = g[(g.hm >= 900) & (g.hm < 1100)]
    if len(r) < 100 or len(w) < 100: continue
    H, L = r.High.max(), r.Low.min(); R = H - L
    if R <= 0: continue
    up = r.ts[r.High.idxmax()] >= r.ts[r.Low.idxmin()]
    org = L if up else H; end = H if up else L; s = 1 if up else -1
    O = w.Open.iloc[0]
    closer.append(abs(O - end) < abs(O - org))
    wH, wL = w.High.max(), w.Low.min()
    for v in np.arange(-2.0, 3.01, 0.25):
        if 0 <= v <= 1: continue
        y = org + s * v * R
        side = 'cont' if v > 1 else 'term'
        above = up if v > 1 else (not up)
        hit = (wH >= y) if above else (wL <= y)
        recs.append((side, v, abs(y - O) / R, hit))
df = pd.DataFrame(recs, columns=['side', 'v', 'distR', 'hit'])
print('09:00 open closer to the later extreme:', round(100*np.mean(closer),1), '%')
df['bin'] = pd.cut(df.distR, [0, .25, .5, .75, 1, 1.5, 2, 3])
print(df.groupby(['bin', 'side'], observed=True).hit.agg(['mean', 'size']).unstack().round(3))
