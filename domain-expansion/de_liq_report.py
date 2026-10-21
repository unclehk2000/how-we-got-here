import pandas as pd, numpy as np, statsmodels.api as sm
LV = pd.read_pickle('/home/claude/byk/de_LV.pkl'); DY = pd.read_pickle('/home/claude/byk/de_DY.pkl')
print(f"unswept overnight pivot levels at 02:30: {len(LV)} ({100*LV['eq'].mean():.1f}% are equal highs/lows) over {LV.tday.nunique()} days")
print('\n1) Do equal highs/lows get hit (02:30-04:59) more than ordinary pivots at the same distance?')
for sp in ['train', 'test']:
    Z = LV[(LV.sp == sp) & (LV.distR > 0)].copy()
    Z['ld'] = np.log(Z.distR); Z['eqf'] = Z['eq'].astype(float)
    m = sm.Logit(Z.hit.astype(float), sm.add_constant(Z[['ld', 'eqf', 'up']])).fit(disp=0, cov_type='cluster', cov_kwds={'groups': Z.tday.astype('int64')})
    print(f"  {sp}: EQ coefficient {m.params['eqf']:+.3f} (t {m.tvalues['eqf']:.2f}) | odds ratio {np.exp(m.params['eqf']):.2f} | n {len(Z)}")
    bins = [0, 0.5, 1, 2, 4, 100]
    g = Z.groupby([pd.cut(Z.distR, bins), 'eq'], observed=True).hit.agg(['mean', 'size']).unstack()
    print('   hit rate by distance (domain ranges) [ordinary | equal]:',
          {str(k): f"{100*g.loc[k, ('mean', False)]:.0f}% | {100*g.loc[k, ('mean', True)]:.0f}% (n{int(g.loc[k, ('size', True)])})" for k in g.index if ('mean', True) in g.columns and not np.isnan(g.loc[k, ('mean', True)])})
print('\n2) One-sided equal liquidity: EQH within 3 ranges above and no EQL within 3 below (or the reverse)')
for sp in ['train', 'test']:
    Z = DY[DY.sp == sp]
    upS = (Z.eqh_up <= 3) & ~(Z.eql_dn <= 3); dnS = (Z.eql_dn <= 3) & ~(Z.eqh_up <= 3)
    S = pd.concat([Z[upS].assign(side=1), Z[dnS].assign(side=-1)])
    toward_brk = (S.brk == S.side).mean(); geo = np.where(S.side > 0, S.octv, 1 - S.octv).mean()
    toward_ext = (S.ext_dir == S.side).mean(); toward_ret = (np.sign(S.ret) == S.side).mean()
    print(f"  {sp}: n{len(S)} | first break toward the EQ side {100*toward_brk:.1f}% (geometry alone {100*geo:.1f}%) | London extreme on that side {100*toward_ext:.1f}% | 04:59 close that way {100*toward_ret:.1f}%")
    E = S[S.sd2]
    print(f"        on 2 SD expansion days (n{len(E)}): extreme on the EQ side {100*(E.ext_dir == E.side).mean():.1f}%")
print('\n3) Peak-volume level (close of the biggest-volume bar since 18:00), price at 02:29 above vs below')
print('   where the peak-volume bar sits (hour, ET):', (DY.pv_hm // 100).value_counts(normalize=True).sort_index().mul(100).round(0).to_dict())
for sp in ['train', 'test']:
    Z = DY[DY.sp == sp]
    for nm, m in [('above', Z.above_pvl), ('below', ~Z.above_pvl)]:
        S = Z[m]
        print(f"  {sp} price {nm} the level (n{len(S)}): 04:59 close up {100*(S.ret > 0).mean():.1f}% | first break up {100*(S.brk > 0).mean():.1f}% | London extreme up {100*(S.ext_dir > 0).mean():.1f}% | expansion-day extreme up {100*(S[S.sd2].ext_dir > 0).mean():.1f}%")
    print(f"  {sp} all days: 04:59 close up {100*(Z.ret > 0).mean():.1f}% | first break up {100*(Z.brk > 0).mean():.1f}%")
    # control for geometry: first-break-up vs octant, logistic with above_pvl
    W = Z[Z.brk != 0].copy(); W['oct'] = W.octv; W['ab'] = W.above_pvl.astype(float)
    m = sm.Logit((W.brk > 0).astype(float), sm.add_constant(W[['oct', 'ab']])).fit(disp=0)
    print(f"        first break up ~ octant + above level: above coefficient {m.params['ab']:+.3f} (t {m.tvalues['ab']:.2f})")
    W = Z.copy(); W['oct'] = W.octv; W['ab'] = W.above_pvl.astype(float)
    m = sm.Logit((W.ret > 0).astype(float), sm.add_constant(W[['oct', 'ab']])).fit(disp=0)
    print(f"        04:59 close up ~ octant + above level: above coefficient {m.params['ab']:+.3f} (t {m.tvalues['ab']:.2f})")
