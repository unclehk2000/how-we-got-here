import pandas as pd, numpy as np
D = pd.read_pickle('/home/claude/byk/de_D.pkl')
def tstat(v):
    v = np.asarray(v, float); v = v[~np.isnan(v)]
    return v.mean() / (v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 2 else np.nan
def line(name, Z, pcol, bcol, risk=None):
    Z = Z[Z[pcol].notna()]
    r = Z[pcol] / (Z['R'] if risk is None else Z[risk])
    long_ = Z[Z.iloc[:, 0].index.isin(Z.index)]
    print(f"  {name:34s} n{len(Z):4d} | win {100*(Z[pcol]>0).mean():5.1f}% | avg {Z[pcol].mean():7.2f} pt (t {tstat(Z[pcol]):5.2f}) | {r.mean():+.3f}R (t {tstat(r):5.2f})"
          f" | always-long same entry: {Z[bcol].mean():7.2f} pt | strategy - long: {(Z[pcol]-Z[bcol]).mean():+7.2f} pt (t {tstat(Z[pcol]-Z[bcol]):5.2f})")
for sp in ['train', 'test']:
    Z = D[D.sp == sp]
    print(f"\n================ {sp}  ({len(Z)} days)")
    # octant check vs gambler's ruin
    F = Z[Z['first'] != 0].copy()
    F['bin'] = pd.cut(F.octv, [0, .125, .25, .375, .5, .625, .75, .875, 1.0], include_lowest=True)
    g = F.groupby('bin', observed=True).agg(n=('first', 'size'), up_first=('first', lambda s: 100*(s > 0).mean()), oct_mean=('octv', lambda s: 100*s.mean()))
    print('  Octant -> first boundary broken (up%), vs driftless-walk expectation (= mean octant %)')
    print(g.round(1).to_string())
    A = Z[Z.A_side.notna()]
    print(f"  Break inside 02:30-02:49: {100*len(A)/len(Z):.1f}% of days (ambiguous same-bar both sides: {int(Z.get('A_amb', pd.Series(dtype=bool)).fillna(False).sum())})")
    print(f"  A stop-entry: stop hit {100*(A.A_how=='stop').mean():.1f}% | race +1R before -1R: {100*A.A_race.mean():.1f}% (n{A.A_race.notna().sum()}) | median MFE beyond boundary {A.A_mfe.median():.2f}R")
    for nm, S in [('ALL', A), ('long', A[A.A_side > 0]), ('short', A[A.A_side < 0]), ('octant-confirmed', A[A.A_okOct]), ('octant-conf long', A[A.A_okOct & (A.A_side > 0)]), ('octant-conf short', A[A.A_okOct & (A.A_side < 0)])]:
        line('A hold-to-05:00 ' + nm, S, 'A_pnl', 'A_bench')
    for nm, S in [('ALL', A), ('octant-confirmed', A[A.A_okOct])]:
        line('A target 1.84R ' + nm, S, 'A_pnlT', 'A_bench')
        line('A target Asia-cond ' + nm, S, 'A_pnlAsia', 'A_bench')
    B = Z[Z.B_side.notna()]
    print(f"  B close-confirm: race +1R first {100*B.B_race.mean():.1f}%")
    for nm, S in [('ALL', B), ('long', B[B.B_side > 0]), ('short', B[B.B_side < 0]), ('octant-confirmed', B[B.B_okOct])]:
        line('B close-confirm ' + nm, S, 'B_pnl', 'B_bench', risk='B_risk')
    C = Z[Z.C_side.notna()]
    print(f"  C retest filled on {100*len(C)/max(len(B),1):.1f}% of close-confirm days")
    for nm, S in [('ALL', C), ('long', C[C.C_side > 0]), ('short', C[C.C_side < 0]), ('octant-confirmed', C[C.C_okOct])]:
        line('C retest ' + nm, S, 'C_pnl', 'C_bench')
    print(f"  Always-long 02:30 open -> 04:59 close, every day: {Z.long_bench_0230.mean():.2f} pt (t {tstat(Z.long_bench_0230):.2f}), up {100*(Z.long_bench_0230>0).mean():.1f}%")
