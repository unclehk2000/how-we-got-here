"""The doc's own secondary filters, tested as written (no new tuning): narrow LOR (< its 20-day trailing average) and Asia-sweep status."""
import pandas as pd, numpy as np
D = pd.read_pickle('/home/claude/byk/de_D.pkl').sort_values('tday').reset_index(drop=True)
D['Ravg'] = D.R.shift(1).rolling(20).mean()
D['narrow'] = D.R < D.Ravg
def t(v): v = np.asarray(v, float); v = v[~np.isnan(v)]; return v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))
A = D[D.A_side.notna() & D.Ravg.notna()].copy()
A['r'] = A.A_pnl / A.R; A['ex'] = A.A_pnl - A.A_bench
for sp in ['train', 'test']:
    Z = A[A.sp == sp]
    for nm, S in [('narrow LOR', Z[Z.narrow]), ('wide LOR', Z[~Z.narrow]),
                  ('narrow + octant', Z[Z.narrow & Z.A_okOct])]:
        print(f"{sp:5s} {nm:16s} n{len(S):4d} stop hit {100*(S.A_how=='stop').mean():5.1f}% | {S.r.mean():+.3f}R (t {t(S.r):5.2f}) | vs always-long {S.ex.mean():+6.2f} pt (t {t(S.ex):5.2f})")
