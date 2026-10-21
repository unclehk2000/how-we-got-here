import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl')
rows = []
for d, g in b.groupby('tday'):
    r = g[(g.hm >= 700) & (g.hm < 900)]
    w = g[(g.hm >= 900) & (g.hm < 1100)]       # levels watched from 09:00 until the 11:00 cut-off
    if len(r) < 100 or len(w) < 100:
        continue
    H, L = r.High.max(), r.Low.min()
    R = H - L
    if R <= 0:
        continue
    tH = r.ts[r.High.idxmax()]; tL = r.ts[r.Low.idxmin()]   # first occurrence, like the script
    up = tH >= tL
    org = L if up else H
    s = 1 if up else -1
    wH, wL = w.High.max(), w.Low.min()
    row = {'tday': d}
    for v in [1.5, 2.0, 2.5, -0.25, -0.5, -1.25, -1.5]:
        y = org + s * v * R
        above = (v > 1) == up if v > 1 else (not up)
        if v > 1:
            above = up
        else:
            above = not up
        row[v] = (wH >= y) if above else (wL <= y)
    # either 7-9 extreme taken by 11:00
    rows.append(row)
df = pd.DataFrame(rows)
df['yr'] = df.tday.dt.year
print('days', len(df), 'years', sorted(df.yr.unique()))
for lab, sub in [('all', df), ('2018-24', df[df.yr <= 2024]), ('2025-26', df[df.yr >= 2025])]:
    print(lab, len(sub), {k: round(100 * sub[k].mean(), 1) for k in [1.5, 2.0, 2.5, -0.25, -0.5, -1.25, -1.5]})
