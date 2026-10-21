"""Event clock: running range and net move from the 18:00 open, ÷ (open × ADR20), at the end of each 30-minute slot of the
CME trading day (18:00 → 17:00 ET, 46 slots), by day type. Quantiles q10/q25/q50/q75/q90, plus the median share of the
day's final range already made by each slot. Output clock.json; prints stability 2018–24 vs 2025–26 at key slots."""
import pandas as pd, numpy as np, json
TYPES = ['FOMC', 'NFP', 'CPI', 'POST', 'PRE', 'HOLLOW', 'NORMAL']
NS = 46
QS = [0.10, 0.25, 0.50, 0.75, 0.90]
OUT = {}
for root in ('NQ', 'ES'):
    b = pd.read_pickle(f'/home/claude/t3/bars_{root}_all.pkl')
    b['mod'] = b.ts.dt.hour * 60 + b.ts.dt.minute
    D = pd.read_pickle(f'days_{root}.pkl'); TD = D[D.anchor == 'TD'].set_index('tday')
    rows = []
    for td, x in b.groupby('tday'):
        if td not in TD.index: continue
        md = x['mod'].values
        if not (md >= 1080).any() or len(x) < 1000: continue
        el = (md - 1080) % 1440                                  # minutes since 18:00
        slot = el // 30
        O = x.Open.values[0]; d = TD.loc[td]; s = O * d.adr
        hi = np.maximum.accumulate(x.High.values); lo = np.minimum.accumulate(x.Low.values); cl = x.Close.values
        R = np.full(NS, np.nan); N = np.full(NS, np.nan)
        for j in range(NS):
            idx = np.where(slot <= j)[0]
            if len(idx): k = idx[-1]; R[j] = (hi[k] - lo[k]) / s; N[j] = (cl[k] - O) / s
        rows.append(dict(tday=td, type=d.type, year=d.year, R=R, N=N, fin=R[-1]))
    P = pd.DataFrame(rows)
    res = {}
    for t in TYPES:
        x = P[P.type == t]
        Rm = np.vstack(x.R.values); Nm = np.vstack(x.N.values); sh = Rm / x.fin.values[:, None]
        res[t] = dict(n=int(len(x)),
                      R=[[round(float(v), 3) for v in np.nanquantile(Rm, q, axis=0)] for q in QS],
                      N=[[round(float(v), 3) for v in np.nanquantile(Nm, q, axis=0)] for q in QS],
                      share=[round(float(v), 3) for v in np.nanmedian(sh, axis=0)])
        tr = x[x.year <= 2024]; te = x[x.year >= 2025]
        res[t]['R50_train'] = [round(float(v), 3) for v in np.nanmedian(np.vstack(tr.R.values), axis=0)]
        res[t]['R50_test'] = [round(float(v), 3) for v in np.nanmedian(np.vstack(te.R.values), axis=0)] if len(te) else None
    OUT[root] = res
    # slots: 08:30 release → slot ending 09:00 is j = (15*60 - 0)/30 - 1 ... 18:00 + 30(j+1)
    lab = lambda j: f'{(18 * 60 + 30 * (j + 1)) // 60 % 24:02d}:{(30 * (j + 1)) % 60:02d}'
    print('=' * 90, '\n', root)
    for j in (28, 29, 30, 31, 33, 39, 40, 41, 45):
        line = f'{lab(j)} ' + ' · '.join(f"{t} {res[t]['R'][2][j]:.2f} ({res[t]['R50_train'][j]:.2f}/{res[t]['R50_test'][j] if res[t]['R50_test'] else 0:.2f}) sh{res[t]['share'][j]*100:.0f}%" for t in TYPES)
        print(line)
json.dump(OUT, open('clock.json', 'w'))
