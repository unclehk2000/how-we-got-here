import json, numpy as np, pandas as pd
R = pd.read_pickle('sb_rows.pkl')
E = [0.05, 0.1, 0.2, 0.35]
R['b'] = R.dA.map(lambda x: int(np.searchsorted(E, x, side='right')))
print('bucket share', (R.b.value_counts(normalize=True).sort_index() * 100).round(0).to_dict())
for nm, end in (('Shikai 16:59', 450), ('Bankai 11:00', 90)):
    R['mid'] = R.tMid < end; R['mir'] = R.tMir < end
    print('\n', nm, 'all: mid', round(100 * R.mid.mean(), 1), 'mirror', round(100 * R.mir.mean(), 1))
    t = R.groupby('b')[['mid', 'mir']].mean().mul(100).round(0)
    t['n'] = R.groupby('b').size(); print(t.T.to_string())
    print(R.groupby(['half', 'b'])[['mid', 'mir']].mean().mul(100).round(0).unstack().to_string())
    print(R.groupby(['sym', 'b'])['mid'].mean().mul(100).round(0).unstack().to_string())
    # long side (mid above open) vs short side
    print('up (LONG into mid):', R[R.up].groupby('b').mid.mean().mul(100).round(0).to_dict(), ' down:', R[~R.up].groupby('b').mid.mean().mul(100).round(0).to_dict())
# live tables
out = {}
for key, end, CK in (('SH', 450, [0, 15, 30, 45, 60, 90, 120, 180, 240, 300, 360, 420]), ('BK', 90, [0, 5, 10, 15, 20, 30, 45, 60, 75])):
    for lv, col in (('M', 'tMid'), ('R', 'tMir')):
        tab = []
        for m in CK:
            row = []
            for b in range(5):
                d = R[(R.b == b) & ~(R[col] < m)]
                row.append(int(round(100 * (d[col] < end).mean())))
            tab.append(row)
        out[key + lv] = tab
        print(key + lv); print(pd.DataFrame(tab, index=CK).to_string())
# London high / low taken after 05:00
L = R.dropna(subset=['lH'])
for nm, end in (('by 11:00', 660), ('by 16:59', 1020)):
    h = L.tLH < end; l = L.tLL < end
    print('London', nm, 'high', round(100 * h.mean()), 'low', round(100 * l.mean()), 'either', round(100 * (h | l).mean()), 'both', round(100 * (h & l).mean()),
          {k: (round(100 * (g.tLH < end).mean()), round(100 * (g.tLL < end).mean())) for k, g in L.groupby('half')},
          {k: (round(100 * (g.tLH < end).mean()), round(100 * (g.tLL < end).mean())) for k, g in L.groupby('sym')})
    out['LON_' + nm[-5:].replace(':', '')] = [int(round(100 * h.mean())), int(round(100 * l.mean())), int(round(100 * (h & l).mean()))]
# session range medians in ADR
for c in ('rA', 'rL', 'rN'):
    print(c, 'median', round(R[c].median(), 3), {k: round(g[c].median(), 3) for k, g in R.groupby('sym')}, {k: round(g[c].median(), 3) for k, g in R.groupby('half')})
    out['med_' + c] = round(R[c].median(), 3)
json.dump(out, open('sb_tables.json', 'w'))
