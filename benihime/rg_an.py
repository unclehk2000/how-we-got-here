import numpy as np, pandas as pd
R = pd.read_pickle('/home/claude/rg/rg_rows.pkl')
R = R[R.ratio.notna()].copy()
R['news'] = R.regime != 'normal'
R['bk'] = pd.cut(R.ratio, [0, 0.5, 1.0, 1.5, 2.5, 99], labels=['<0.5', '0.5-1', '1-1.5', '1.5-2.5', '2.5+'], right=False)
pc = lambda s: (s.astype(float).mean() * 100).round(1)
cols = ['ce_rth', 'fill_rth', 'c1_rth', 'c2_rth', 'o1_rth', 'o2_rth', 'ce_w5', 'fill_w5', 'c1_w5', 'c2_w5', 'o1_w5', 'o2_w5', 'ce_w20', 'fill_w20']
print('n', len(R)); print(R[cols].astype(float).mean().mul(100).round(1).to_string())
print('\nby half'); print(R.groupby('half')[cols].mean().mul(100).round(1).T)
print('\nby sym'); print(R.groupby('sym')[cols].mean().mul(100).round(1).T)
print('\nby size bucket'); print(R.groupby('bk', observed=True)[cols].mean().mul(100).round(1).T)
print(R.bk.value_counts(normalize=True).sort_index().round(3))
print('\nby regime'); print(R.groupby('regime')[cols + ['ratio', 'pct']].mean().round(3).T)
print('\nmedian ratio by regime', R.groupby('regime').ratio.median().round(2).to_dict(), 'median pct', R.groupby(['sym', 'regime']).pct.median().round(3).unstack().to_dict())
print('\nnews vs normal within size bucket (fill_rth, ce_rth, c1_rth, o1_rth)')
print(R.groupby(['bk', 'news'], observed=True)[['fill_rth', 'ce_rth', 'c1_rth', 'o1_rth', 'fill_w5']].agg(['mean', 'size']).round(3))
# CE / fill by time of day (minutes after 09:30)
for m in (30, 90, 150, 404):
    print('by', m, 'min: ce', pc(R.ce_min < m), 'fill', pc(R.fill_min < m))
# older gaps: not filled within the staircase life -> fill / CE during sessions 6-20
O = R[R.fill_w5 == False]
print('\nnot filled in 5 sessions n', len(O), 'fill 5→20', pc(O.fill_5to20.dropna()), 'ce 5→20', pc(O.ce_5to20.dropna()))
O2 = R[R.ce_w5 == False]
print('CE not hit in 5 sessions n', len(O2), 'ce 5→20', pc(O2.ce_5to20.dropna()))
R.to_pickle('/home/claude/rg/rg_rows2.pkl')
