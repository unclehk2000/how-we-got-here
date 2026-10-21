"""Qualifier for the indicator: 5-day overnight ATR known at 02:30.
Overnight = 18:00 -> 02:29 ET. True range = max(ON high, prior 16:59 close) - min(ON low, prior 16:59 close), as % of price.
ATR5 = average of the last 5 overnights INCLUDING today's (complete at 02:30). Also the plain-range version for comparison.
Threshold pre-set as the top third of the 2018-24 distribution; checked on 2025-26."""
import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
F = pd.read_pickle('/home/claude/byk/de_D.pkl')[['tday', 'A_side', 'A_pnl', 'A_bench', 'R']].set_index('tday')
rows = []; prevC = np.nan
for d, x in b.groupby('tday'):
    on = x[(x.hm >= 1800) | (x.hm <= 229)]; lor = x[(x.hm >= 200) & (x.hm <= 229)]; c5 = x[x.hm == 459]; last = x[x.hm == 1659]
    if len(on) > 300 and len(lor) >= 28 and len(c5) == 1:
        P = lor.Close.iloc[-1]; H, L = lor.High.max(), lor.Low.min(); C5 = c5.Close.iloc[0]
        hi, lo = on.High.max(), on.Low.min()
        tr = (max(hi, prevC) - min(lo, prevC)) if not np.isnan(prevC) else np.nan
        rows.append(dict(tday=d, year=d.year, P=P, rng=100 * (hi - lo) / P, tr=100 * tr / P, pts=tr,
                         exp=(C5 >= H * 1.003) or (C5 <= L * 0.997)))
    prevC = last.Close.iloc[0] if len(last) else np.nan
Q = pd.DataFrame(rows).sort_values('tday').reset_index(drop=True)
Q['atr5'] = Q.tr.rolling(5).mean(); Q['rng5'] = Q.rng.rolling(5).mean(); Q['atr5pts'] = Q.pts.rolling(5).mean()
Q = Q.dropna(subset=['atr5']).join(F, on='tday'); Q['sp'] = np.where(Q.year >= 2025, 'test', 'train')
Tr, Te = Q[Q.sp == 'train'], Q[Q.sp == 'test']
print('ATR5 (% of price) distribution, train:', Tr.atr5.quantile([.1, .25, .5, .67, .75, .9]).round(3).to_dict())
print('ATR5 (% of price) distribution, test :', Te.atr5.quantile([.1, .25, .5, .67, .75, .9]).round(3).to_dict())
print('ATR5 in points, test median', round(Te.atr5pts.median(), 1))
bins = [0, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.25, 9]
for nm, Z in [('train', Tr), ('test', Te)]:
    g = Z.groupby(pd.cut(Z.atr5, bins), observed=True).exp.agg(['mean', 'size']); g['mean'] *= 100
    print(f'\n{nm}: expansion-day rate by ATR5 bucket (% of price)'); print(g.round(1).to_string())
def t(v): v = pd.Series(v).dropna(); return v.mean() / (v.std(ddof=1) / np.sqrt(len(v)))
for col in ['atr5', 'rng5']:
    cut = Tr[col].quantile(2/3)
    print(f"\n{col}: threshold (train top third) = {cut:.3f}%")
    for nm, Z in [('train', Tr), ('test', Te)]:
        q = Z[Z[col] >= cut]; r = Z[Z[col] < cut]; T_ = q[q.A_side.notna()]
        print(f"  {nm}: qualifies on {100*len(q)/len(Z):.0f}% of days | expansion days {100*q.exp.mean():.1f}% vs {100*r.exp.mean():.1f}% "
              f"(base {100*Z.exp.mean():.1f}%) | break trade on qualifying days {(T_.A_pnl/T_.R).mean():+.3f}R (t {t(T_.A_pnl/T_.R):.2f}, n{len(T_)})")

print('\nTiers used as indicator defaults (true-range ATR5): below 0.70% / 0.70-1.00% / 1.00%+')
for nm, Z in [('train', Tr), ('test', Te)]:
    k = np.digitize(Z.atr5, [0.70, 1.00])
    s = [f"{['not', 'qualifies', 'strong'][i]}: {100*(k==i).mean():.0f}% of days, expansion {100*Z.exp[k==i].mean():.1f}%" for i in range(3)]
    print(f"  {nm}: " + ' | '.join(s))

print('\nSingle threshold 1.00% (indicator default)')
for nm, Z in [('train', Tr), ('test', Te)]:
    q = Z[Z.atr5 >= 1.0]; r = Z[Z.atr5 < 1.0]; T_ = q[q.A_side.notna()]
    print(f"  {nm}: qualifies {100*len(q)/len(Z):.0f}% of days | expansion {100*q.exp.mean():.1f}% vs {100*r.exp.mean():.1f}% | "
          f"break trade {(T_.A_pnl/T_.R).mean():+.3f}R (t {t(T_.A_pnl/T_.R):.2f}, n{len(T_)}) | vs always-long {(T_.A_pnl-T_.A_bench).mean():+.1f} pt")
