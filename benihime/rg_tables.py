import json, numpy as np, pandas as pd
R = pd.read_pickle('/home/claude/rg/rg_rows2.pkl')
edges = [0.5, 1.0, 1.5, 2.5]
bi = lambda r: int(np.searchsorted(edges, r, side='right'))
R['b'] = R.ratio.map(bi)
CK = [0, 15, 30, 45, 60, 90, 120, 180, 240, 300, 360]
out = {}
for key, col, fin in (('FL', 'fill_min', 'fill_rth'), ('CE', 'ce_min', 'ce_rth')):
    tab = []
    for m in CK:
        row = []
        for b in range(5):
            d = R[(R.b == b) & ~(R[col] < m)]
            row.append(round(100 * (d[col] >= m).mean() if len(d) else 0))   # P(hit by close | not hit before m)
        tab.append(row)
    out[key] = tab
    print(key); print(pd.DataFrame(tab, index=CK, columns=['<0.5', '0.5-1', '1-1.5', '1.5-2.5', '2.5+']).to_string())
# n per cell at the last checkpoint
print(R.groupby('b').size().to_dict())
# after the close, not filled in RTH -> filled within the staircase life (5 sessions); same for CE
for key, a, w in (('F5', 'fill_rth', 'fill_w5'), ('C5', 'ce_rth', 'ce_w5')):
    out[key] = [round(100 * R[(R.b == b) & (R[a] == False)][w].dropna().astype(float).mean()) for b in range(5)]
    print(key, out[key])
# SD reach in RTH and within 5 sessions by bucket (cont = beyond the open, over = beyond the prior close)
for key in ('c1_rth', 'c2_rth', 'o1_rth', 'o2_rth', 'c1_w5', 'c2_w5', 'o1_w5', 'o2_w5'):
    out[key] = [round(100 * R[R.b == b][key].dropna().astype(float).mean()) for b in range(5)]
    print(key, out[key])
# regime size: median ratio and fill
for rg in ('CPI', 'NFP', 'normal'):
    d = R[R.regime == rg]
    print(rg, 'n', len(d), 'median ratio', round(d.ratio.median(), 2), 'fill', round(100 * d.fill_rth.mean()), 'ce', round(100 * d.ce_rth.mean()), 'share big (>=1.5)', round(100 * (d.ratio >= 1.5).mean()))
print('bucket share', (R.b.value_counts(normalize=True).sort_index() * 100).round(0).to_dict())
json.dump(out, open('/home/claude/rg/rg_tables.json', 'w'))
