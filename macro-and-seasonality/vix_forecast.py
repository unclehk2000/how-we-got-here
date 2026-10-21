"""Compact VIX range forecast that Pine can compute live: log(range ÷ ADR20) = a + b·ivrv + c·vspike (+ event dummies).
ivrv = ln(VIX prior close / √252) − ln(ADR20 in %), vspike = ln(VIX prior close / its 20-day mean). Fit 2018–24, score 2025–26."""
import pandas as pd, numpy as np, json
from scipy import stats
EV = ['FOMC', 'NFP', 'CPI', 'POST', 'PRE', 'HOLLOW']
OUT = {}
for root in ('NQ', 'ES'):
    T = pd.read_pickle(f'macro_{root}.pkl'); T = T[(T.R > 0)].dropna(subset=['ivrv', 'vspike']).copy()
    tr = T.year <= 2024; te = T.year >= 2025
    def run(cols):
        X = np.column_stack([np.ones(len(T))] + [T[c].values if c in T else (T.type == c).astype(float).values for c in cols])
        beta, *_ = np.linalg.lstsq(X[tr.values], T.lR.values[tr.values], rcond=None)
        pred = X @ beta; y = T.lR.values
        r2 = 1 - ((y[te.values] - pred[te.values]) ** 2).sum() / ((y[te.values] - y[tr.values].mean()) ** 2).sum()
        res = y[tr.values] - pred[tr.values]
        return beta, pred, r2, res
    for cols in (['ivrv', 'vspike'], ['ivrv', 'vspike'] + EV):
        beta, pred, r2, res = run(cols)
        q10, q90 = np.quantile(res, [.1, .9])
        f = np.exp(pred); real = T.R.values
        inside = ((np.log(real) >= pred + q10) & (np.log(real) <= pred + q90))
        ratio = real / f
        print(f'{root} {"+".join(cols[:2])}{" + events" if len(cols) > 2 else ""}: OOS R² {r2:.3f} · coef ' + ' '.join(f'{c}={b:+.3f}' for c, b in zip(['a'] + cols, beta)))
        print(f'    residual P10/P90 ×{np.exp(q10):.2f} / ×{np.exp(q90):.2f} · 2025–26 realised ÷ forecast median {np.median(ratio[te.values]):.2f} · inside P10–P90 {inside[te.values].mean() * 100:.0f}% (train {inside[tr.values].mean() * 100:.0f}%)')
        fc = pd.Series(f, index=T.index)
        for nm, m in (('2018–24', tr), ('2025–26', te)):
            g = T[m].copy(); g['f'] = fc[m]
            q = pd.qcut(g.f, 3, labels=['low', 'mid', 'high'])
            print(f'    {nm}: forecast tercile → realised median ÷ ADR20 ' + ' / '.join(f'{g[q == k].R.median():.2f}' for k in ('low', 'mid', 'high')) + f' · forecast medians ' + ' / '.join(f'{g[q == k].f.median():.2f}' for k in ('low', 'mid', 'high')))
        OUT[f'{root}_{len(cols)}'] = dict(cols=cols, beta=list(beta), r2=r2, q10=float(np.exp(q10)), q90=float(np.exp(q90)), cover_te=float(inside[te.values].mean()), ratio_te=float(np.median(ratio[te.values])))
    # what a trader sees: VIX spike states in plain words
    for nm, m in (('2018–24', tr), ('2025–26', te)):
        g = T[m]; s = g.vspike
        rows = [('VIX ≥ 10% above its 20-day mean', s >= np.log(1.10)), ('within ±10%', (s > np.log(0.90)) & (s < np.log(1.10))), ('≥ 10% below', s <= np.log(0.90))]
        print(f'    {nm} ' + ' · '.join(f'{lab}: {g[c].R.median():.2f}× ADR (n{c.sum()}, ran above ADR {(g[c].R > 1).mean() * 100:.0f}%)' for lab, c in rows))
json.dump(OUT, open('vix_forecast.json', 'w'), indent=1, default=float)
