"""Export full-sample (2018–2026) event-day shape stats as Pine string rows: per root (NQ, ES) × anchor (TD, MID, RTH) × type."""
import pandas as pd, numpy as np, json
from shapes import TYPES, BUCKETS
rows = {}; meta = {}
for root in ('NQ', 'ES'):
    D = pd.read_pickle(f'days_{root}.pkl'); D = D[np.isfinite(D.R)]
    meta[root] = (str(D.tday.min().date()), str(D.tday.max().date()))
    for an in ('TD', 'MID', 'RTH'):
        A = D[D.anchor == an]; out = []
        for t in TYPES:
            x = A[A.type == t]
            q = lambda s: list(np.quantile(s, [0.25, 0.5, 0.75]))
            def share(col):
                r = [((x[col] >= a) & (x[col] < z)).mean() for a, z in BUCKETS[an]]
                return r + [0.0] * (6 - len(r))
            vals = [len(x), x.up.mean()] + q(x.u) + q(x.v) + [x.c.median()] + q(x.R) + share('tH') + share('tL')
            out.append(','.join(str(int(v)) if i == 0 else f'{v:.3f}' for i, v in enumerate(vals)))
        rows[f'{root}_{an}'] = ';'.join(out)
for k, v in rows.items(): print(k, len(v))
json.dump(dict(rows=rows, meta=meta), open('stats_rows.json', 'w'), indent=1)
print(meta)
# quick readable table: TD and RTH medians
for root in ('NQ', 'ES'):
    for an in ('TD', 'RTH'):
        print(root, an)
        for t, r in zip(TYPES, rows[f'{root}_{an}'].split(';')):
            f = r.split(','); print(f'   {t:7s} n {f[0]:>4s} up {float(f[1])*100:3.0f}% u50 {f[3]} v50 {f[6]} R25/50/75 {f[9]} {f[10]} {f[11]}')
