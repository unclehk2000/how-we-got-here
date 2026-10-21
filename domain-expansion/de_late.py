"""Can an expansion day be recognised later in London and still pay? Pre-specified main rule:
at the 03:30 close (after the 08:00 UK expansion), if price is >= 0.15% beyond the 02:00-02:29 range, enter that way,
stop = back inside the range (the broken boundary), exit at the 04:59 close. 1 pt cost. Small grid shown for context only."""
import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
def t(v): v = pd.Series(v).dropna(); return v.mean() / (v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 2 else np.nan
rows = []
for d, x in b.groupby('tday'):
    lor = x[(x.hm >= 200) & (x.hm <= 229)]; post = x[(x.hm >= 230) & (x.hm <= 459)]
    if len(lor) < 28 or len(post) < 140 or post.hm.iloc[-1] != 459: continue
    H, L = lor.High.max(), lor.Low.min(); C5 = post.Close.iloc[-1]
    exp = (C5 >= H * 1.003) or (C5 <= L * 0.997)
    hm, h, l, c = post.hm.values, post.High.values, post.Low.values, post.Close.values
    for T in [300, 330, 400]:
        k_i = np.where(hm == T - 1 if T % 100 else hm == T - 41)[0]  # bar before T: 02:59 / 03:29 / 03:59
        if len(k_i) == 0: continue
        i = k_i[0]; e = c[i]
        for k in [0.10, 0.15, 0.20]:
            side = 1 if e >= H * (1 + k / 100) else (-1 if e <= L * (1 - k / 100) else 0)
            if side == 0: continue
            stop = H if side > 0 else L; pnl = None
            for j in range(i + 1, len(c)):
                if (l[j] <= stop) if side > 0 else (h[j] >= stop):
                    pnl = side * (stop - e); break
            if pnl is None: pnl = side * (C5 - e)
            rows.append(dict(year=d.year, T=T, k=k, side=side, pnl=pnl - 1, risk=abs(e - stop), bench=C5 - e, exp=exp,
                             exp_right=exp and ((C5 > H) == (side > 0))))
Q = pd.DataFrame(rows); Q['sp'] = np.where(Q.year >= 2025, 'test', 'train'); Q['r'] = Q.pnl / Q.risk
g = Q.groupby(['T', 'k', 'sp']).apply(lambda z: pd.Series(dict(n=len(z), exp_right=100*z.exp_right.mean(), avg_pt=z.pnl.mean(),
        R=z.r.mean(), tR=t(z.r), vs_long=(z.pnl - z.bench).mean(), t_vs=t(z.pnl - z.bench),
        long_R=z[z.side > 0].r.mean(), short_R=z[z.side < 0].r.mean())), include_groups=False)
pd.set_option('display.width', 200)
print(g.round(3).to_string())
