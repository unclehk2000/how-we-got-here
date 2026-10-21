"""Domain Expansion day = the 04:59 ET close sits more than 0.3% beyond the 02:00-02:29 high (up) or low (down).
Known only at 05:00, so: (1) base rate, (2) the break trade on those days vs the rest, (3) can it be picked out by 02:30?
Features use only information available by 02:30. Train 2018-24, test 2025-26."""
import pandas as pd, numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
D0 = pd.read_pickle('/home/claude/byk/de_D.pkl').set_index('tday')
rows = []
for d, x in b.groupby('tday'):
    lor = x[(x.hm >= 200) & (x.hm <= 229)]; c5 = x[x.hm == 459]
    asia = x[(x.hm >= 2000) | (x.hm <= 0)]; on = x[(x.hm >= 1800) | (x.hm <= 159)]
    if len(lor) < 28 or len(c5) != 1 or len(asia) < 100: continue
    H, L = lor.High.max(), lor.Low.min(); P = lor.Close.iloc[-1]; C5 = c5.Close.iloc[0]
    up = C5 >= H * 1.003; dn = C5 <= L * 0.997
    rows.append(dict(tday=d, year=d.year, H=H, L=L, P=P, exp=up or dn, expDir=1 if up else (-1 if dn else 0),
                     lor_pct=100 * (H - L) / P, asia_pct=100 * (asia.High.max() - asia.Low.min()) / P,
                     on_pct=100 * (on.High.max() - on.Low.min()) / P, octv=(P - L) / (H - L) if H > L else 0.5,
                     asia_sw=(H > asia.High.max()) or (L < asia.Low.min()), dow=d.dayofweek,
                     day_rng=100 * (x.High.max() - x.Low.min()) / P, day_ret=100 * (x.Close.iloc[-1] / x.Open.iloc[0] - 1)))
F = pd.DataFrame(rows).sort_values('tday').reset_index(drop=True)
F['pd_rng'] = F.day_rng.shift(1); F['pd_ret'] = F.day_ret.shift(1); F['vol5'] = F.day_rng.shift(1).rolling(5).mean()
F['lor_rel'] = F.lor_pct / F.lor_pct.shift(1).rolling(20).mean()
F['asia_rel'] = F.asia_pct / F.asia_pct.shift(1).rolling(20).mean()
F = F.dropna(subset=['vol5', 'lor_rel', 'asia_rel', 'pd_ret']).reset_index(drop=True)
F['sp'] = np.where(F.year >= 2025, 'test', 'train')
F = F.join(D0[['A_side', 'A_pnl', 'A_bench', 'R', 'A_okOct']], on='tday')
def t(v): v = pd.Series(v).dropna(); return v.mean() / (v.std(ddof=1) / np.sqrt(len(v)))
print('== 1. How often')
for sp in ['train', 'test']:
    Z = F[F.sp == sp]
    print(f"  {sp}: {len(Z)} days | expansion day {100*Z.exp.mean():.1f}% (up {100*(Z.expDir>0).mean():.1f}%, down {100*(Z.expDir<0).mean():.1f}%)")
print('  by year:', (F.groupby('year').exp.mean() * 100).round(1).to_dict())
print('\n== 2. The break trade (first touch 02:30-02:49, stop opposite side, exit 04:59)')
for sp in ['train', 'test']:
    Z = F[(F.sp == sp) & F.A_side.notna()]; E = Z[Z.exp]; N_ = Z[~Z.exp]
    match = (E.A_side == E.expDir).mean()
    print(f"  {sp}: on expansion days the first break was the right side {100*match:.1f}% (n{len(E)}) | "
          f"R on expansion days {(E.A_pnl/E.R).mean():+.2f} | on other days {(N_.A_pnl/N_.R).mean():+.2f} (n{len(N_)})")
print('\n== 3. Can it be seen by 02:30? Expansion rate by tercile (cuts set on train)')
feats = ['lor_pct', 'lor_rel', 'asia_pct', 'asia_rel', 'on_pct', 'vol5', 'pd_rng', 'pd_ret', 'octv']
Tr = F[F.sp == 'train']; Te = F[F.sp == 'test']
for f in feats:
    q = Tr[f].quantile([1/3, 2/3]).values
    def rates(Z): k = np.digitize(Z[f], q); return [100 * Z.exp[k == i].mean() for i in range(3)]
    a, c = rates(Tr), rates(Te)
    print(f"  {f:9s} low/mid/high  train {a[0]:5.1f} {a[1]:5.1f} {a[2]:5.1f} | test {c[0]:5.1f} {c[1]:5.1f} {c[2]:5.1f}")
for f, lab in [('asia_sw', 'Asia extreme swept inside 02:00-02:30')]:
    print(f"  {lab}: train yes {100*Tr.exp[Tr[f]].mean():.1f} / no {100*Tr.exp[~Tr[f]].mean():.1f} | test yes {100*Te.exp[Te[f]].mean():.1f} / no {100*Te.exp[~Te[f]].mean():.1f}")
X = feats + ['asia_sw']
sc = StandardScaler().fit(Tr[X].astype(float)); m = LogisticRegression(max_iter=1000).fit(sc.transform(Tr[X].astype(float)), Tr.exp)
pTr = m.predict_proba(sc.transform(Tr[X].astype(float)))[:, 1]; pTe = m.predict_proba(sc.transform(Te[X].astype(float)))[:, 1]
print(f"\n  Logistic model (all features, fit on train): AUC train {roc_auc_score(Tr.exp, pTr):.3f} | test {roc_auc_score(Te.exp, pTe):.3f}")
print('  coefficients:', dict(zip(X, np.round(m.coef_[0], 2))))
cut = np.quantile(pTr, 2/3)
F.loc[Tr.index, 'p'] = pTr; F.loc[Te.index, 'p'] = pTe
print(f"\n== 4. Trade only the days the model flags (top third of predicted odds, cut set on train)")
for sp in ['train', 'test']:
    Z = F[(F.sp == sp)]; top = Z[Z.p >= cut]; rest = Z[Z.p < cut]
    T = top[top.A_side.notna()]; Rr = rest[rest.A_side.notna()]
    print(f"  {sp}: flagged days are expansion days {100*top.exp.mean():.1f}% vs {100*rest.exp.mean():.1f}% for the rest | "
          f"break trade on flagged days {(T.A_pnl/T.R).mean():+.3f}R (t {t(T.A_pnl/T.R):.2f}, n{len(T)}), vs always-long {(T.A_pnl-T.A_bench).mean():+.1f} pt (t {t(T.A_pnl-T.A_bench):.2f})"
          f" | other days {(Rr.A_pnl/Rr.R).mean():+.3f}R")
    for s_, nm in [(1, 'long'), (-1, 'short')]:
        S = T[T.A_side == s_]
        print(f"      flagged {nm:5s} n{len(S):3d} {(S.A_pnl/S.R).mean():+.3f}R (t {t(S.A_pnl/S.R):.2f})")
