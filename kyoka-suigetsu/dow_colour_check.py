"""How often does each weekday's last-20 median range read 'wide' (>=1.05x the last-100-day median) or 'narrow' (<=0.95x),
with true weekday labels vs labels shuffled within each week (the null: weekday carries no information)."""
import pandas as pd, numpy as np
F = pd.read_pickle('/home/claude/byk/dow_F.pkl').sort_values('tday').reset_index(drop=True)
rng = np.random.default_rng(3)
def shares(dow, N=20, thr=(1.05, 0.95)):
    r = F.rng.values; out = np.zeros((5, 3)); cnt = 0
    for t in range(150, len(F), 5):
        past = slice(0, t); allm = np.median(r[max(0, t - 5 * N):t])
        for k in range(5):
            idx = np.where(dow[:t] == k)[0][-N:]
            m = np.median(r[idx]) / allm
            out[k] += [m >= thr[0], m <= thr[1], 1]
    return out[:, 0] / out[:, 2] * 100, out[:, 1] / out[:, 2] * 100
w, n = shares(F.dow.values)
print('true labels   wide% ', np.round(w, 0), ' narrow%', np.round(n, 0))
W = []; Nn = []
F['wk'] = F.tday.dt.to_period('W-SUN')
for s in range(40):
    d = F.dow.values.copy()
    for _, g in F.groupby('wk').groups.items():
        g = np.array(list(g)); d[g] = rng.permutation(d[g])
    a, b = shares(d); W.append(a); Nn.append(b)
print('shuffled null wide% ', np.round(np.mean(W, 0), 0), ' narrow%', np.round(np.mean(Nn, 0), 0))
print('null 95th pct wide%', np.round(np.percentile(W, 95, 0), 0))
